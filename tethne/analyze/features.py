"""
Methods for analyzing featuresets.

.. autosummary::
   :nosignatures:
   
   cosine_distance
   cosine_similarity
   distance
   kl_divergence
   
"""

import numpy
from scipy.sparse import coo_matrix
import scipy.spatial as spat

def distance(sa, sb, method, normalize=True, smooth=False):
    """
    Calculate the distance between two sparse feature vectors using a method
    from scipy.spatial.distance.
    
    Supported distance methods:

    ================    ====================
    Method              Documentation
    ================    ====================
    braycurtis          `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.braycurtis.html>`_
    canberra            `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.canberra.html>`_
    chebyshev           `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.chebyshev.html>`_
    cityblock           `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cityblock.html>`_
    correlation         `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.correlation.html>`_
    cosine              `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.cosine.html>`_
    dice                `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.dice.html>`_
    euclidean           `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.euclidean.html>`_
    hamming             `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.hamming.html>`_
    jaccard             `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.jaccard.html>`_
    kulsinski           `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.kulsinski.html>`_
    matching            `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.matching.html>`_
    rogerstanimoto      `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.rogerstanimoto.html>`_
    russellrao          `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.russellrao.html>`_
    sokalmichener       `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.sokalmichener.html>`_
    sokalsneath         `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.sokalsneath.html>`_
    sqeuclidean         `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.sqeuclidean.html>`_
    yule                `scipy.org <http://docs.scipy.org/doc/scipy/reference/generated/scipy.spatial.distance.yule.html>`_
    ================    ====================


    """
    if method not in spat.distance.__dict__:
        raise RuntimeError('No method named {0} in scipy.spatial.distance'
                                                                .format(method))
    
    # Convert sparse data into dense arrays.
    amax = max(zip(*sa)[0])
    bmax = max(zip(*sb)[0])
    adense = _sparse_to_array(sa, size=max(amax, bmax)+1)
    bdense = _sparse_to_array(sb, size=max(amax, bmax)+1)
    
    if normalize:
        adense = numpy.array(adense/float(numpy.sum(adense)))
        bdense = numpy.array(bdense/float(numpy.sum(bdense)))

    if smooth:
        # Smooth according to Bigi 2003.
        Ndiff = _shared_features(adense, bdense)
        adense, bdense = _smooth(adense, bdense, Ndiff)

    return spat.distance.__dict__[method](adense, bdense)

def kl_divergence(sa, sb):
    """
    Calculate Kullback-Leibler Distance for sparse feature vectors.
    
    """
    # Convert sparse data into dense arrays.
    adense = _sparse_to_array(sa)
    bdense = _sparse_to_array(sb, size=adense.size)
 
    # Find shared features.
    Ndiff = _shared_features(adense, bdense)
    
    # aprob and bprob should each sum to 1.0
    aprob = numpy.array(adense/float(numpy.sum(adense)))
    bprob = numpy.array(bdense/float(numpy.sum(bdense)))

    # Smooth according to Bigi 2003.
    aprob, bprob = _smooth(aprob, bprob, Ndiff)

    return numpy.sum( (aprob - bprob) * numpy.log(aprob/bprob) )

def cosine_distance(sa, sb):
    """
    Calculate cosine distance for sparse feature vectors.
    """
    # Convert sparse data into dense arrays.
    amax = max(zip(*sa)[0])
    bmax = max(zip(*sb)[0])
    adense = _sparse_to_array(sa, size=max(amax, bmax)+1)
    bdense = _sparse_to_array(sb, size=max(amax, bmax)+1)

    from scipy.spatial.distance import cosine
    return cosine(adense, bdense)

def cosine_similarity(sa, sb):
    """
    """

    return -1.*(cosine_distance(sa, sb) - 1.)

def _sparse_to_coo(svect, size=None):
    """
    Convert a sparse feature [(i,v),] to a SciPy COO sparse matrix.
    """
    svect = [ (t,v) for t,v in svect if v != 0 ]
    JK = zip(*svect)
    J = list(JK[0])
    K = list(JK[1])
    I = [0]*len(J)
    
    # Adding a null value with an index of size-1 makes it easier to work with
    #  arrays of different size.
    if size is not None:
        I.append(0)
        J.append(size-1)
        K.append(0)
    coo = coo_matrix((K, (I,J)), shape=(1, max(J)+1))
    return coo

def _sparse_to_array(coo, size=None):
    """
    Convert a sparse feature [(i,v),] to a vector array.
    """
    dense = _sparse_to_coo(coo, size=size).todense()
    l = dense.shape[1]
    return dense.reshape((l,))

def _shared_features(adense, bdense):
    """
    Number of features in ``adense`` that are also in ``bdense``.
    """
    a_indices = set(numpy.nonzero(adense)[0])
    b_indices = set(numpy.nonzero(bdense)[0])  
    
    shared = list(a_indices & b_indices)
    diff = list(a_indices - b_indices) 
    Ndiff = len(diff) 
    
    return Ndiff

def _smoothing_parameters(aprob, bprob, Ndiff):
    min_a = numpy.min(aprob[numpy.nonzero(aprob)])
    sum_a = numpy.sum(aprob)    
    min_b = numpy.min(bprob[numpy.nonzero(bprob)])
    sum_b = numpy.sum(bprob)
    
    epsilon = min((min_a/sum_a), (min_b/sum_b)) * 0.001
    gamma = 1 - Ndiff * epsilon   
    
    return gamma, epsilon

def _smooth(aprob, bprob, Ndiff):
    """
    Smooth distributions for KL-divergence according to `Bigi 2003
    <http://link.springer.com/chapter/10.1007%2F3-540-36618-0_22?LI=true>`_.
    """
    gamma, epsilon = _smoothing_parameters(aprob, bprob, Ndiff)

    # Remove zeros.
    in_a = numpy.nonzero(aprob)  # Use these indices only.
    aprob = aprob[in_a]
    bprob = bprob[in_a]*gamma
    
    # Replace zero values with epsilon.
    numpy.place(bprob, bprob == 0., (epsilon,))
    
    return aprob, bprob