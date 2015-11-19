"""
Build networks from topics in a topic model.
"""

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

import networkx
#from scipy import stats
import numpy

import sys
if sys.version_info[0] > 2:
    xrange = range

from ..analyze import features
from tethne.networks.base import cooccurrence, coupling


def terms(model, threshold=0.01):
    """
    Two terms are coupled if they belong to the same topic with phi > threshold.
    """
    select = lambda f, v, c, dc: v > threshold
    graph = cooccurrence(model.phi, filter=select)

    # Only include labels for terms that are actually in the graph.
    label_map = {k: v for k, v in model.vocabulary.items()
                 if k in graph.nodes()}
    # print label_map

    return networkx.relabel_nodes(graph, label_map)


def topic_coupling(model, threshold=None):
    """
    Two papers are coupled if they both contain a shared topic above threshold.
    """
    if not threshold:
        threshold = 3./model.Z
    select = lambda f, v, c, dc: v > threshold
    return coupling(model.corpus, 'topics', filter=select)


def cotopics(model, threshold=None):
    """
    Two topics are coupled if they occur in the same documents.
    """
    if not threshold:
        threshold = 2./model.Z

    select = lambda f, v, c, dc: v > threshold
    return cooccurrence(model.corpus, 'topics', filter=select)


def distance(model, method='cosine', percentile=90, bidirectional=False,
             normalize=True, smooth=False, transform='log'):
    """
    Generate a network of :class:`.Paper`\s based on a distance metric from
    `scipy.spatial.distance
    <http://docs.scipy.org/doc/scipy/reference/spatial.distance.html>`_
    using :ref:`sparse-feature-vector`\s over the dimensions in ``model``.

    Refer to the documentation for :func:`.analyze.features.distance` for
    a list of distance statistics. The only two methods that will not work
    in this context are ``hamming`` and ``jaccard``.

    Distances are inverted to a similarity metric, which is log-transformed by
    default (see ``transform`` parameter, below). Edges are included if they are
    at or above the ``percentile``th percentile.

    Parameters
    ----------
    model : :class:`.LDAModel` or :class:`.DTMModel`
        :func:`.distance` uses ``model.item`` and ``model.metadata``.
    method : str
        Name of a distance method from `scipy.spatial.distance
        <http://docs.scipy.org/doc/scipy/reference/spatial.distance.html>`_.
        See :func:`.analyze.features.distance` for a list of distance
        statistics. ``hamming`` or ``jaccard`` will raise a RuntimeError.
        :func:`.analyze.features.kl_divergence` is also available as
        'kl_divergence'.
    percentile : int
        (default: 90) Edges are included if they are at or above the
        ``percentile`` for all distances in the ``model``.
    bidirectional : bool
        (default: False) If True, ``method`` is calculated twice for each pair
        of :class:`.Paper`\s ( ``(i,j)`` and ``(j,i)`` ), and the mean is used.
    normalize : bool
        (default: True) If True, vectors over topics are normalized so that they
        sum to 1.0 for each :class:`.Paper`.
    smooth : bool
        (default: False) If True, vectors over topics are smoothed according to
        `Bigi 2003
        <http://lvk.cs.msu.su/~bruzz/articles/classification/Using%20Kullback-Leibler%20Distance%20for%20Text%20Categorization.pdf>`_.
        This may be useful if vectors over topics are very sparse.
    transform : str
        (default: 'log') Transformation to apply to similarity values before
        building the graph. So far only 'log' and None are supported.

    Returns
    -------
    thegraph : networkx.Graph
        Similarity values are included as edge weights. Node attributes are set
        using the fields in ``model.metadata``.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.networks import topics
       >>> thegraph = topics.distance(MyLDAModel, 'cosine')

       >>> from tethne.writers import graph
       >>> graph.to_graphml(thegraph, '~./thegraph.graphml')

    .. figure:: _static/images/lda_cosine_network.png
       :width: 80%

       Edge weight and opacity indicate similarity. Node color indicates the
       journal in which each :class:`.Paper` was published. In this graph,
       papers published in the same journal tend to cluster together.

    """

    if method in ['hamming','jaccard']:
        raise RuntimeError(
            'There is no sensicle interpretation of {0} for these data.'
                                                            .format(method))

    thegraph = networkx.Graph()

    edges = {}
    for i in xrange(model.M):
        for j in xrange(i+1, model.M):
            if method == 'kl_divergence':   # Not a SciPy method.
                dist = features.kl_divergence( model.item(i), model.item(j) )
                dist_ = features.kl_divergence( model.item(j), model.item(i) )
                dist = (dist + dist_)/2.
            else:
                dist = features.distance( model.item(i), model.item(j), method,
                                          normalize=normalize, smooth=smooth  )

            if bidirectional:
                dist_ = features.distance(
                            model.item(j), model.item(i), method,
                            normalize=normalize, smooth=smooth  )

                dist = (dist + dist_)/2.

            sim = 1./dist

            if transform == 'log':
                sim = numpy.log(sim)

            edges[(i,j)] = sim

    pct = numpy.percentile(edges.values(), percentile)
    for edge, sim in edges.items():
        if sim >= pct:
            thegraph.add_edge(edge[0], edge[1], weight=float(sim))

    for key in model.metadata[0].keys():
        values = { k:v[key] for k,v in model.metadata.items()
                                if k in thegraph.nodes()    }
        networkx.set_node_attributes(thegraph, key, values)

    return thegraph

