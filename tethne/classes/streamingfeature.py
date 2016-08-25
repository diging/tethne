from collections import Counter, OrderedDict
from itertools import repeat
import sys, copy
from scipy.sparse import coo_matrix
import numpy as np


class StreamingFeature(object):
    def __init__(self, feature_getter, token_normalizer=None, token_filter=None):
        self.feature_getter = feature_getter
        # Allows for dependency injection in unit tests.
        self.token_filter = token_filter if token_filter else lambda *a: a[1]
        self.token_normalizer = token_normalizer if token_normalizer else lambda a: a
        self.paths_buffer = None

    def __iter__(self):
        return self.feature_getter()

    def __getitem__(self, key):
        feature_iter = self.feature_getter(key)
        while True:
            try:
                feature, value = feature_iter.next()
            except StopIteration:
                break
            feature = self.token_normalizer(feature)
            value = self.token_filter(feature, value)
            if value:
                yield feature, value
    def keys(self):
        if self.paths_buffer is None:
            self.paths_buffer = [i for i, _ in self.feature_getter()]
        return self.paths_buffer


class GetterThingy(object):
    def __init__(self, getter):
        self.getter = getter

    def __getitem__(self, key):
        return self.getter(key)

    def get(self, key, default):
        try:
            return self.getter(key)
        except KeyError:
            return default


class GensimCorpus(object):
    def __init__(self, iterator_factory, size):
        self.iterator_factory = iterator_factory
        self.size = size

    def __iter__(self):
        return self.iterator_factory()

    def __len__(self):
        return self.size


