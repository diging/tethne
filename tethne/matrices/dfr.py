"""
Methods for generating Numpy data objects from JSTOR Data-for-Research datasets.

.. autosummary::

   array
   matrix

"""

import numpy as np

class Map(object):
    """
    Maps integer indices to string values.
    """

    def __init__(self):
        self.by_str = {}
        self.by_int = {}

    def __setitem__(self, key, value):
        if type(key) == str:
            self.by_str[key] = value
            self.by_int[value] = key
        if type(key) == int:
            self.by_int[key] = value
            self.by_str[value] = key

    def __getitem__(self, key):
        if type(key) == str:
            return self.by_str[key]
        if type(key) == int:
            return self.by_int[key]

    def __len__(self):
        return len(self.by_str)

def array(data, normalize=False, verbose=False):
    """
    Yields a Numpy array, along with feature-index and document-index mappings.

    Parameters
    ----------
    data : dict
        Keys are document identifiers (e.g. DOIs), values are lists of feature-
        frequency tuples.
    normalize : bool
        If True, matrix values are relative to the maximum value in the matrix.

    Returns
    -------
    A : Numpy array
        Columns are documents, rows are features.
    document_index : class:`.Map`
        Maps column indices to document identifiers (keys of provided data).
    feature_index : :class:`.Map`
        Maps row indices to features.

    """
    document_index, feature_index = _index_data(data, verbose)
    N_docs = len(document_index)
    N_feat = len(feature_index)
    max_v = np.max([ np.float(v[1]) for doc in data.keys() for v in data[doc] ])

    if verbose:
        print "array(): {0} documents, {1} features".format(N_docs, N_feat)

    if normalize:
        dtype = np.float
    else:
        dtype = np.int

    A = np.zeros((N_docs, N_feat), dtype=dtype)
    d = 0

    for doc, features in data.iteritems():
        if verbose:
            d += 1
            if d%200 == 0:
                print "array(): Processed {0} of {1} documents"\
                                                              .format(d, N_docs)

        i = document_index[doc]
        for f, v in features:
            j = feature_index[f]
            if normalize:
                v = v/max_v
            A[i, j] = v

    if verbose:
        print "array(): Processed all documents."

    return A, document_index, feature_index

def matrix(data, normalize=False, verbose=False):
    """
    Yields a Numpy matrix, along with feature-index and document-index mappings.

    Parameters
    ----------
    data : dict
        Keys are document identifiers (e.g. DOIs), values are lists of feature-
        frequency tuples.
    normalize : bool
        If True, matrix values are relative to the maximum value in the matrix.

    Returns
    -------
    M : Numpy matrix
        Columns are documents, rows are features.
    document_index : class:`.Map`
        Maps column indices to document identifiers (keys of provided data).
    feature_index : :class:`.Map`
        Maps row indices to features.

    """

    if verbose:
        print "matrix(): converting array to matrix."

    A, document_index, feature_index = array(data, normalize, verbose)
    M = np.asmatrix(A)

    if verbose:
        print "matrix(): done."

    return M, document_index, feature_index

def _index_data(data, verbose=False):
    """
    Yields document and feature indices from a data dict.

    Parameters
    ----------
    data : dict
        Keys are document identifiers (e.g. DOIs), values are lists of feature-
        frequency tuples.

    Returns
    -------
    document_index : class:`.Map`
        Maps integer indices to document identifiers (keys of provided data).
    feature_index : :class:`.Map`
        Maps integer row indices to features.
    """

    document_index = Map()
    feature_index = Map()
    N_docs = len(data)

    if verbose:
        print "_index_data(): Indexing {0} documents".format(N_docs)

    features = set()
    for i in xrange(N_docs): # Index documents.
        if verbose and i%200 == 0:
            print "_index_data(): Indexed {0} of {1} documents"\
                                                              .format(i, N_docs)

        document_index[i] = data.keys()[i]
        for f,c in data.values()[i]:
            features.add(f) # Build a set of features.

    N_feat = len(features)
    if verbose:
        print "_index_data(): Done indexing documents."
        print "_index_data(): Indexing {0} features.".format(N_feat)

    features = list(features)
    for i in xrange(N_feat):  # Index features.
        if verbose and i %10000 == 0:
            print "_index_data(): Indexed {0} of {1} features."\
                                                              .format(i, N_feat)

        feature_index[i] = features[i]

    if verbose:
        print "_index_data(): Done indexing features."

    return document_index, feature_index