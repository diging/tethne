"""
Methods for network analysis.
"""

import networkx as nx
import tethne.networks as nt

def node_global_closeness_centrality(g, node, normalize=True):
    """
    Calculates the global closeness centrality of a single node in the network.

    Closeness centrality is based on the average shortest path length
    between a focal node and all other nodes in the network. For multi-component
    graphs, conventional closeness centrality metrics fail because it is not
    possible to traverse between a given node and all other nodes in the graph.
    Global closeness centrality is calculated in a way that yields values even
    for multi-component graphs. For an example of how global closeness
    centrality can be used to analyze co-authorship networks, see the blog post
    `here <http://devo-evo.lab.asu.edu/node/459>`_.

    To calculate the global closeness centrality of a single node, try:

    .. code-block:: python

       >>> import tethne.analyze as az
       >>> ngbc = az.node_global_closeness_centrality(BC, 'LEE 1975 EVOLUTION')
       >>> ngbc
       0.154245

    You can calculate the global closeness centrality of all nodes in the
    network using :func:`.global_closeness_centrality` .

    .. code-block:: python

       >>> GBC = az.global_closeness_centrality(BC)
       >>> GBC
       {'a': 0.0, 'c': 0.0, 'b': 0.6666666666666666, 'd': 0.0}

    For connected graphs, this is equivalent to conventional betweenness
    centrality. For disconnected graphs, works around infinite path lengths
    between nodes in different components.

    Parameters
    ----------
    g : networkx.Graph
    node : any
        Identifier of node of interest in g.
    normalize : boolean
        If True, normalizes centrality based on the average shortest path
        length. Default is True.

    Returns
    -------
    c : float
        Global closeness centrality of node.
    """

    c = 0
    try:
        for pl in nx.shortest_path_length(g, node).values():
            if pl != 0:     # Ignore self-loops.
                c += 1/float(pl)
        c = c/len(g)
    except ZeroDivisionError:
        c = 0.

    if normalize:
        ac = 0
        for sg in nx.connected_component_subgraphs(g):
            if len(sg.nodes()) > 1:
                aspl = nx.average_shortest_path_length(sg)
                ac += (1/aspl) * (float(len(sg)) / float(len(g))**2 )
        c = c/ac

    return c

def global_closeness_centrality(g, normalize=True):
    """
    Calculates global closeness centrality for all nodes in the network.

    See :func:`.node_global_closeness_centrality` for more information.

    Parameters
    ----------
    g : networkx.Graph
    normalize : boolean
        If True, normalizes centrality based on the average shortest path
        length. Default is True.

    Returns
    -------
    C : dict
        Dictionary of results, with node identifiers as keys and gcc as values.
    """

    C = {}
    for node in g.nodes():
        C[node] = node_global_closeness_centrality(g, node, normalize=normalize)

    return C
