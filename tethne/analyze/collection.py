"""
Methods for analyzing :class:`.GraphCollection`\s.
"""

import networkx
import types
import graph

def algorithm(G, method, **kwargs):
    """
    Apply a ``method`` from NetworkX to all ``networkx.Graph`` objects in the
    :class:`.GraphCollection` ``G``.



    Parameters
    ----------
    G : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each graph in ``G``.
    method : string
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

    results = {}

    if not method in networkx.__dict__:
        raise(ValueError("No such name in networkx."))
    else:
        if type(networkx.__dict__[method]) is not types.FunctionType:
            raise(ValueError("No such method in networkx."))
        else:
            for k, g in G.graphs.iteritems():
                r = networkx.__dict__[method](g, **kwargs)
                for elem, value in r.iteritems():
                    try:
                        results[elem][k] = value
                    except KeyError:
                        results[elem] = { k: value }
                networkx.set_node_attributes(g, method, r)    # [#61510128]
    return results

def delta(G, attribute):
    """
    Updates a :class:`.GraphCollection` with deltas of a node attribute.
    
    Parameters
    ----------
    G : :class:`.GraphCollection`
    attribute : str
        Name of a node attribute in ``G``.
        
    Returns
    -------
    deltas : dict

    """
    import copy

    keys = sorted(G.graphs.keys())
    all_nodes =  G.nodes()
    deltas = { k:{} for k in keys }
    #n:{} for n in all_nodes }
    last = { n:None for n in all_nodes }
    
    for k in keys:
        graph = G[k]
        asdict = { v[0]:v[1] for v in graph.nodes(data=True) }
    
        for n in all_nodes:
            try:
                curr = float(asdict[n][attribute])
                if last[n] is not None and curr is not None:
                    delta = float(curr) - float(last[n])
                    last[n] = float(curr)
                elif last[n] is None and curr is not None:
                    delta = float(curr)
                    last[n] = float(curr)
                else:
                    delta = 0.
                deltas[k][n] = float(delta)
            except KeyError:
                pass
        networkx.set_node_attributes(G[k], attribute+'_delta', deltas[k])

    return deltas

def connected(G, method, **kwargs):
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

    results = {}

    if not method in networkx.connected.__dict__:
        raise(ValueError("No such name in networkx.connected."))
    else:
        if type(networkx.connected.__dict__[method]) is not types.FunctionType:
            raise(ValueError("No such method in networkx.connected."))
        else:
            for k, g in G.graphs.iteritems():
                results[k] = networkx.connected.__dict__[method](g, **kwargs)
    return results

def node_global_closeness_centrality(G, node):
    """
    Calculates global closeness centrality for node in each graph in
    :class:`.GraphCollection` G.

    """

    results = {}
    for key, g in G.graphs.iteritems():
        results[key] = graph.node_global_closeness_centrality(g, node)

    return results
    
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
                networkx.set_node_attributes(G.graphs[k_], 'attachment_probability', probs[k_])
    
        G_ = G
        k_ = k

    # Handle last graph (no values).
    key = G.graphs.keys()[-1]
    zprobs = { n:0. for n in G.graphs[key].nodes() }
    networkx.set_node_attributes(G.graphs[key], 'attachment_probability', zprobs)

    return probs