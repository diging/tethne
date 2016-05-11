"""
Build networks from topics in a topic model.
"""

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

import networkx
from math import log

import sys
if sys.version_info[0] > 2:
    xrange = range

from tethne.analyze import features
from tethne.networks.base import cooccurrence, coupling
from tethne.utilities import argsort


def terms(model, threshold=0.01, **kwargs):
    """
    Two terms are coupled if they belong to the same topic with phi > threshold.
    """
    select = lambda f, v, c, dc: v > threshold
    graph = cooccurrence(model.phi, filter=select, **kwargs)

    # Only include labels for terms that are actually in the graph.
    label_map = {k: v for k, v in model.vocabulary.items()
                 if k in graph.nodes()}
    graph.name = ''
    return networkx.relabel_nodes(graph, label_map)


def topic_coupling(model, threshold=None, **kwargs):
    """
    Two papers are coupled if they both contain a shared topic above threshold.
    """
    if not threshold:
        threshold = 3./model.Z
    select = lambda f, v, c, dc: v > threshold

    graph = coupling(model.corpus, 'topics', filter=select, **kwargs)
    graph.name = ''
    return graph


def cotopics(model, threshold=None, **kwargs):
    """
    Two topics are coupled if they occur in the same documents.
    """
    if not threshold:
        threshold = 2./model.Z

    select = lambda f, v, c, dc: v > threshold
    return cooccurrence(model.corpus, 'topics', filter=select, **kwargs)


def distance(model, method='cosine', percentile=90, bidirectional=False,
             normalize=True, smooth=False, transform='log', **kwargs):
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
                sim = log(sim)

            edges[(i,j)] = sim

    # pct = numpy.percentile(edges.values(), percentile)
    pct = int(round(len(edges)*(percentile/100.)))
    for i in argsort(edges.values())[::-1][:pct]:
        edge, sim = edges.keys()[i], edges.values()[i]
        thegraph.add_edge(edge[0], edge[1], weight=float(sim))

    for key in model.metadata[0].keys():
        values = { k:v[key] for k,v in model.metadata.items()
                                if k in thegraph.nodes()    }
        networkx.set_node_attributes(thegraph, key, values)

    return thegraph
