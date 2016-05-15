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

def algorithm(G, method_name, **kwargs):
    """
    Apply a ``method`` from NetworkX to all ``networkx.Graph`` objects in the
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


def attachment_probability(G):
    """
    Calculates the observed attachment probability for each node at each
    time-step.
    
    
    Attachment probability is calculated based on the observed new edges in the
    next time-step. So if a node acquires new edges at time t, this will accrue
    to the node's attachment probability at time t-1. Thus at a given time,
    one can ask whether degree and attachment probability are related.

    Parameters
    ----------
    G : :class:`.GraphCollection`
        Must be sliced by 'date'. See :func:`.GraphCollection.slice`\.
    
    Returns
    -------
    probs : dict
        Keyed by index in G.graphs, and then by node.
    """
    warnings.warn("Removed in 0.8. Too domain-specific.")

    probs = {}
    G_ = None
    k_ = None
    for k,g in G.graphs.iteritems():
        new_edges = {}
        if G_ is not None: 
            for n in g.nodes():
                try:
                    old_neighbors = set(G_[n].keys())
                    if len(old_neighbors) > 0:
                        new_neighbors = set(g[n].keys()) - old_neighbors
                        new_edges[n] = float(len(new_neighbors))
                    else:
                        new_edges[n] = 0.
                except KeyError:
                    pass
    
            N = sum( new_edges.values() )
            probs[k_] = { n:0. for n in G_.nodes() }
            if N > 0.:
                for n in G.nodes():
                    try:
                        probs[k_][n] = new_edges[n]/N
                    except KeyError:
                        pass

            if probs[k_] is not None:
                networkx.set_node_attributes(G.graphs[k_],
                                             'attachment_probability',
                                             probs[k_])
    
        G_ = G
        k_ = k

    # Handle last graph (no values).
    key = G.graphs.keys()[-1]
    zprobs = { n:0. for n in G.graphs[key].nodes() }
    networkx.set_node_attributes(G.graphs[key], 'attachment_probability', zprobs)

    return probs