#def paper_coupling(model, threshold=0.1):
#    """
#    """
#
#    D = model.doc_topic.shape[0]
#    Z = model.doc_topic.shape[1]
#
#    edges = {}
#    for d in xrange(D):
#        d_s = model.doc_topic[d,:]
#        for i in xrange(Z):
#            for j in xrange(i+1, Z):
#                if d_s[i] >= threshold and d_s[j] >= threshold:
#                    try:
#                        edges[(i,j)].append( (d, d_s[i]*d_s[j]/2) )
#                    except KeyError:
#                        edges[(i,j)] = [(d, d_s[i]*d_s[j]/2)]
#
#    pc = nx.Graph()
#
#    for e, papers in edges.items():
#        weight = sum( [p[1] for p in papers] ) / D
#        pc.add_edge(e[0], e[1], weight=weight, \
#                    papers=[model.metadata[p[0]] for p in papers])
#
#    for t in pc.nodes():
#        pc.node[t]['words'] = model.top_keys[t][1]  # Add list of top words.
#
#    return pc
#
#def term_coupling(model, threshold=0.01):
#    """
#    """
#
#    Z = model.top_word.shape[0]
#    W = model.top_word.shape[1]
#
#    edges = {}
#    for w in xrange(W):
#        t_sub = []
#
#        for z in xrange(Z):
#            if model.top_word[z,w] >= threshold:
#                t_sub.append(z)
#
#        for i in xrange(len(t_sub)):
#            for j in xrange(i+1, len(t_sub)):
#                t_i = t_sub[i]
#                t_j = t_sub[j]
#                p_i = model.top_word[t_i,w]
#                p_j = model.top_word[t_j,w]
#                try:
#                    edges[(t_i,t_j)].append((w, (p_i+p_j)/2))
#                except KeyError:
#                    edges[(t_i,t_j)] = [(w, (p_i+p_j)/2)]
#    tc = nx.Graph()
#
#    #print edges
#
#    for e, words in edges.items():
#        weight = sum( [ w[1] for w in words ] ) / W
#        word_list = [model.vocabulary[w[0]] for w in words]
#        tc.add_edge(e[0], e[1], weight=weight, words=word_list)
#
#    for t in tc.nodes():
#        tc.node[t]['words'] = model.top_keys[t][1]  # Add list of top words.
#
#    return tc
#
#def topic_coupling(model, papers=None, threshold=None):
#    """
#    Builds a network of topics using inverse symmetric KL-divergence on papers.
#
#    If `papers` is not None, uses only those papers provided to calculate
#    KL-divergence.
#
#    Parameters
#    ----------
#    model : :class:`.LDAModel`
#    papers : list
#        A list of paper indices to use in KL-divergence calculation.
#    threshold : float
#        Minimum inverse symmetric KL-divergence for an edge. (default = 0.25)
#    """
#
#    Z = model.top_word.shape[0]
#    G = nx.Graph()
#
#    if threshold is None:
#        # Scaling factor to remove negative correlation between N_d and number
#        # of edges.
#        threshold = len(papers)**-0.2 + 0.1
#
#    if papers is None:
#        dt_matrix = model.doc_topic
#    else:
#        N_d = len(papers)
#        dt_matrix = np.zeros((N_d, Z))
#        for d in xrange(N_d):
#            dt_matrix[d, :] = model.doc_topic[papers[d], :]
#
#    for i in xrange(Z):
#        for j in xrange(i+1, Z):
#            D_ij = stats.entropy(dt_matrix[:,i], dt_matrix[:,j])
#            D_ji = stats.entropy(dt_matrix[:,j], dt_matrix[:,i])
#            iD_sym = float(1/(D_ij + D_ji))
#
#            if iD_sym >= threshold:
#                G.add_node(j, label=', '.join(model.top_keys[i][1]))
#                G.add_edge(i,j,weight=iD_sym)
#
#    return G
