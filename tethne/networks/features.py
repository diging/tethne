"""
Methods for building networks from terms in bibliographic records. This
includes keywords, abstract terms, etc.

.. autosummary::
   :nosignatures:

   cooccurrence
   mutual_information
   keyword_cooccurrence
   topic_coupling

"""

from math import log
import networkx as nx
import warnings

from tethne.networks.base import cooccurrence, coupling, multipartite

def _nPMI(p_ij, p_i, p_j):
    lower = (-1.*log(p_ij))
    joint = (p_i*p_j)
    if lower == 0. or joint == 0.:
        return 0.
    return (log(p_ij/joint))/(-1.*log(p_ij))


def feature_cooccurrence(corpus, featureset_name, min_weight=1,
                         filter=lambda f, v, c, dc: True):
    return cooccurrence(corpus, featureset_name, min_weight=min_weight,
                        filter=filter)


def mutual_information(corpus, featureset_name, min_weight=0.9,
                       filter=lambda f, v, c, dc: True):
    """
    Generates a graph of features in ``featureset`` based on normalized
    `pointwise mutual information (nPMI)
    <http://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.

    .. math::

       nPMI(i,j)=\\frac{log(\\frac{p_{ij}}{p_i*p_j})}{-1*log(p_{ij})}

    ...where :math:`p_i` and :math:`p_j` are the probabilities that features
    *i* and *j* will occur in a document (independently), and :math:`p_{ij}` is
    the probability that those two features will occur in the same document.
    """

    graph = feature_cooccurrence(corpus, featureset_name, min_weight=1,
                                 filter=filter)
    mgraph = type(graph)()
    keep_nodes = set()

    fset = corpus.features[featureset_name]
    for s, t, attrs in graph.edges(data=True):
        p_ij = float(attrs['weight'])/len(corpus.papers)
        p_i = float(fset.documentCounts[fset.lookup[s]])/len(corpus.papers)
        p_j = float(fset.documentCounts[fset.lookup[t]])/len(corpus.papers)
        MI = _nPMI(p_ij, p_i, p_j)
        if MI >= min_weight:
            mgraph.add_edge(s, t, nPMI=MI, **attrs)
            keep_nodes.add(s)
            keep_nodes.add(t)

    for n in list(keep_nodes):  # Retain node attributes.
        mgraph.node[n].update(graph.node[n])

    return mgraph

def keyword_cooccurrence(corpus, min_weight=1, filter=lambda f, v, c, dc: True):
    warnings.warn('keyword_cooccurrence will be removed in v0.8. Use ' +
                  'feature_cooccurrence with "authorKeywords" or '+
                  '"keywordsPlus" instead.', DeprecationWarning)
    return feature_cooccurrence(corpus, 'authorKeywords',
                                min_weight=min_weight, filter=filter)
