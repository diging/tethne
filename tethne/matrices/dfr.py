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
    
    if verbose: 
        print "array(): %c documents, %c features".format(N_docs, N_feat)
                        
    A = np.zeros((N_docs, N_feat))
    d = 0
    
    for doc, features in data.iteritems():
        if verbose:
            d += 1
            if d%100 == 0:
                print "array(): Processed %c of %c documents".format(d, N_docs)
                
        i = document_index[doc]
        for f, v in features:
            j = feature_index[f]
            A[i, j] = v
    
    if verbose:
        print "array(): Processed all documents."
    
    if normalize:
        if verbose:
            print "array(): Normalizing."
        A = A / np.max(A)

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

    A, document_index, feature_index = array(data, normalize, verbose)
    M = np.matrix(A)
    
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
        print "_index_data(): Indexing %c documents".format(N_docs)
    
    features = set()
    for i in xrange(N_docs): # Index documents.
        if verbose and i%100 == 0:
            print "_index_data(): Indexed %c of %c documents".format(i, N_docs)
            
        document_index[i] = data.keys()[i]
        for f,c in data.values()[i]:
            features.add(f) # Build a set of features.

    N_feat = len(features)
    if verbose:
        print "_index_data(): Done indexing documents."
        print "_index_data(): Indexing %c features.".format(N_feat)
    
    features = list(features)
    for i in xrange(N_feat):  # Index features.
        if verbose and i %100 == 0:
            print "_index_data(): Indexed %c of %c features.".format(i, N_feat)
            
        feature_index[i] = features[i]
    
    if verbose:
        print "_index_data(): Done indexing features."
    
    return document_index, feature_index
    
if __name__ == '__main__':
    import tethne.readers as rd
    
    path = "/Users/erickpeirson/Downloads/DfR/ecology_1960-64"
#    papers = read(path)
    bigrams = rd.dfr.ngrams(path)

    print len(bigrams)
    
    M = matrix(bigrams, verbose=True)
    print M