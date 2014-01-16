"""
This module provides methods for analyzing :class:`.GraphCollection` objects,
conventionally denoted as **C**. In large part, these methods simply provide
systematic access to algorithms in NetworkX.
"""

import networkx as nx
import types

def algorithm(C, method, **kwargs):
    """
    Passes kwargs to specified NetworkX method for each Graph, and returns
    a dictionary of results as:

    results
        | elem (node or edge)
            | graph index (e.g. year)

    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to analyze. The specified method will be
        applied to each :class:`graph` in **C**.
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

        import tethne.data as ds
        import tethne.analyze as az
        import numpy as np
        collection = ds.GraphCollection()
        N = 100
        for graph_index in xrange(1999, 2004):
            d = np.random.random((N, N))
            g = nx.Graph()
            for i in xrange(N):
                for j in xrange(i+1, N):
                    if d[i, j] > 0.8:
                        g.add_edge(i, j)
            collection.graphs[graph_index] = g

        results = az.collection.algorithm(collection, 'betweenness_centrality',
                                          k=None)
        print results[0]

    Should produce something like:

    .. code-block:: text

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
        applied to each :class:`graph` in **C**.
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

        import tethne.data as ds
        import tethne.analyze as az
        import numpy as np
        collection = ds.GraphCollection()
        N = 100
        for graph_index in xrange(1999, 2004):
            d = np.random.random((N, N))
            g = nx.Graph()
            for i in xrange(N):
                for j in xrange(i+1, N):
                    if d[i, j] > 0.8:
                        g.add_edge(i, j)
            collection.graphs[graph_index] = g

        results = az.collection.connected('connected', k=None)
        print results

    Should produce something like:

    .. code-block:: text

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
