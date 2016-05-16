"""
Classes in this module provide structures for additional data about
:class:`.Paper`\s.
"""

from collections import Counter, defaultdict

from tethne.utilities import _iterable
try:    # Might as well use numpy if it is available.
    import numpy as np
    argsort = lambda l: list(np.argsort(l))
except ImportError:
    from tethne.utilities import argsort

import logging
logger = logging.getLogger('feature')
logger.setLevel('WARNING')


from itertools import chain, izip
from collections import Counter, defaultdict

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    xrange = range
    unicode = str


class StructuredFeature(list):
    """
    A :class:`.StructuredFeature` represents the contents of a document as an
    array of tokens, divisible into a set of nested contexts.

    The canonical use-case is to represent a document as a set of words divided
    into sentences, paragraphs, and (perhaps) pages.

    Parameters
    ----------
    tokens : list
        An ordered list of tokens.
    contexts : list
        A list of (name, indices) 2-tuples, where ``name`` is string-like and
        indices is an iterable of int token indices.
    reference : tuple
        A (feature, map) 2-tuple, where ``feature`` is a
        :class:`.StructuredFeature` and ``map`` is a dict mapping token indices
        in this :class:`.StructuredFeature` to token indices in ``feature``.
    """
    def __init__(self, tokens, contexts=None, reference=None):
        self.extend(tokens)
        self.contexts = {}
        self.contexts_ranked = []
        self.referenceFeature = None
        self.referenceMap = None

        if contexts:
            self._validate_contexts(contexts)
            for context in contexts:
                self._validate_context(context)
                self.add_context(*context)

        if reference:
            self._validate_reference(reference)

            self.referenceFeature, self.referenceMap = reference

    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.Feature`\.
        """
        if len(self) > 0:
            return set(self)
        return set()

    def __getitem__(self, selector):
        if type(selector) is int:
            return super(StructuredFeature, self).__getitem__(selector)

        if type(selector) in [str, unicode]:
            if selector in self.contexts:
                return self.context_chunks(selector)
        elif type(selector) is tuple:
            if selector[0] in self.contexts:
                return self.context_chunk(*selector)

    def context_chunks(self, context):
        """
        Retrieves all tokens, divided into the chunks in context ``context``.

        Parameters
        ----------
        context : str
            Context name.

        Returns
        -------
        chunks : list
            Each item in ``chunks`` is a list of tokens.
        """
        N_chunks = len(self.contexts[context])
        chunks = []
        for j in xrange(N_chunks):
            chunks.append(self.context_chunk(context, j))
        return chunks

    def context_chunk(self, context, j):
        """
        Retrieve the tokens in the ``j``th chunk of context ``context``.

        Parameters
        ----------
        context : str
            Context name.
        j : int
            Index of a context chunk.

        Returns
        -------
        chunk : list
            List of tokens in the selected chunk.
        """

        N_chunks = len(self.contexts[context])
        start = self.contexts[context][j]
        if j == N_chunks - 1:
            end = len(self)
        else:
            end = self.contexts[context][j+1]
        return [self[i] for i in xrange(start, end)]

    def _validate_context(self, context):
        try:
            assert hasattr(context, '__iter__')
            assert len(context) == 2
            assert type(context[0]) in [str, unicode]
            assert hasattr(context[1], '__iter__')
            assert type(context[1][0]) is int
        except AssertionError:
            raise ValueError("""a context should be a (name, indices) 2-tuple,
            where ``name`` is string-like and indices is an iterable of int
            token indices.""")

        if max(context[1]) > len(self):
            raise ValueError("""One or more indices in the specified context
            exceed the number of tokens in this StructuredFeature.""")

    @staticmethod
    def _validate_contexts(contexts):
        try:
            assert hasattr(contexts, '__iter__')
        except AssertionError:
            raise ValueError("""contexts should be a list of (name, indices)
            2-tuples, where ``name`` is string-like and indices is an iterable
            of int token indices.""")

    @staticmethod
    def _validate_reference(reference):
        try:
            assert type(reference) is tuple
            assert type(reference[0]) is StructuredFeature
            assert type(reference[1]) is dict
        except AssertionError:
            raise ValueError("""reference should be a (feature, map) 2-tuple
            where ``feature`` is a StructuredFeature and ``map`` is a dict
            mapping token indices in this StructuredFeature to token indices
            in ``feature``.""")

    def add_context(self, name, indices, level=None):
        """
        Add a new context level to the hierarchy.

        By default, new contexts are added to the lowest level of the hierarchy.
        To insert the context elsewhere in the hierarchy, use the ``level``
        argument. For example, ``level=0`` would insert the context at the
        highest level of the hierarchy.

        Parameters
        ----------
        name : str
        indices : list
            Token indices at which each chunk in the context begins.
        level : int
            Level in the hierarchy at which to insert the context. By default,
            inserts context at the lowest level of the hierarchy

        """

        self._validate_context((name, indices))

        if level is None:
            level = len(self.contexts_ranked)
        self.contexts_ranked.insert(level, name)
        self.contexts[name] = indices


class Feature(list):
    """
    A :class:`.Feature` instance is a sparse vector of features over a given
    concept (usually a :class:`.Paper`\).

    For example, a :class:`.Feature` might represent word counts for a single
    :class:`.Paper`\.

    A :class:`.Feature` may be initialized from a list of ``(feature, value)``
    tuples...

    .. code-block:: python

       >>> myFeature = Feature([('the', 2), ('pine', 1), ('trapezoid', 5)])

    ...or by passing a list of raw feature tokens:

    .. codeblock:: python

       >>> myFeature = Feature(['the', 'the', 'pine', 'trapezoid', 'trapezoid',
       ...                      'trapezoid', 'trapezoid', 'trapezoid'])
       >>> myFeature
       [('the', 2), ('pine', 1), ('trapezoid', 5)]

    To get the set of unique features in this :class:`.Feature`\, use
    :prop:`.Feature.unique`\:

    .. code-block:: python

       >>> myFeature.unique
       set(['the', 'pine', 'trapezoid'])

    Normalized feature values (so that all values sum to 1.) can be accessed
    using :prop:`.Feature.norm`\.

    .. code-block:: python

       >>> myFeature.norm
       [('the', 0.25), ('pine', 0.125), ('trapezoid', 0.625)]

    """

    def __init__(self, data):
        if len(data) > 0:
            self.extend(data)

    def __add__(self, data):
        if len(data) > 0:
            if type(data[0]) is tuple and type(data[0][-1]) in [float, int]:
                # There may be overlap with existing features,
                combined_data = defaultdict(type(data[0][-1]))
                for k, v in data + list(self):
                    combined_data[k] += v
                return combined_data.items()
            else:   # Recurses.
                c = Counter(_iterable(data))
                keys = list(c.keys())
                return self.__add__(list(zip(keys, c.values())))
        return self

    def __sub__(self, data):
        if len(data) > 0:
            if type(list(data)[0]) is tuple and type(list(data)[0][-1]) in [float, int]:
                combined_data = defaultdict(type(data[0][-1]))
                combined_data.update(dict(self))
                for k, v in data:
                    combined_data[k] -= v
                return list(combined_data.items())
            else:   # Recurses.
                return self.__sub__(list(Counter(_iterable(data)).items()))
        return self

    def __iadd__(self, data):
        return self.extend(data)

    def __isub__(self, data):
        if len(data) > 0:
            combined_data = self.__sub__(data)
            del self[:]
            super(Feature, self).extend(combined_data)
        return self

    def extend(self, data):
        if len(data) > 0:
            combined_data = self.__add__(data)  # Combines new and extant data.
            del self[:]                         # Clear old data.
            super(Feature, self).extend(combined_data)
        return self

    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.Feature`\.
        """
        if len(self) > 0:
            return set(list(zip(*self))[0])
        return set()

    @property
    def norm(self):
        T = sum(list(zip(*self))[1])
        return Feature([(i, float(v)/T) for i, v in self])

    def top(self, topn=10):
        """
        Get a list of the top ``topn`` features in this :class:`.Feature`\.

        Example
        -------

        .. code-block:: python

        >>> myFeature = Feature([('the', 2), ('pine', 1), ('trapezoid', 5)])
        >>> myFeature.top(1)
        [('trapezoid', 5)]

        Parameters
        ----------
        topn : int

        Returns
        -------
        list
        """
        return [self[i] for i in argsort(list(zip(*self))[1])[::-1][:topn]]

    def value(self, element):
        return dict(self)[element]


class BaseFeatureSet(object):
    def __init__(self, features={}):
        self._setUp()

        for paper, feature in features.iteritems():
            self.add(paper, feature)

    def _setUp(self):
        self.index = {}
        self.lookup = {}
        self.counts = Counter()
        self.documentCounts = Counter()
        self.features = {}
        self.with_feature = defaultdict(list)

    def __getitem__(self, key):
        try:
            return self.features[key]
        except KeyError as E:
            if type(key) is int:
                return self.features.values()[key]
            raise E

    def __len__(self):
        return len(self.features)

    def items(self):
        return self.features.items()

    def iteritems(self):
        return self.features.iteritems()

    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.FeatureSet`\.
        """
        return set(self.lookup.keys())

    @property
    def N_features(self):
        return len(self.unique)

    @property
    def N_documents(self):
        return len(self.features)

    def count(self, elem):
        logger.debug(u'Get count for {0}'.format(elem))
        if elem in self.lookup:
            i = self.lookup[elem]
            count = self.counts[i]
            logger.debug(u'Found elem %s with index %i and count %f' % (elem, i, count))
            return count
        else:
            return 0.

    def documentCount(self, elem):
        if elem in self.lookup:
            return self.documentCounts[self.lookup[elem]]
        else:
            return 0.

    def papers_containing(self, elem):
        return self.with_feature[self.lookup[elem]]

    def add(self, paper_id, feature):
        if type(feature) not in [Feature, StructuredFeature]:
            raise ValueError("""`feature` must be an instance of Feature or
            StructuredFeature""")

        self.features[paper_id] = feature

        if len(feature) < 1:
            return

        if type(feature[0]) is not tuple:
            feature = Counter(feature).items()

        for elem, value in feature:
            i = self.lookup.get(elem, len(self.lookup))

            self.lookup[elem] = i
            self.index[i] = elem

            self.counts[i] += value
            self.documentCounts[i] += 1.
            self.with_feature[i].append(paper_id)


    def top(self, topn, by='counts'):
        """
        Get the top ``topn`` features in the :class:`.FeatureSet`\.

        Parameters
        ----------
        topn : int
            Number of features to return.
        by : str
            (default: 'counts') How features should be sorted. Must be 'counts' or
            'documentcounts'.

        Returns
        -------
        list

        """

        if by not in ['counts', 'documentCounts']:
            raise NameError('kwarg `by` must be "counts" or "documentCounts"')

        cvalues = getattr(self, by)
        top = [list(cvalues.keys())[i] for i in argsort(list(cvalues.values()))][::-1]
        return [(self.index[x], cvalues[x]) for x in top][:topn]