class StreamingFeatureSet(object):
    """

    Parameters
    ----------
    path : str
        Location of data.
    parser : callable
        Should accept an optional parameter ``identifier`` to select data
        for a single record. Returns a nested iterator that iterates over
        records and over feature, values. If the inner iterator is not
        called, then no files should be opened.
    token_normalizer : callable
        Signature: (feature). Called before ``token_filter``, should return
        a unicode object. TODO: multilingual support.
    token_filter : callable
        Signature: (feature, count, global count=None, document count=None).
        If return is truthy, will be used as the count value for this
        feature. If falsey, the feature will be ommitted. If counts have not
        yet been generated, then only feature and count will be provided.
        Note that this allows for implementations that apply different
        filtering logic depending on whether this is the first pass (no
        global/document counts) or later passes.

    """

    def __init__(self, path, parser, token_normalizer=None, token_filter=None,
                 **parse_kwargs):
        self.path = path
        self.parser_class = parser
        self.parser = self.parser_class(path, **parse_kwargs)
        self.token_filter = token_filter if token_filter else lambda *a: a[1]
        self.token_normalizer = token_normalizer if token_normalizer else lambda a: a
        self.parse_kwargs = parse_kwargs
        self.paths_buffer = None
        self._index = OrderedDict()
        self._lookup = OrderedDict()
        self._keys = OrderedDict()
        self._key_lookup = OrderedDict()

    def __getitem__(self, key):
        return self.features[key]

    def __contains__(self, key):
        sys.stdout.flush()
        if self.paths_buffer is None:
            self.paths_buffer = [i for i, _ in self.parser.parse()]
        return key in self.paths_buffer

    def keys(self):
        if len(self._keys) > 0:
            return self._keys.values()
        return self.parser.keys()

    def _generate_counts(self, token_normalizer=None, token_filter=None):
        self.counts = Counter()
        self.documentCounts = Counter()

        # Allows for dependency injection in unit tests.
        token_normalizer = token_normalizer if token_normalizer else self.token_normalizer
        token_filter = token_filter if token_filter else self.token_filter

        for identifier, feature_iter in self.parser.parse():
            for feature, value in feature_iter:
                feature = token_normalizer(feature)
                value = token_filter(feature, value)
                if value:
                    self.counts[feature] += value
                    self.documentCounts[feature] += 1.

    def __iter__(self):
        return self.parser.parse()

    @property
    def index(self):
        if len(self._index) > 0:
            return self._index
        return GetterThingy(lambda w: w)

    @property
    def features(self):
        return StreamingFeature(lambda ident=None: self.parser.parse(self.path, ident, **self.parse_kwargs),
                                self.token_normalizer, self.token_filter)

    def transform(self, func):
        """
        Returns a new :class:`StreamingFeatureSet` adding ``func`` as an
        additional :prop:`.token_filter`\.
        """
        def _combined_filter(f, c, C=None, DC=None):
            c = self.token_filter(f, c, C, DC)
            if c:
                return func(f, c, C, DC)

        return StreamingFeatureSet(self.path, self.parser_class, self.token_normalizer, _combined_filter, **self.parse_kwargs)

    def normalize(self, func):
        """
        Returns a new :class:`StreamingFeatureSet` with ``func`` as an
        additional :prop:`.token_normalizer`\.
        """

        _combined_normalizer = lambda f: func(self.token_normalizer(f))

        return StreamingFeatureSet(self.path, self.parser_class, _combined_normalizer, self.token_filter, **self.parse_kwargs)

    def _index_tokens(self):
        self._len = 0
        for ident, feature_iter in self:
            self._len += 1
            for token, value in feature_iter:
                token = self.token_normalizer(token)
                if token in self._lookup or not self.token_filter(token, value):
                    continue
                idx = len(self._index)
                self._lookup[token] = idx
                self._index[idx] = token

    def _index_in_passing(self, token):
        token = self.token_normalizer(token)
        if token in self._lookup:
            return self._lookup[token]
        idx = len(self._index)
        self._index[idx] = token
        self._lookup[token] = idx
        return idx

    def _index_document_in_passing(self, doc):
        if doc in self._key_lookup:
            return self._key_lookup[doc]
        idx = len(self._keys)
        self._keys[idx] = doc
        self._key_lookup[doc] = idx
        return idx

    def _stream_with_index(self):
        iterator = self.parser.parse()

        while True:
            try:
                ident, feature_iter = iterator.next()
            except StopIteration:
                break
            yield [(self._lookup[self.token_normalizer(token)],
                    self.token_filter(self.token_normalizer(token), value))
                   for token, value in feature_iter if self.token_filter(value)]

    def to_coo_matrix(self):
        """
        Generate a :class:`scipy.sparse.coo_matrix` from the data in this
        :class:`.StreamingFeatureSet`\.

        Returns
        -------
        data : :class:`scipy.sparse.coo_matrix`
        documents : dict
            Maps row indices (int) to document identifiers.
        vocabulary : dict
            Maps column indices (int) to words.
        """
        data = np.array([
            (self.token_filter(self.token_normalizer(f), c), self._index_document_in_passing(d), self._index_in_passing(f))
            for d, feature_iter in self for f, c in feature_iter if self.token_filter(f, c)
        ]).T

        return coo_matrix((data[0], (data[1], data[2]))),\
                self._keys,\
                self._index

    def to_gensim_corpus(self, raw=False):
        """
        Yield a bag-of-words corpus compatible with the Gensim package.

        Returns a (corpus, index) tuple (see below).

        Parameters
        ----------
        context : str
            If provided, each "document" in the Gensim corpus will be a chunk
            of type ``context``.


        Returns
        -------
        list
            A list of lists of (id, count) tuples. Each sub-list represents a
            single context item (e.g. a document, or a paragraph). This is the
            "bag of words" representation used in Gensim.
        dict
            Maps integer IDs to words.

        Examples
        --------

        .. code-block:: python

           >>> from tethne.readers.wos import read
           >>> corpus = read('/path/to/my/data')
           >>> from nltk.tokenize import word_tokenize
           >>> corpus.index_feature('abstract', word_tokenize)
           >>> gensim_corpus, id2word = corpus.features['abstract'].to_gensim_corpus()
           >>> from gensim import corpora, models
           >>> model = models.ldamodel.LdaModel(corpus=gensim_corpus,
                                                id2word=id2word,
                                                num_topics=5, update_every=1,
                                                chunksize=100, passes=1)
        """

        if raw:
            return [[token for term, count in feature_iter for token in repeat(term, int(count))]
                    for i, feature_iter in self], None
        self._index_tokens()
        return GensimCorpus(self._stream_with_index, size=len(self.parser)), self._index
