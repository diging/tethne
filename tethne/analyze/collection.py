"""
Methods for analyzing :class:`.GraphCollection`\s.

.. autosummary::
   :nosignatures:

   algorithm
   attachment_probability
   connected
   delta
   node_global_closeness_centrality

"""

import networkx
import graph
import warnings
from collections import defaultdict, Counter


def algorithm(G, method_name, **kwargs):
    """
    Apply a ``method`` from NetworkX to all :ref:`networkx.Graph <networkx:graph>` objects in the
    :class:`.GraphCollection` ``G``.

    For options, see the `list of algorithms
    <http://networkx.github.io/documentation/networkx-1.9/reference/algorithms.html>`_
    in the NetworkX documentation. Not all of these have been tested.

    Parameters
    ----------
    G : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each graph in ``G``.
    method_name : string
        Name of a method in NetworkX to execute on graph collection.
    **kwargs
        A list of keyword arguments that should correspond to the parameters
        of the specified method.

    Returns
    -------
    results : dict
        Indexed by element (node or edge) and graph index (e.g. ``date``).

    Raises
    ------
    ValueError
        If no such method exists.

    Examples
    --------

    *Betweenness centrality:* (``G`` is a :class:`.GraphCollection`\)

    .. code-block:: python

       >>> from tethne.analyze import collection
       >>> BC = collection.algorithm(G, 'betweenness_centrality')
       >>> print BC[0]
       {1999: 0.010101651117889644,
       2000: 0.0008689093723107329,
       2001: 0.010504898852426189,
       2002: 0.009338654511194512,
       2003: 0.007519105636349891}

    """
    warnings.warn("To be removed in 0.8. Use GraphCollection.analyze instead.",
                  DeprecationWarning)

    return G.analyze(method_name, **kwargs)


def connected(G, method_name, **kwargs):
    """
    Performs analysis methods from networkx.connected on each graph in the
    collection.

    Parameters
    ----------
    G : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each graph in ``G``.
    method : string
        Name of method in networkx.connected.
    **kwargs : kwargs
        Keyword arguments, passed directly to method.

    Returns
    -------
    results : dict
        Keys are graph indices, values are output of method for that graph.

    Raises
    ------
    ValueError
        If name is not in networkx.connected, or if no such method exists.

    """
    warnings.warn("To be removed in 0.8. Use GraphCollection.analyze instead.",
                  DeprecationWarning)

    return G.analyze(['connected', method_name], **kwargs)


def attachment_probability(G, raw=False):
    """
    Calculates the attachment probability for each node at each time-step.

    The attachment probability for a node at a particular graph state ``t`` is
    the probability that the next edge added to the graph will accrue to that
    node. The MLE for attachment probability is thus the observed fraction of
    all new edges in graph state ``t + 1`` that accrue to a particular node.

    Note that values will only be calculated for nodes present in state ``t``.
    In other words, if in ``t + 1`` a new node is introduced who also accrues
    new edges, that node will **not** appear in the results for state ``t``.

    Parameters
    ----------
    G : :class:`.GraphCollection`
    raw : bool
        (default: ``False``) If ``True``, nodes are represented by their
        integer ids in ``G``, rather than their label.

    Returns
    -------
    probs : dict
        Keyed by index in ``G``, and then by node. If ``raw`` is True, node keys
        will be integer indices from the GraphCollection's  ``node_index``.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers.wos import read
       >>> corpus = read("/path/to/my/data")
       >>> from tethne import coauthors, GraphCollection
       >>> collection = GraphCollection(corpus, coauthors)
       >>> from tethne.analyze.collection import attachment_probability
       >>> probs = attachment_probability(collection)

    """

    probs = {}

    keys = sorted(G.keys())
    attach = defaultdict(Counter)
    for i, key in enumerate(keys):
        graph = G[key]

        if i == 0:          # All calculations are retrospective, so we can
            last = G[key]   #  skip the first graph.
            last_key = key
            continue

        for node in graph.nodes():
            if node not in last.node:
                continue
            new = len(set(graph.neighbors(node)) - set(last.neighbors(node)))
            attach[last_key][node] = new

        # The MLE for node attachment probability is the observed fraction of
        #  all new edges in a time-step that accrue to a particular node.
        N = 1. * sum(attach[last_key].values())
        attach[last_key] = dict([
            (node, attach[last_key][node]/N if attach[last_key][node] > 0 else 0.)
            for node in last.nodes()])
        networkx.set_node_attributes(G[last_key],
                                     'attachment_probability',
                                     attach[last_key])

        last = G[key]
        last_key = key

    # Nodes in the last graph have 0 probability, but we want to include this
    #  graph for symmetry with the collection.
    attach[key] = {node: 0. for node in graph.nodes()}
    networkx.set_node_attributes(G[key], 'attachment_probability', attach[key])

    if raw:
        return attach
    return {key: {G.node_index[node]: prob for node, prob in values.iteritems()}
            for key, values in attach.iteritems()}