class StructuredFeatureSet(BaseFeatureSet):
    """
    A :class:`.StructuredFeatureSet` organizes several
    :class:`.StructuredFeature` instances.
    """

    def transform(self, func):
        features = {}
        for i, feature in self.features.iteritems():
            feature_ = []
            for f in feature:
                t = self.lookup[f]
                v_ = func(f, self.count(f), feature.count(f), self.documentCounts[t])
                if v_ is not None:
                    feature_.append(f)
            features[i] = StructuredFeature(feature_)

        return StructuredFeatureSet(features)

    def context_chunks(self, context):
        """
        Retrieves all tokens, divided into the chunks in context ``context``.

        If ``context`` is not found in a feature, then the feature will be
        treated as a single chunk.

        Parameters
        ----------
        context : str
            Context name.

        Returns
        -------
        papers : list
            2-tuples of (paper ID, chunk indices).
        chunks : list
            Each item in ``chunks`` is a list of tokens.
        """

        chunks = []
        papers = []
        for paper, feature in self.features.iteritems():
            if context in feature.contexts:
                new_chunks = feature.context_chunks(context)
            else:
                new_chunks = list(feature)
            indices = range(len(chunks), len(chunks) + len(new_chunks))
            papers.append((paper, indices))
            chunks += new_chunks
        return papers, chunks


