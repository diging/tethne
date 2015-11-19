"""
Methods for analyzing featuresets.

.. autosummary::
   :nosignatures:

   cosine_distance
   cosine_similarity
   distance
   kl_divergence

"""

from math import sqrt, log, acos, pi
from tethne.utilities import nonzero


def kl_divergence(V_a, V_b):
    """
    Calculate Kullback-Leibler distance.

    Uses the smoothing method described in `Bigi 2003
    <http://lvk.cs.msu.su/~bruzz/articles/classification/Using%20Kullback-Leibler%20Distance%20for%20Text%20Categorization.pdf>`_
    to facilitate better comparisons between vectors describing wordcounts.

    Parameters
    ----------
    V_a : list
    V_b : list

    Returns
    -------
    divergence : float
        KL divergence.
    """

    # Find shared features.
    Ndiff = _shared_features(V_a, V_b)

    # aprob and bprob should each sum to 1.0
    aprob = map(lambda v: float(v)/sum(V_a), V_a)
    bprob = map(lambda v: float(v)/sum(V_b), V_b)

    # Smooth according to Bigi 2003.
    aprob, bprob = _smooth(aprob, bprob, Ndiff)

    return sum(map(lambda a, b: (a-b)*log(a/b), aprob, bprob))

def cosine_similarity(F_a, F_b):
    """
    Calculate `cosine similarity
    <http://en.wikipedia.org/wiki/Cosine_similarity>`_ for sparse feature
    vectors.

    Parameters
    ----------
    F_a : :class:`.Feature`
    F_b : :class:`.Feature`

    Returns
    -------
    similarity : float
        Cosine similarity.
    """

    shared = list(F_a.unique & F_b.unique)
    A = [dict(F_a.norm)[i] for i in shared]
    B = [dict(F_b.norm)[i] for i in shared]
    dot = sum(map(lambda a, b: a*b, A, B))
    mag_A = sqrt(sum(map(lambda a: a**2, A)))
    mag_B = sqrt(sum(map(lambda a: a**2, B)))

    return dot / (mag_A + mag_B)

def angular_similarity(F_a, F_b):
    """
    Calculate the `angular similarity
    <http://en.wikipedia.org/wiki/Cosine_similarity#Angular_similarity>`_ for
    sparse feature vectors.

    Unlike `cosine_similarity`, this is a true distance metric.

    Parameters
    ----------
    F_a : :class:`.Feature`
    F_b : :class:`.Feature`

    Returns
    -------
    similarity : float
        Cosine similarity.
    """
    return 1. - (2. *  acos(cosine_similarity(F_a, F_b))) / pi

### Helpers ###


def _shared_features(adense, bdense):
    """
    Number of features in ``adense`` that are also in ``bdense``.
    """
    a_indices = set(nonzero(adense))
    b_indices = set(nonzero(bdense))

    shared = list(a_indices & b_indices)
    diff = list(a_indices - b_indices)
    Ndiff = len(diff)

    return Ndiff

def _smoothing_parameters(aprob, bprob, Ndiff):
    min_a = min(list([list(aprob)[i] for i in nonzero(aprob)]))
    sum_a = sum(aprob)
    min_b = min(list([list(bprob)[i] for i in nonzero(bprob)]))
    sum_b = sum(bprob)

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
    in_a = [i for i,v in enumerate(aprob) if abs(v) > 0.0]
    aprob = list([list(aprob)[i] for i in in_a])
    bprob = list([list(bprob)[i]*gamma for i in in_a])

    # Replace zero values with epsilon.
    bprob = list(map(lambda v: v if v != 0. else epsilon, bprob))

    return aprob, bprob
