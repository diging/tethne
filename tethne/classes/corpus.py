"""
A :class:`.Corpus` organizes :class:`.Paper`\s for analysis.
"""

from collections import Counter
import hashlib

from tethne.classes.feature import FeatureSet, Feature
from tethne.utilities import _iterable, argsort


def _tfidf(f, c, C, DC, N):
    tf = float(c)
    idf = np.log(float(N)/float(DC))
    return tf*idf


def _filter(s, C, DC):
    if C > 3 and DC > 1 and len(s) > 3:
        return True
    return False


class Corpus(object):
    """
    Represents a collection of :class:`.Paper` instances.
    
    The easiest way to get a :class:`.Corpus` is by using a method from
    :mod:`tethne.readers`\. For example:
    
    .. code-block:: python
    
       >>> from tethne.readers.wos import read
       >>> read('/path/to/data')
       <tethne.classes.corpus.Corpus object at 0x10278ea10>
       
    If you're building a corpus yourself, you can pass a list of 
    :class:`.Paper`\s to the constructor.
    
    .. code-block:: python
    
       >>> papers = however_you_generate_papers()   # <- list of Papers.
       >>> corpus = Corpus(papers)

    The :class:`.Corpus` will attempt to decide which field in the 
    :class:`.Paper`\s should be used for indexing. **Caution**: if you are
    building a corpus using bibliographic data from multiple sources, you
    should probably specificy the indexing field manually. It is important
    that all of the :class:`.Paper`\s in your corpus have a unique value for
    that field. For example:
    
    .. code-block:: python
    
       >>> corpus = Corpus(papers, index_by='doi')
       >>> corpus.indexed_papers.keys()
       ['doi/123', 'doi/456', ..., 'doi/789']
       
    By default, :class:`.Corpus` will index the ``authors`` and ``citations``
    fields. To control which fields are indexed, pass the ``index_fields``
    argument, or call :meth:`.Corpus.index`\.
    
    .. code-block:: python
    
       >>> corpus = Corpus(papers, index_fields=['authors', 'date'])
       >>> corpus.indices.keys()
       ['authors', 'date']
       
    Similarly, :class:`.Corpus` will index features. By default, ``authors`` 
    and ``citations`` will be indexed as features (i.e. available for
    network-building methods). To control which fields are indexed as features,
    pass the ``index_features`` argument, or call 
    :meth:`.Corpus.index_features`\.
    
    .. code-block:: python
    
       >>> corpus = Corpus(papers, index_features=['unigrams'])
       >>> corpus.features.keys()
       ['unigrams']
       
    There are a variety of ways to select :class:`.Paper`\s from the corpus.
    
    .. code-block:: python
    
       >>> corpus = Corpus(papers)
       >>> corpus[0]    # Integer indices yield a single Paper.
       <tethne.classes.paper.Paper object at 0x103037c10>

       >>> corpus[range(0,5)]  # A list of indices will yield a list of Papers.
       [<tethne.classes.paper.Paper object at 0x103037c10>, 
        <tethne.classes.paper.Paper object at 0x10301c890>, 
        ...
        <tethne.classes.paper.Paper object at 0x10302f5d0>]

       >>> corpus[('date', 1995)]  # You can select based on indexed fields.
       [<tethne.classes.paper.Paper object at 0x103037c10>, 
        <tethne.classes.paper.Paper object at 0x10301c890>, 
        ...
        <tethne.classes.paper.Paper object at 0x10302f5d0>]
       
       >>> corpus[('date', range(1993, 1995))]
       [<tethne.classes.paper.Paper object at 0x103037c10>, 
        <tethne.classes.paper.Paper object at 0x10301c890>, 
        ...
        <tethne.classes.paper.Paper object at 0x10302f5d0>]
        
    If you prefer to retrieve a :class:`.Corpus` rather than simply a list of
    :class:`.Paper` instances (e.g. to build networks), use
    :meth:`.Corpus.subcorpus`\. ``subcorpus`` accepts selector arguments
    just like :meth:`.Corpus.__getitem__`\.
    
    .. code-block:: python
    
       >>> corpus = Corpus(papers)
       >>> subcorpus = corpus.subcorpus(('date', 1995))
       >>> subcorpus
       <tethne.classes.corpus.Corpus object at 0x10278ea10>

    """
    @property
    def papers(self):
        return self.indexed_papers.values()

    def __init__(self, papers=None, index_by=None,
                 index_fields=['authors', 'citations'],
                 index_features=['authors', 'citations'], **kwargs):
        """
        Parameters
        ----------
        paper : list
        index_by : str
        index_fields : str or iterable of strs
        """

        self.index_by = index_by
        self.indices = {}
        self.features = {}
        self.slices = []

        self.indexed_papers = {self._generate_index(paper): paper for paper in papers}

        if index_features:
            for feature_name in index_features:
                self.index_feature(feature_name)

        if index_fields:
            for attr in _iterable(index_fields):
                self.index(attr)


    def __len__(self):
        return len(self.indexed_papers)
        
    def _generate_index(self, paper):
        """
        If the ``index_by`` field is not set or not available, generate a unique
        identifier using the :class:`.Paper`\'s title and author names.
        """

        if self.index_by is None or not hasattr(paper, self.index_by):
            authors = zip(*paper.authors)[0]
            m = hashlib.md5()            
            hashable = ' '.join(list([paper.title] + [l + f for l, f in authors]))
            m.update(hashable)
            return m.hexdigest()
        return getattr(paper, self.index_by)    # Identifier is available.

    def index_feature(self, feature_name):
        """
        Create a new :class:`.Feature` from the attribute ``feature_name``
        in each :class:`.Paper`\.
        """
        feats = {self._generate_index(p): Feature(getattr(p, feature_name))
                 for p in self.papers if hasattr(p, feature_name)}
        self.features[feature_name] = FeatureSet(feats)

    def index(self, attr):
        """
        Index ``papers`` by ``attr``
        """

        self.indices[attr] = {}
        for i, paper in self.indexed_papers.iteritems():
            if hasattr(paper, attr):
                value = getattr(paper, attr)
                for v in _iterable(value):
                    if type(value) is Feature:
                        v_ = v[:-1]
                    else:
                        v_ = v

                    if hasattr(v_, '__iter__'):
                        if len(v_) == 1:
                            t = type(v_[0])
                            v_ = t(v_[0])

                    if v_ not in self.indices[attr]:
                        self.indices[attr][v_] = []
                    self.indices[attr][v_].append(i)

    
    def __getitem__(self, selector):
        if type(selector) is tuple: # Select papers by index.
            index, value = selector
            if type(value) is list:  # Set of index values.
                papers = [p for v in value for p in self[index, v]]
            else:
                papers = [self.indexed_papers[p] for p in self.indices[index][value]] # Single index value.
        elif type(selector) is list:
            if selector[0] in self.indexed_papers:
                # Selector is a list of primary indices.
                papers = [self.indexed_papers[s] for s in selector]
            elif type(selector[0]) is int:
                papers = [self.papers[i] for i in selector]
        elif type(selector) is int:
            papers = self.papers[selector]
        return papers

    def __getattr__(self, key):
        if hasattr(self, key):
            return getattr(self, key)
        elif key in self.indices:
            return self.indices[key]
        raise AttributeError("Corpus has no such attribute")

    def slice(self, window_size=1, step_size=1):
        """
        Returns a generator that yields key, subcorpus tuples for sequential
        time windows.
        
        Example
        -------
        .. code-block:: python
        
           >>> from tethne.readers.wos import read
           >>> corpus = read('/path/to/data')
           >>> for key, subcorpus in corpus.slice():
           ...     print key, len(subcorpus)
           2005, 5
           2006, 5
        
        Parameters
        ----------
        window_size : int
            (default: 1) Size of the time window, in years.
        step_size : int
            (default: 1) Number of years to advance window at each step.

        Returns
        -------
        generator
        """


        if 'date' not in self.indices:
            self.index('date')
        
        start = min(self.indices['date'].keys())
        end = max(self.indices['date'].keys())
        while start <= end - (window_size - 1):
            selector = ('date', range(start, start + window_size, 1))
            yield start, self.subcorpus(selector)
            start += step_size
            
    def distribution(self, **slice_kwargs):
        """
        Returns the number of papers in each slice, as defined by
        ``slice_kwargs``.
        
        Example
        -------
        .. code-block:: python
        
           >>> corpus.distribution()
           [5, 5]

        Parameters
        ----------
        slice_kwargs : kwargs
            Keyword arguments to be passed to :method:`.Corpus.slice`\.
        
        Returns
        -------
        list
        """
        return [len(papers[1]) for papers in self.slice(**slice_kwargs)]

    def feature_distribution(self, featureset_name, feature, mode='counts',
                             **slice_kwargs):
            
        values = []
        keys = []

        for key, subcorpus in self.slice(**slice_kwargs):
            values.append(subcorpus.features[featureset_name].count(feature))
            keys.append(key)
        return keys, values

    def top_features(self, featureset_name, topn=20, by='counts',
                     perslice=False, slice_kwargs={}):
        if perslice:
            return [(k, subcorpus.features[featureset_name].top(topn, by=by))
                    for k, subcorpus in self.slice(**slice_kwargs)]
        return self.features[featureset_name].top(topn, by=by)

    def subcorpus(self, selector):
        """
        Generate a new :class:`.Corpus` using the criteria in ``selector``.
        
        .. code-block:: python
        
           >>> c.subcorpus(('date', 1950))
           
           >>> c.subcorpus(('date', range(1920, 1940)))
           
           >>> c.subcorpus(['doi/123', 'doi/456'])
        """

        subcorpus = Corpus(self[selector], index_by=self.index_by,
                           index_fields=self.indices.keys(),
                           index_features=self.features.keys())

        # Transfer FeatureSets.
        for featureset_name, featureset in self.features.iteritems():
            if featureset_name not in subcorpus:
                new_featureset = FeatureSet()
                for k, f in featureset.items():
                    if k in subcorpus.indexed_papers:
                        new_featureset.add(k, f)
                subcorpus.features[featureset_name] = new_featureset

        return subcorpus

