"""
Methods for analyzing :class:`.GraphCollection` objects.

For the most part, these methods simply provide systematic access to algorithms
in NetworkX.
"""

import networkx as nx
import types
import graph

def algorithm(C, method, **kwargs):
    """
    Apply NetworkX method to each ``Graph`` in :class:`.GraphCollection`\.

    Passes kwargs to specified NetworkX method for each Graph, and returns
    a dictionary of results indexed by element (node or edge) and graph index
    (e.g. ``date``).

    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each :class:`.Graph` in **C**.
    method : string
        Name of a method in NetworkX to execute on graph collection.
    **kwargs
        A list of keyword arguments that should correspond to the parameters
        of the specified method.

    Returns
    -------
    results : dict
        A nested dictionary of results: results/elem(node or edge)/graph
        index.

    Raises
    ------
    ValueError
        If name is not in networkx, or if no such method exists.

    Examples
    --------

    *Betweenness centrality:*

    .. code-block:: python

       >>> import tethne.analyze as az
       >>> BC = az.collection.algorithm(C, 'betweenness_centrality')
       >>> print BC[0]
       {1999: 0.010101651117889644,
       2000: 0.0008689093723107329,
       2001: 0.010504898852426189,
       2002: 0.009338654511194512,
       2003: 0.007519105636349891}

    """

    results = {}

    if not method in nx.__dict__:
        raise(ValueError("No such name in networkx."))
    else:
        if type(nx.__dict__[method]) is not types.FunctionType:
            raise(ValueError("No such method in networkx."))
        else:
            for k, G in C.graphs.iteritems():
                r = nx.__dict__[method](G, **kwargs)
                for elem, value in r.iteritems():
                    try:
                        results[elem][k] = value
                    except KeyError:
                        results[elem] = { k: value }
                nx.set_node_attributes(G, method, r)    # [#61510128]
    return results

def connected(C, method, **kwargs):
    """
    Performs analysis methods from networkx.connected on each graph in the
    collection.

    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each :class:`.Graph` in **C**.
    method : string
        Name of method in networkx.connected.
    **kwargs : kwargs
        Keyword arguments, passed directly to method.

    Returns
    -------
    results : dictionary
        Keys are graph indices, values are output of method for that graph.

    Raises
    ------
    ValueError
        If name is not in networkx.connected, or if no such method exists.

    Examples
    --------

    .. code-block:: python

        >>> import tethne.data as ds
        >>> import tethne.analyze as az
        >>> import networkx as nx
        >>> C = ds.GraphCollection()
        >>> # Generate some random graphs
        >>> for graph_index in xrange(1999, 2004):
        >>>     g = nx.random_regular_graph(4, 100)
        >>>     C[graph_index] = g
        >>> results = az.collection.connected(C, 'connected', k=None)
        >>> print results
        {1999: False,
        2000: False,
        2001: False,
        2002: False,
        2003: False }

    """

    results = {}

    if not method in nx.connected.__dict__:
        raise(ValueError("No such name in networkx.connected."))
    else:
        if type(nx.connected.__dict__[method]) is not types.FunctionType:
            raise(ValueError("No such method in networkx.connected."))
        else:
            for k, G in C.graphs.iteritems():
                results[k] = nx.connected.__dict__[method](G, **kwargs)
    return results

def node_history(C, node, attribute, verbose=False):
    """
    Returns a dictionary of attribute values for each Graph in C for a single
    node.

    Parameters
    ----------
    C : :class:`.GraphCollection`
    node : str
        The node of interest.
    attribute : str
        The attribute of interest; e.g. 'betweenness_centrality'
    verbose : bool
        If True, prints status and debug messages.

    Returns
    -------
    history : dict
        Keys are Graph keys in C; values are attribute values for node.
    """

    history = {}

    for k,G in C.graphs.iteritems():
        asdict = { v[0]:v[1] for v in G.nodes(data=True) }
        try:
            history[k] = asdict[node][attribute]
        except KeyError:
            if verbose: print "No such node or attribute in Graph " + str(k)

    return history

def edge_history(C, source, target, attribute, verbose=False):
    """
    Returns a dictionary of attribute vales for each Graph in C for a single
    edge.

    Parameters
    ----------
    C : :class:`.GraphCollection`
    source : str
        Identifier for source node.
    target : str
        Identifier for target node.
    attribute : str
        The attribute of interest; e.g. 'betweenness_centrality'
    verbose : bool
        If True, prints status and debug messages.

    Returns
    -------
    history : dict
        Keys are Graph keys in C; values are attribute values for edge.
    """

    history = {}

    for k,G in C.graphs.iteritems():
        try:
            attributes = G[source][target]
            try:
                history[k] = attributes[attribute]
            except KeyError:
                if verbose: print "No such attribute for edge in Graph " \
                                    + str(k)
        except KeyError:
            if verbose: print "No such edge in Graph " + str(k)

    return history

def node_global_closeness_centrality(C, node):
    """
    Calculates global closeness centrality for node in each graph in
    :class:`.GraphCollection` C.

    """

    results = {}
    for key, g in C.graphs.iteritems():
        results[key] = graph.node_global_closeness_centrality(g, node)

    return results
    
def attachment_probability(C):
    """
    Calculates the observed attachment probability for each node at each
    time-step.
    """
    
    probs = {}
    G_ = None
    for k,G in C.graphs.iteritems():
        print k
        new_edges = {}
        print len(G.nodes())
        if G_ is not None: 
            for n in G.nodes():
                try:
                    old_neighbors = set(G_[n].keys())
                    new_neighbors = set(G[n].keys()) - old_neighbors
                    new_edges[n] = float(len(new_neighbors))
                except KeyError:
                    pass
                    
        N = sum( new_edges.values() )
        if N > 0.:
            probs[k] = { k:v/N for k,v in new_edges.iteritems() }
        else:
            probs[k] = None
        if probs[k] is not None:
            nx.set_node_attributes(C.graphs[k], 'attachment', probs[k])
        G_ = G
    return C, probs


if __name__ == '__main__':

    import tethne.readers as rd
    from tethne.data import DataCollection
    from tethne.builders import authorCollectionBuilder
    import tethne.writers as wr
    
    papers = rd.wos.read("/Users/erickpeirson/Dropbox/Research/Phenotypic Plasticity/Web of Science/20110219_WoS_full record/download1.txt")
    
    D = DataCollection(papers)
    D.slice('date', method='time_period', cumulative=True)
    
    builder = authorCollectionBuilder(D)
    C = builder.build('date', 'coauthors')
    C, probs = attachment_probability(C)
    
    wr.collection.to_dxgmml(C, '/Users/erickpeirson/Desktop/test.xgmml')