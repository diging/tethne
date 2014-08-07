"""
A :class:`.Corpus` organizes :class:`.Paper`\s for analysis.
"""

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib
from paper import Paper
from collections import Counter
from nltk.corpus import stopwords
import scipy

import copy

from unidecode import unidecode

from ..utilities import strip_punctuation

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
    A :class:`.Corpus` organizes :class:`.Paper`\s for analysis.

    You can instantiate a :class:`.Corpus` directly by providing a list of
    :class:`.Paper` instances, and (optionally) some features over those papers,
    e.g. wordcounts. Once you have created a :class:`.Corpus` you can use it
    to generate a :class:`.GraphCollection`\, or generate corpus or social
    models (see the :mod:`.model` module).

    You can create new :class:`.Corpus` objects from bibliographic datasets
    using the methods in :mod:`.readers`\. For more information about what you
    can do with a :class:`.Corpus`\, see :ref:`working-with-corpora`\.
    
    .. autosummary::
       :nosignatures:

       N_axes
       abstract_to_features
       add_features
       all_papers
       distribution
       feature_counts
       feature_distribution
       filter_features
       get_axes
       get_slice
       get_slices
       index
       indices
       plot_distribution
       slice
       transform

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    features : dict
        Contains dictionary `{ type: { i: [ (f, w) ] } }` where `i` is an
        index for papers (see kwarg `index_by`), `f` is a feature (e.g. an
        N-gram), and `w` is a weight on that feature (e.g. a count).
    index_by : str
        A key in :class:`.Paper` for indexing. If `features` is provided,
        then this must by the field from which indices `i` are drawn. For
        example, if a dictionary in `features` describes DfR wordcounts for
        the :class:`.Paper`\s in `data`, and is indexed by DOI, then
        `index_by` should be 'doi'.
    index_citation_by : str
        Just as ``index_by``, except for citations.
    exclude : set
        (optional) Features to ignore, e.g. stopwords.
    filt : function
        Takes a lambda function that returns True if a feature should be
        included.
    index : bool
        (default: True) Set to False to supress indexing.

    Returns
    -------
    :class:`.Corpus`

    Examples
    --------

    These examples deal with instantiating a :class:`.Corpus` using its
    constructor. To read about loading a :class:`.Corpus` directly from data,
    see :ref:`working-with-corpora`\.

    To create a :class:`.Corpus` from a JSTOR DfR dataset containing wordcounts,
    you might do:

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> papers = dfr.read('/path/to/dataset')
       >>> wordcounts = dfr.ngrams('/path/to/dataset', N='uni')

       >>> from tethne import Corpus
       >>> MyCorpus = Corpus(papers, features={'wc':wordcounts}, index_by='doi')
       >>> MyCorpus
       <tethne.classes.corpus.Corpus object at 0x107975ad0>

    :mod:`.readers.dfr` and :mod:`.readers.wos` provide some convenience
    functions for generating a :class:`.Corpus` directly from a dataset. For
    example:

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> MyCorpus = dfr.read_corpus('/path/to/dataset', features=('uni',))
       >>> MyCorpus
       <tethne.classes.corpus.Corpus object at 0x107975ad0>

    You can organize your :class:`.Corpus` using the :meth:`.slice` method, and
    generate some descriptive statistics with :meth:`.distribution` and
    :meth:`.plot_distribution`\.

    To save/load your :class:`.Corpus` (e.g. for archiving your data), you can
    convert it to or from a :class:`.HDF5Corpus` using :func:`.hdf5.to_hdf5` and
    :func:`.hdf5.from_hdf5`\.

    """

    def __init__(self, papers, features=None, index_by='ayjid',
                       index_citation_by='ayjid', exclude=set([]),
                       filt=None, index=True):

        self.papers = {}             # { p : paper }, where p is index_by
        self.features = {}
        self.authors = {}
        self.citations = {}          # { c : citation }
        self.papers_citing = {}      # { c : [ p ] }

        self.axes = {}
        self.index_by = index_by    # Field in Paper, e.g. 'wosid', 'doi'.
        self.index_citation_by = index_citation_by

        if index:
            self.index( papers, features, index_by=index_by,
                        index_citation_by=index_citation_by,
                        exclude=exclude, filt=filt  )

    def index(  self,   papers, features=None, index_by='ayjid',
                        index_citation_by='ayjid', exclude=set([]),
                        filt=None, stem=False   ):
        """
        Indexes `papers`, `features`, and `citations` (if present).
        This should be called automatically from :func:`.__init__`, unless
        explicitly supressed.

        Parameters
        ----------
        papers : list
            A list of :class:`.Paper` instances.
        features : dict
            Contains dictionary `{ type: { i: [ (f, w) ] } }` where `i` is an
            index for papers (see kwarg `index_by`), `f` is a feature (e.g. an
            N-gram), and `w` is a weight on that feature (e.g. a count).
        index_by : str
            (default: 'ayjid')
            A key in :class:`.Paper` for indexing. If `features` is provided,
            then this must by the field from which indices `i` are drawn. For
            example, if a dictionary in `features` describes DfR wordcounts for
            the :class:`.Paper`\s in `data`, and is indexed by DOI, then
            `index_by` should be 'doi'.
        index_citation_by : str
            (default: 'ayjid') Similar to ``index_by``, but for citations.
        exclude : set
            (optional) Features to ignore, e.g. stopwords.
        filt : function
            Takes a lambda function that returns True if a feature should be
            included.
        """

        # Check if index_by is a valid key.
        self.datakeys = papers[0].keys()
        if index_by not in self.datakeys:
            raise(KeyError(str(index_by) + " not a valid key in data."))

        # Tokenize and index citations (both directions).
        self._index_citations(papers)

        # Index the Papers in data.
        for paper in papers:
            self.papers[paper[index_by]] = paper
        self.N_p = len(self.papers)

        # Index the Papers by author.
        self._index_papers_by_author()

        # Tokenize and index features.
        if features is not None:
            for ftype, fdict in features.iteritems():   # e.g. unigrams, bigrams

                # Stem only for unigrams, when requested.
                if stem and ftype == 'unigrams':    # Use stemming?
                    from nltk.stem.porter import PorterStemmer
                    stemmer = PorterStemmer()
                    transformer = stemmer.stem
                else:
                    transformer = None

                tokd = self._tokenize_features( ftype, fdict, exclude, filt,
                                                transformer=transformer )
                ft, fi, fs, c, dC, fp = tokd
                self._define_features(ft, fi, fs, c, dC, fp)
        else:
            logger.debug('features is None, skipping tokenization.')
            pass

    def add_features(self, name, features, exclude=[], filt=None):
        """
        Add a new featureset to the :class:`.Corpus`\.

        Parameters
        ----------
        name : str
        features : dict
            Keys should be :class:`.Paper` identifiers
            (:prop:`.Corpus.index_by`), and values should be distributions
            over features in sparse-tuple formats.
        exclude : set
            (optional) Features to ignore, e.g. stopwords.
        filt : function
            Takes a lambda function that returns True if a feature should be
            included.

        Returns
        -------
        None

        Examples
        --------

        .. code-block:: python

           >>> from tethne.readers import dfr
           >>> bigrams = dfr.ngrams('/path/to/dataset', N='bi')
           >>> MyCorpus.add_features('bigrams', bigrams)

        """

        tokd = self._tokenize_features(name, features, exclude, filt)
        ft, fi, fs, c, dC, fp = tokd
        self._define_features(ft, fi, fs, c, dC, fp)
        return

    def _define_features(   self, name, index, features,
                            counts, documentCounts, fpapers ):
        """
        Update :prop:`.features` with a tokenized featureset.
        """
        logger.debug('define features with name {0}'.format(name))
        self.features[name] = {
            'index': index,         # { int(f_i) : str(f) }
            'features': features,   # { str(p) : [ ( f_i, c) ] }
            'counts': counts,       # { int(f_i) : int(C) }
            'documentCounts': documentCounts,   # { int(f_i) : int(C) }
            'papers': fpapers       # { int(f_i) : [ (str(p), c ] }
            }

    def _index_papers_by_author(self):
        """
        Generates dict `{ author : [ p ] }` where `p` is an index of a
        :class:`.Paper` .
        """

        logger.debug('indexing authors in {0} papers'.format(self.N_p))

        author_dict = {}

        for k,p in self.papers.iteritems():
            for author in p.authors():
                if author in author_dict:
                    author_dict[author].append(k)
                else:
                    author_dict[author] = [k]

        self.N_a = len(author_dict)
        for k,v in author_dict.iteritems():
            self.authors[k] = v
        logger.debug('indexed {0} authors'.format(self.N_a))

    def _index_citations(self, papers):
        """
        Generates dict `{ c : citation }` and `{ c : [ p ] }`.
        """

        logger.debug('indexing citations in {0} papers'.format(len(papers)))

        cited = {}  # { p : [ (c,1) ] }
        citation_counts = Counter()
        citation_index = {}
        citation_index_ = {}

        citations = {}

        fpapers = {}

        papers_citing = {}

        for paper in papers:
            p = paper[self.index_by]
            if paper['citations'] is not None:
                cited[p] = []

                for citation in paper['citations']:
                    c = citation[self.index_citation_by]
                    try:
                        c_i = citation_index_[c]
                    except KeyError:
                        c_i = len(citation_index)
                        citation_index[c_i] = c
                        citation_index_[c] = c_i

                    cited[p].append((c_i,1))
                    citation_counts[c_i] += 1

                    if c not in citations:
                        citations[c] = citation

                    if c not in papers_citing:
                        fpapers[c_i] = [ (p, 1) ]
                        papers_citing[c] = [ p ]
                    else:
                        fpapers[c_i].append( (p, 1) )
                        papers_citing[c].append(p)

        # Separating this part allows for more flexibility in what sits behind
        #  self.papers_citing (e.g. HDF5 VArray).
        for k,v in papers_citing.iteritems():
            self.papers_citing[k] = v

        for k,v in citations.iteritems():
            self.citations[k] = v

        self._define_features('citations', citation_index, cited,
                                citation_counts, citation_counts, fpapers)

        self.N_c = len(self.citations)
        logger.debug('indexed {0} citations'.format(self.N_c))

    def _tokenize_features( self, ftype, fdict, exclude=set([]),
                            filt=None, transformer=None ):
        """

        Parameters
        ----------
        ftype : str
            Name of featureset.
        fdict : dict
            Contains dictionary `{ i: [ (f, w) ] }` where `i` is an
            index for papers (see kwarg `index_by`), `f` is a feature (e.g. an
            N-gram), and `w` is a weight on that feature (e.g. a count).
        exclude : set
            (optional) Features to ignore, e.g. stopwords.
        filt : function
            Takes a lambda function that returns True if a feature should be
            included.

        Returns
        -------
        ftype : str
            Name of the featureset.
        findex : dict
            Maps integer IDs onto features (e.g. words).
        features : dict
            Keys are identifiers for :class:`.Paper` instances in the
            :class:`.Corpus`\, and values are sparse feature vectors.
            e.g. [ (f1,v1), (f3,v3) ]
        counts : dict
            Overall frequency of each feature in the :class:`.Corpus`
        documentCounts : dict
            Number of documents containing each feature in the :class:`.Corpus`
        """

        if filt is None:
            filt = lambda s: True

        if exclude is None:
            exclude = set([])
        if type(exclude) is not set:
            exclude = set(exclude)

        def _handle(tok,w):
            if tok in findex_:
                counts[findex_[tok]] += w
                return True
            return False

        def _transform(string):
            if transformer is None:
                return string
            return transformer(string)

        logger.debug('tokenizing features of type {0}'.format(ftype))

        features = {}
        index = {}
        counts = Counter()
        documentCounts = Counter()

        # List of unique tokens.
        ftokenset = set([ unidecode(unicode(f)) for k,fval in fdict.items()
                                                for f,v in fval])
        ftokens = list(set([ _transform(s) for s in list(ftokenset - exclude) if filt(s) ]))
        logger.debug('found {0} unique tokens'.format(len(ftokens)))

        # Create forward and reverse indices.
        findex = { i:ftokens[i] for i in xrange(len(ftokens)) }
        findex_ = { v:k for k,v in findex.iteritems() }     # lookup.
        logger.debug('created forward and reverse indices.')

        # Holds a list of (document, count) tuples for each feature.
        fpapers = {}

        # Tokenize.
        for key, fval in fdict.iteritems(): # fval is a list of tuples.
            if type(fval) is not list or type(fval[0]) is not tuple:
                raise ValueError('Malformed features data.')

            tokenized = []
            for f,w in fval:
                if _handle(f,w):
                    tokenized.append( ( findex_[f], w ) )
                    try:
                        fpapers[findex_[f]].append( ( key, w ) )
                    except KeyError:
                        fpapers[findex_[f]] = [ ( key, w ) ]

            features[key] = tokenized
            for t,w in tokenized:
                documentCounts[t] += 1

        logger.debug('done tokenizing features')
        return ftype, findex, features, counts, documentCounts, fpapers

    def transform(self, fold, fnew, transformer=_tfidf):
        """
        Transform values in featureset ``fold``, creating a new featureset 
        ``fnew``.
        
        ``transformer`` is a method that will be applied to each feature in each
        document, returning a new value for that feature. It should accept the
        following parameters:
        
        =========   ============================================================
        Parameter   Description
        =========   ============================================================
        ``s``       Representation of the feature (e.g. string).
        ``c``       Value of the feature in the document (e.g. frequency).
        ``C``       Value of the feature in the :class:`.Corpus` (e.g. global
                    frequency).
        ``DC``      Number of documents in which the feature occcurs.
        ``N``       Total number of documents in the :class:`.Corpus`\.
        =========   ============================================================
        
        If ``transformer`` is not provided, the default behavior is a standard
        `tf*idf transformation <http://en.wikipedia.org/wiki/Tf%E2%80%93idf>`_.
        
        Parameters
        ----------
        fold : str
            Name of the featureset to be transformed.
        fnew : str  
            Name of the featureset to be created, with transformed values.
        transformer : method
            Applied to each feature in each document in the :class:`.Corpus`\.
            See above.
            
        Returns
        -------
        None
        
        """
        logger.debug('start transformation: "{0}" -> "{1}"'.format(fold, fnew))
        logger.debug('with transformer: {0}'.format(transformer.__name__))
        
        fdict = self.features[fold]

        features = {}
        index = fdict['index']
        counts = fdict['counts']
        documentCounts = fdict['documentCounts']    # Re-use this.
        fpapers = {}
        
        for d, fvect in fdict['features'].iteritems():
            fvect_ = []
            for f,v in fvect:
                v_ = transformer(
                    index[f], v, counts[f], documentCounts[f], len(self.papers))
                fvect_.append(  (f, v_) )
                try:
                    fpapers[f].append(  (d, v_) )
                except KeyError:
                    fpapers[f] = [ (d, v_), ]
            
            features[d] = fvect_

        self._define_features(fnew, index, features, counts, documentCounts, fpapers)

    def apply_stoplist(self, fold, fnew, stoplist):
        """
        Apply ``stoplist`` to the featureset ``fold``, resulting in featureset
        ``fnew``\.
        
        Parameters
        ----------
        fold : str
            Key into ``features`` for existing featureset.
        fnew : str
            Key into ``features`` for resulting featuresset.
        stoplist : list
            A list of features to remove from the featureset.
        
        Returns
        -------
        None
        
        Examples
        --------
        
        .. code-block:: python
        
           >>> from nltk.corpus import stopwords
           >>> MyCorpus.apply_stoplist('unigrams', 'u_stop', stopwords.words())
           
        """
    
        def filt(s, *args, **kwargs):
            if s in stoplist:
                return False
            return True
        
        return self.filter_features(fold, fnew, filt=filt)

    def filter_features(self, fold, fnew, filt=_filter):
        """
        Create a new featureset by applying a filter to an existing featureset.
        
        ``filt`` is a method applied to each feature in the :class:`.Corpus`\.
        It should return True if the feature is to be retained, and False if the
        feature is to be discarded. ``filt`` should accept the following
        parameters:
        
        =========   ============================================================
        Parameter   Description
        =========   ============================================================
        ``s``       Representation of the feature (e.g. a string).
        ``C``       The overall frequency of the feature in the
                    :class:`.Corpus`\.
        ``DC``      The number of documents in which the feature occurs.
        =========   ============================================================

        Parameters
        ----------
        fold : str
            Key into ``features`` for existing featureset.
        fnew : str
            Key into ``features`` for resulting featuresset.
        filt : method
            Filter function to apply to the featureset. See above.

        Returns
        -------
        None

        Examples
        --------

        .. code-block:: python

           >>> def filt(s, C, DC):
           ...     if C > 3 and DC > 1 and len(s) > 3:
           ...         return True
           ...     return False
           >>> MyCorpus.filter_features('wc', 'wc_filtered', filt)

        Assuming that the :class:`.Corpus` ``MyCorpus`` already has a
        feature called ``wc``, this would generate a new feature called
        ``wc_filtered`` containing only those features that...

        1. Occur more than three times overall in the :class:`.Corpus`\,
        2. Occur in more than one document, and
        3. Are at least four characters in length.

        """

        def _handle(tok,w): # Counts tokens, and excludes unwanted tokens.
            if tok in findex_:
                counts[findex_[tok]] += w
                return True
            return False

        logger.debug('Generating a new featureset {0} from {1}.'
                                                .format(fnew, fold))
        # index, features, counts, documentCounts

        fdict = self.features[fold]

        features = {}
        index = {}
        counts = Counter()
        documentCounts = Counter()

        ftokens = [ s for i,s in fdict['index'].iteritems()
                    if filt(s, fdict['counts'][i], fdict['documentCounts'][i] )]
        Ntokens = len(ftokens)

        logger.debug('found {0} unique tokens'.format(Ntokens))

        findex = { i:ftokens[i] for i in xrange(Ntokens) }
        findex_ = { v:k for k,v in findex.iteritems() }

        fpapers = { i:[] for i in findex.keys() }

        logger.debug('created forward and reverse indices.')

        feats = fdict['features']


        for key, fval in feats.iteritems():
            if type(fval) is not list or type(fval[0]) is not tuple:
                raise ValueError('Malformed features data.')

            tokenized = []

            for f,w in fval:
                if _handle(fdict['index'][f],w):
                    f_ = findex_[fdict['index'][f]]
                    tokenized.append( (f_,w) )
                    fpapers[f_].append( ( key, w ))

            features[key] = tokenized
            for f,w in tokenized:
                documentCounts[f] += 1

        self._define_features(fnew, findex, features, counts, documentCounts, fpapers)

        logger.debug('done indexing features')
        return

    def abstract_to_features(self, remove_stopwords=True, stem=True):
        """
        Generates a unigram (wordcount) featureset from the abstracts of all
        :class:`.Paper`\s in the :class:`.Corpus` (if available).

        Words are automatically tokenized, and stopwords are removed be default
        (see parameters).

        Parameters
        ----------
        remove_stopwords : bool
            (default: True) If True, passes tokenizer the NLTK stoplist.
        stem : bool
            (default: True) If True, passes tokenizer the NLTK Porter stemmer.

        Examples
        --------
        .. code-block:: python

           >>> MyCorpus.abstract_to_features()
           >>> 'abstractTerms' in MyCorpus.features
           True

        Notes
        -----

        **TODO:**

            * Should be able to pass one's own stemmer and stoplist, if desired.
              [`Issue #23 <https://github.com/diging/tethne/issues/23>`_]

        """
        logger.debug('abstract_to_features: start.')

        unigrams = {}
        for p,paper in self.papers.iteritems():
            if paper['abstract'] is not None:
                term_counts = Counter()
                terms = strip_punctuation(paper['abstract'].lower()).split()
                for term in terms: term_counts[term] += 1
                unigrams[p] = term_counts.items()

        logger.debug('abstract_to_features: generated features.')
        if remove_stopwords:    # Use stoplist?
            stoplist = set(stopwords.words())
        else:
            stoplist = set([])

        if stem:    # Use stemming?
            from nltk.stem.porter import PorterStemmer
            stemmer = PorterStemmer()
            transformer = stemmer.stem
        else:
            transformer = None

        tokd = self._tokenize_features( 'abstractTerms', unigrams,
                                        exclude=stoplist,
                                        transformer=transformer )
        ft, fi, fs, c, dC, fp = tokd
        self._define_features(ft, fi, fs, c, dC, fp)

        return unigrams

    def slice(self, key, method=None, **kwargs):
        """
        Slices data by key, using method (if applicable).

        In order to perform comparative analyses among your data, you must
        define the "axes" that you wish to compare by "slicing" your
        :class:`.Corpus`\. You can slice by (theoretically) any field in your
        :class:`.Paper`\s, but most of the time you'll be slicing by the `date`.

        Here are some methods for slicing a :class:`.Corpus`\, which you can
        specify using the `method` keyword argument.

        ===========    =============================    =======    =============
        Method         Description                      Key        kwargs
        ===========    =============================    =======    =============
        time_window    Slices data using a sliding      date       window_size
                       time-window. Dataslices are                 step_size
                       indexed by the start of the
                       time-window.
        time_period    Slices data into time periods    date       window_size
                       of equal length. Dataslices
                       are indexed by the start of
                       the time period.
        ===========    =============================    =======    =============

        The main difference between the sliding time-window (``time_window``)
        and the time-period (``time_period``) slicing methods are whether the
        resulting periods can overlap. Whereas time-period slicing divides data
        into subsets by sequential non-overlapping time periods, subsets
        generated by time-window slicing can overlap.

        .. figure:: _static/images/bibliocoupling/timeline.timeslice.png
           :width: 400
           :align: center

           **Time-period** slicing, with a window-size of 4 years.

        .. figure:: _static/images/bibliocoupling/timeline.timewindow.png
           :width: 400
           :align: center

           **Time-window** slicing, with a window-size of 4 years and a
           step-size of 1 year.

        Avilable kwargs:

        ===========    ======   ================================================
        Argument       Type     Description
        ===========    ======   ================================================
        window_size    int      Size of time-window or period, in years
                                (default = 1).
        step_size      int      Amount to advance time-window or period in each
                                step (ignored for time_period).
        cumulative     bool     If True, the data from each successive slice
                                includes the data from all preceding slices.
                                Only applies if key is 'date' (default = False).
        ===========    ======   ================================================

        If you slice your :class:`.Corpus` by a field other than `date`, you do
        not need to specifiy a `method` or any other keyword arguments.

        Once you have sliced your :class:`.Corpus`\, you can use
        :func:`.distribution` or :func:`.plot_distribution` to generate
        descriptive statistics about your data.

        Parameters
        ----------
        key : str
            key in :class:`.Paper` by which to slice data.
        method : str (optional)
            Dictates how data should be sliced. See table for available methods.
            If key is 'date', default method is time_period with window_size and
            step_size of 1.
        kwargs : kwargs
            See methods table, above.

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.slice('date', method='time_period', window_size=5)
           >>> MyCorpus.plot_distribution('date')

        Should generate a plot that looks something like this:

        .. figure:: _static/images/corpus_plot_distribution.png
           :width: 400
           :align: center

        """

        if key == 'date':
            if method == 'time_window':
                kw = {  'window_size': kwargs.get('window_size', 1),
                        'step_size': kwargs.get('step_size', 1) }
                self.axes[key] = self._time_slice(**kw)

            elif method == 'time_period' or method is None:
                kw = {  'window_size': kwargs.get('window_size', 1),
                        'step_size': kwargs.get('window_size', 1),
                        'cumulative': kwargs.get('cumulative', False) }

                self.axes[key] = self._time_slice(**kw)
            else:
                raise(ValueError(str(method) + " not a valid slicing method."))

        # TODO: consider removing this, and just focusing on time.
        elif key == 'author':   # Already indexed.
            self.axes[key] = self.authors     # { a : [ p ] }

        # TODO: consider indexing journals in __init__, perhaps optionally.
        elif key in self.datakeys: # e.g. 'jtitle'
            self.axes[key] = {}     # { jtitle : [ p ] }
            for p,paper in self.papers.iteritems():
                try:
                    self.axes[key][paper[key]].append(p)
                except KeyError:
                    self.axes[key][paper[key]] = [p]
        else:
            raise(KeyError(str(key) + " not a valid key in data."))

    def _time_slice(self, **kwargs):
        """
        Slices data by date.

        If step_size = 1, this is a sliding time-window. If step_size =
        window_size, this is a time period slice.

        Parameters
        ----------
        kwargs : kwargs
            See table, below.

        Returns
        -------
        slices : dict
            Keys are start date of time slice, values are :class:`.Paper`
            indices (controlled by index_by argument in
            :func:`.Corpus.__init__` )

        Notes
        -----

        Avilable kwargs:

        ===========    ======   ================================================
        Argument       Type     Description
        ===========    ======   ================================================
        window_size    int      Size of time-window or period, in years
                                (default = 1).
        step_size      int      Amount to advance time-window or period in each
                                step (ignored for time_period).
        cumulative     bool     If True, the data from each successive slice
                                includes the data from all preceding slices.
                                Only applies if key is 'date' (default = False).
        ===========    ======   ================================================

        """

        # Get parameters from kwargs.
        window_size = kwargs.get('window_size', 1)
        step_size = kwargs.get('step_size', 1)
        start = kwargs.get('start', min([ paper['date']
                                           for paper in self.papers.values() ]))
        end = kwargs.get('start', max([ paper['date']
                                           for paper in self.papers.values() ]))
        cumulative = kwargs.get('cumulative', False)

        slices = {}     # { s : [ p ] }
        last = None
        for s in xrange(start, end-window_size+2, step_size):
            slices[s] = [ p for p,paper in self.papers.iteritems()
                            if s <= paper['date'] < s + window_size ]
            if cumulative and last is not None:
                slices[s] += last
            last = slices[s]
        return slices

    def indices(self):
        """
        Yields a list of indices of all :class:`.Paper`\s in this
        :class:`.Corpus`\.

        Returns
        -------
        keys : list
            List of indices.

        Examples
        --------

        .. code-block:: python

           >>> indices = MyCorpus.indices()
           >>> indices[0]
           '10.2307/20037014'

        """
        keys = self.papers.keys()
        return keys

    def all_papers(self):
        """
        Yield the complete set of :class:`.Paper` instances in this
        :class:`.Corpus` .

        Returns
        -------
        papers : list
            A list of :class:`.Paper` instances.

        Examples
        --------

        .. code-block:: python

           >>> papers = MyCorpus.all_papers()
           >>> papers[0]
           <tethne.classes.paper.Paper at 0x10970e4d0>
        """

        return self.papers.values()

    def get_slices(self, key, papers=False):
        """
        Get all of the :class:`.Paper`\s (or just their IDs) in a 
        particular slice.

        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.Corpus` .
        papers : bool
            (default: False) If True, returns :class:`.Paper` objects rather
            than just their IDs.

        Returns
        -------
        slices : dict
            Keys are slice indices. If `papers` is `True`, values are
            lists of :class:`.Paper` instances; otherwise returns paper IDs
            (e.g. 'wosid' or 'doi').

        Raises
        ------
        RuntimeError : Corpus has not been sliced.
        KeyError : Data has not been sliced by [key]

        Examples
        --------

        .. code-block:: python

           >>> slices = MyCorpus.get_slices('date')
           >>> slices.keys()
           [1921, 1926, 1931, 1936, 1941, 1946, 1951, 1956, 1961, 1966, 1971]

           >>> slices[1926]
           ['10.2307/2470705',
            '10.2307/2480027',
            '10.2307/2255991',
            '10.2307/2428098',
            '10.2307/1654383',
            '10.2307/2256048',
            '10.2307/41421952']

        """

        if len(self.axes) == 0:
            raise(RuntimeError("Corpus has not been sliced."))
        if key not in self.axes.keys():
            raise(KeyError("Data has not been sliced by " + str(key)))

        slices = { k:self.axes[key][k] for k in sorted(self.axes[key].keys()) }

        if papers:  # Retrieve Papers.
            return { k:[ self.papers[p] for p in v ]
                     for k,v in slices.iteritems() }
        return slices

    def get_slice(self, key, index, papers=False):
        """
        Get the :class:`.Paper`\s (or just their IDs) from a single slice.

        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.Corpus` .
        index : str or int
            Slice index for key (e.g. 1999 for 'date').
        papers : bool
            (default: False) If True, returns :class:`.Paper` objects rather
            than just their IDs.

        Returns
        -------
        slice : list
            List of paper indices in this :class:`.Corpus` , or (if
            `papers` is `True`) a list of :class:`.Paper` instances.

        Raises
        ------
        RuntimeError : Corpus has not been sliced.
        KeyError : Data has not been sliced by [key]
        KeyError : [index] not a valid index for [key]

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.get_slice('date', 1926)
           ['10.2307/2470705',
            '10.2307/2480027',
            '10.2307/2255991',
            '10.2307/2428098',
            '10.2307/1654383',
            '10.2307/2256048',
            '10.2307/41421952']

           >>> MyCorpus.get_slice('date', 1926, papers=True)
           [<tethne.classes.paper.Paper at 0x109942110>,
            <tethne.classes.paper.Paper at 0x109922b50>,
            <tethne.classes.paper.Paper at 0x109934190>,
            <tethne.classes.paper.Paper at 0x109951410>,
            <tethne.classes.paper.Paper at 0x10971f350>,
            <tethne.classes.paper.Paper at 0x10975f810>,
            <tethne.classes.paper.Paper at 0x10975fed0>]

        """

        if len(self.axes) == 0:
            raise(RuntimeError("Corpus has not been sliced."))
        if key not in self.axes.keys():
            raise(KeyError("Data has not been sliced by " + str(key)))
        if index not in self.axes[key].keys():
            raise(KeyError(str(index) + " not a valid index for " + str(key)))

        slice = self.axes[key][index]

        if papers:
            return [ self.papers[p] for p in slice ]
        return slice

    def _get_slice_i(self, key, i):
        k = sorted(self.axes[key].keys())[i]
        return self.axes[key][k]

    def _get_by_i(self, key_indices):
        slices = []
        for k, i in key_indices:
            slice = set(self._get_slice_i(k, i))
            slices.append(slice)

        return list( set.intersection(*slices) )

    def _get_slice_keys(self, slice):
        if slice in self.get_axes():
            return sorted(self.axes[slice].keys())

    def get_axes(self):
        """
        Returns a list of all slice axes for this :class:`.Corpus` .

        Returns
        -------
        axes : list

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.get_axes()
           ['date', 'jtitle']

        """

        axes = self.axes.keys()
        return axes

    def N_axes(self):
        """
        Returns the number of slice axes for this :class:`.Corpus`\.

        Returns
        -------
        N : int
            Number of slice axes.

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.N_axes()
           2

        """

        N = len(self.axes.keys())
        return N

    def distribution(self, x_axis, y_axis=None):
        """
        Get the distribution of :class:`.Paper`\s over one or two slice axes.

        Returns a Numpy array describing the number of :class:`.Paper`
        associated with each slice-coordinate.

        Parameters
        ----------
        x_axis : str
            Name of a slice axis.
        y_axis : str
            (optional) Name of a slice axis.

        Returns
        -------
        dist : Numpy array
            Values are the number of :class:`.Paper` at that slice-coordinate.

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.distribution('date')
           array([[  1],
                  [  7],
                  [  8],
                  [ 24],
                  [ 32],
                  [ 30],
                  [ 64],
                  [ 66],
                  [ 78],
                  [107],
                  [ 76],
                  [106]])

        You can generate a figure for this distribution using
        :func:`.plot_distribution`\.

        """
        logger.debug('generate distribution over slices')
        if len(self.axes) == 0:
            logger.debug('Corpus has not been sliced')
            raise(RuntimeError("Corpus has not been sliced."))
        if x_axis not in self.get_axes():
            logger.debug('Corpus has no axis {0}'.format(x_axis))
            raise(KeyError("X axis invalid for this Corpus."))

        x_size = len(self.axes[x_axis])
        logger.debug('x axis size: {0}'.format(x_axis))

        if y_axis is not None:
            logger.debug('y axis: {0}'.format(y_axis))
            if y_axis not in self.get_axes():
                logger.debug('Corpus has not axis {0}'.format(y_axis))
                raise(KeyError("Y axis invalid for this Corpus."))
            y_size = len(self.axes[y_axis])
            logger.debug('y axis size: {0}'.format(y_axis))
        else:   # Only 1 slice axis.
            logger.debug('only 1 slice axis')
            y_size = 1
        shape = (x_size, y_size)
        logger.debug('distribution shape: {0}'.format(shape))
        I = []
        J = []
        K = []
        for i in xrange(x_size):
            if y_axis is None:
                k = len(self._get_by_i([(x_axis, i)]))
                if k > 0:
                    I.append(i)
                    J.append(0)
                    K.append(k)
            else:
                for j in xrange(y_size):
                    k = len(self._get_by_i([(x_axis, i),(y_axis, j)]))
                    if k > 0:
                        I.append(i)
                        J.append(j)
                        K.append(k)

        # TODO: Move away from SciPy, to facilitate PyPy compatibility?
        dist = np.array(scipy.sparse.coo_matrix((K, (I,J)), shape=shape).todense())

        return dist

    # TODO: Merge this with :func:`.distribution`
    def feature_distribution(self, featureset, feature, x_axis, y_axis=None,
                                   mode='counts', normed=True   ):
        """
        Get the distribution of a ``feature`` over one or two slice axes.

        You can generate a figure for this distribution using
        :func:`.plot_distribution`\.

        Parameters
        ----------
        featureset : str
            Name of a set of features (eg 'unigrams')
        feature : str
            String representation of the feature.
        x_axis : str
            Name of a slice axis.
        y_axis : str
            (optional) Name of a slice axis.
        mode : str
            (default: True) 'counts' or 'documentCounts'
        normed : bool
            (default: True) If True, values are normalized for each slice.

        Returns
        -------
        dist : matrix

        Examples
        --------

        .. code-block:: python

           >>> MyCorpus.feature_distribution('unigrams', 'four', 'date',
                                        mode='counts', normed=True)
           [[  7.10025561e-05]
            [  1.81508792e-03]
            [  3.87657001e-04]
            [  7.68344218e-04]
            [  9.81739643e-04]
            [  1.02986612e-03]
            [  5.04682875e-04]
            [  6.60851176e-04]
            [  1.02951270e-03]
            [  9.94742078e-04]
            [  1.04085711e-03]]

        Notes
        -----

        In the future, it may make sense to merge this into
        :func:`.distribution`\.

        """

        if mode not in [ 'counts', 'documentCounts' ]:
            raise RuntimeError('No such mode. Try "counts" or "documentCounts"')

        if featureset not in self.features:
            raise KeyError('No such featureset in this Corpus')

        index = self.features[featureset]['index']
        feature_lookup = { v:k for k,v in index.iteritems() }
        try:
            findex = feature_lookup[feature]
        except KeyError:
            raise KeyError('No such feature in featureset')

        if x_axis not in self.axes:
            raise KeyError('No such slice axis in this Corpus; try .slice()')

        logger.debug('generate distribution over slices')

        x_size = len(self.axes[x_axis])
        logger.debug('x axis size: {0}'.format(x_axis))

        if y_axis is not None:
            logger.debug('y axis: {0}'.format(y_axis))
            if y_axis not in self.get_axes():
                logger.debug('Corpus has not axis {0}'.format(y_axis))
                raise(KeyError("Y axis invalid for this Corpus."))
            y_size = len(self.axes[y_axis])
            logger.debug('y axis size: {0}'.format(y_axis))
        else:   # Only 1 slice axis.
            logger.debug('only 1 slice axis')
            y_size = 1

        shape = (x_size, y_size)
        logger.debug('distribution shape: {0}'.format(shape))

        fvalues = self.features[featureset]['features']

        def _get_value(papers):
            vtuples = [ fv for p in papers for fv in fvalues[p] ]
            values = [ v for f,v in vtuples if f == findex ]

            if mode == 'counts':
                val = sum(values)
                if normed:
                    Nwords = sum([ v for f,v in vtuples])
                    try:
                        val = float(val)/float(Nwords)
                    except ZeroDivisionError:
                        val = 0.
            if mode == 'documentCounts':
                val = len(values)
                if normed:
                    try:
                        val = float(val)/float(len(papers))
                    except ZeroDivisionError:
                        val = 0.

            return val

        I = []
        J = []
        K = []
        for i in xrange(x_size):
            if y_axis is None:
                papers = self._get_by_i([(x_axis, i)])
                k = _get_value(papers)
                if k > 0:
                    I.append(i)
                    J.append(0)
                    K.append(k)
            else:
                for j in xrange(y_size):
                    papers = self._get_by_i([(x_axis, i),(y_axis, j)])
                    k = _get_value(papers)
                    if k > 0:
                        I.append(i)
                        J.append(j)
                        K.append(k)

        dist = np.array(scipy.sparse.coo_matrix((K, (I,J)), shape=shape).todense())

        return dist

    def feature_counts(self, featureset, slice, axis='date',
                                                documentCounts=False):
        """
        Get the frequency of a feature in a particular ``slice`` of ``axis``.

        Parameters
        ----------
        featureset : str
            Name of a featureset in the corpus.
        slice : int or str
            Name of a slice along ``axis``.
        axis : str
            (default: 'date') Name of slice axis containing ``slice``.
        documentCounts : bool
            (default: False) If True, returns document counts (i.e. the number
            of documents in which a feature occurs) rather than the frequency
            (total number of instances) of that feature.

        Returns
        -------
        counts : dict
        """

        if featureset not in self.features:
            raise KeyError('No such featureset in this Corpus')

        index = self.features[featureset]['index']
        feature_lookup = { v:k for k,v in index.iteritems() }

        fvalues = self.features[featureset]['features']

        papers = self.get_slice(axis, slice)
        counts = Counter()
        for p in papers:
            try:
                for f,v in fvalues[p]:
                    if documentCounts:
                        counts[f] += 1
                    else:
                        counts[f] += v
            except KeyError:
                pass

        return dict(counts)

    def plot_distribution(self, x_axis=None, y_axis=None, type='bar',
                                aspect=0.2, step=2, fig=None, mode='papers',
                                fkwargs={}, **kwargs):
        """
        Plot distribution of papers or features along slice axes, using
        `MatPlotLib <http://matplotlib.org/>`_.

        You must first use :func:`.slice` to divide your data up along axes of
        interest. Then you can use :func:`.distribution` or
        :func:`.plot_distribution` to generate descriptive statistics about your
        data.

        Parameters
        ----------
        x_axis : str
            Name of a slice axis to use for the x axis.
        y_axis : str
            (optional) Name of a slice axis to use for the y axis. If provided,
            uses PyPlot's :func:`plt.imshow` method to generate a 'heatmap'.
        type : str
            PyPlot method to use for 1-dimensional plots. ('plot' or 'bar').
        aspect : float
            When making a 2-d plot (i.e. `y_axis` is provided), sets the aspect
            ratio for the plot.
        step : int
            When making a 2-d plot (i.e. `y_axis` is provided), sets the range
            step for x axis tick labels.
        fig : :class:`matplotlib.figure`
            (optional) If not provided, will generate a new instance of
            :class:`matplotlib.figure`\.
        mode : str
            (default: 'papers') Specify whether to plot the distribution of
            'papers' or 'features'. See examples, below.
        fkwargs : dict
            Keyword arguments passed to PyPlot method.

        Returns
        -------
        fig : :class:`matplotlib.figure`

        Examples
        --------

        The default behavior is to plot the distribution of paper across
        ``x_axis`` (and ``y_axis``):

        .. code-block:: python

           >>> MyCorpus.slice('date', method='time_period', window_size=5)
           >>> MyCorpus.plot_distribution('date')

        Should generate a plot that looks something like this:

        .. figure:: _static/images/corpus_plot_distribution.png
           :width: 400
           :align: center

        To generate a 2-dimensional plot using `date` and `jtitle`, you could do
        something like:

        .. code-block:: python

           >>> MyCorpus.slice('date', method='time_period', window_size=5)
           >>> MyCorpus.slice('jtitle')
           >>> MyCorpus.plot_distribution('date', 'jtitle')

        Which should generate a plot that looks something like:

        .. figure:: _static/images/corpus_plot_distribution_2d.png
           :width: 600
           :align: center

        If ``mode='features`` is set, this method will plot the distribution
        of a feature across ``x_axis`` (and ``y_axis``). Set keyword arguments
        for :func:`Corpus.feature_distribution` using ``fkwargs``.

        .. code-block:: python

           >>> fkwargs = {
           ...     'featureset': 'unigrams',
           ...     'feature': 'four',
           ...     'mode': 'counts',
           ...     'normed': True,
           ...     }
           >>> fig = MyCorpus.plot_distribution('date', 'jtitle', mode='features',
                                         fkwargs=fkwargs, interpolation='none')
           >>> fig.savefig('/path/to/dist.png')

        .. figure:: _static/images/testdist.png
           :width: 600
           :align: center

        """

        if fig is None:
            fig = plt.figure(figsize=(20,10))

        if x_axis is None:
            x_axis = self.get_axes()[0]

        xkeys = self._get_slice_keys(x_axis)

        if mode == 'features':
            featureset = fkwargs['featureset']
            feature = fkwargs['feature']
            fmode = fkwargs['mode']
            fnormed = fkwargs['normed']

        if y_axis is None:
            if mode == 'papers':
                yvals = self.distribution(x_axis)
            elif mode == 'features':
                yvals = self.feature_distribution(featureset, feature, x_axis,
                                                  mode=fmode, normed=fnormed)
            plt.__dict__[type](xkeys, yvals, **kwargs)
            plt.xlim(xkeys[0], xkeys[-1])   # Already sorted.
        else:
            ykeys = self._get_slice_keys(y_axis)
            ax = fig.add_subplot(111)
            if mode == 'papers':
                values = self.distribution(y_axis, x_axis)
            elif mode == 'features':
                values = self.feature_distribution(featureset, feature, y_axis,
                                                   x_axis, fmode, fnormed)
            ax.imshow(values, aspect=aspect, **kwargs)
            plt.yticks(np.arange(len(ykeys)), ykeys)

            nxkeys = len(xkeys)
            tickstops = range(0, nxkeys, step)

            ax.set_xticks(tickstops)
            ax.set_xticklabels([ xkeys[i] for i in tickstops ])
            plt.xlim(0, nxkeys-1)   # Already sorted.
            plt.subplots_adjust(left=0.5)

        return fig