class FeatureSet(BaseFeatureSet):
    """
    A :class:`.FeatureSet` organizes multiple :class:`.Feature` instances.
    """

    def __init__(self, features=None):
        if not features:
            features = dict()
        self._setUp()

        logger.debug(u'Initialize FeatureSet with %i features' % len(features))
        self.features = features
        allfeatures = [v for v in chain(*features.values())]
        logger.debug('features: {0}; allfeatures: {1}'.format(len(features), len(allfeatures)))
        if len(features) > 0 and len(allfeatures) > 0:
            allfeatures_keys = zip(*allfeatures)[0]

            for i, elem in enumerate(set(allfeatures_keys)):
                self.index[i] = elem
                self.lookup[elem] = i
                logger.debug(u'Add feature {0} with index {1}'.format(elem, i))

            self.counts = defaultdict(float)
            for elem, v in allfeatures:
                i = self.lookup[elem]
                self.counts[i] += v
            self.documentCounts = Counter([self.lookup[elem]
                                           for elem
                                           in allfeatures_keys])

            self.with_feature = defaultdict(list)
            for paper_id, counts in features.iteritems():
                try:
                    for elem in zip(*counts)[0]:
                        i = self.lookup[elem]
                        self.with_feature[i].append(paper_id)
                except IndexError:    # A Paper may not have any features.
                    pass



    def transform(self, func):
        """
        Apply a transformation to tokens in this :class:`.FeatureSet`\.

        Parameters
        ----------
        func : callable
            Should take four parameters: token, value in document (e.g. count),
            value in :class:`.FeatureSet` (e.g. overall count), and document
            count (i.e. number of documents in which the token occurs). Should
            return a new numeric (int or float) value, or None. If value is 0
            or None, the token will be excluded.

        Returns
        -------
        :class:`.FeatureSet`

        Examples
        --------

        Apply a tf*idf transformation.

        .. code-block:: python

           >>> words = corpus.features['words']
           >>> def tfidf(f, c, C, DC):
           ... tf = float(c)
           ... idf = log(float(len(words.features))/float(DC))
           ... return tf*idf
           >>> corpus.features['words_tfidf'] = words.transform(tfidf)

        """
        features = {}
        for i, feature in self.features.iteritems():
            feature_ = []
            for f, v in feature:
                t = self.lookup[f]
                v_ = func(f, v, self.counts[t], self.documentCounts[t])
                if v_ > 0 and v_ is not None:
                    feature_.append((f, v_))
            features[i] = Feature(feature_)

        return FeatureSet(features)

    def translate(self, func):
        features = {}
        for i, feature in self.features.iteritems():
            features_ = []
            for f, v in feature:
                t = self.lookup[f]
                f_ = func(f, v, self.counts[t], self.documentCounts[t])
                if f_:
                    feature_.append((f_, v))
            features[i] = Feature(feature_)
        return FeatureSet(features)


    def as_matrix(self):
        """

        """
        matrix = [[0. for e in xrange(self.N_features)]
                  for i in xrange(self.N_documents)]
        for i, p in enumerate(self.features.keys()):
            f = self.features[p]
            for e, c in f:
                j = self.lookup[e]
                print i, j
                matrix[i][j] = c

        return matrix

    def as_vector(self, p, norm=False):
        m = len(self.index.keys())

        if norm:
            values = dict(self.features[p].norm)
        else:
            values = dict(self.features[p])

        vect = []
        for i in xrange(m):
            e = self.index[i]
            if e in values:
                c = float(values[e])
            else:
                c = 0.
            vect.append(c)

        return vect


def feature(f):
    """
    Decorator for properties that should be represented as :class:`.Feature`\s.
    """
    def deco(self):
        return Feature(f(self))
    return deco
