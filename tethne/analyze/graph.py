"""
Methods for network analysis.
"""

import networkx as nx
import tethne.networks as nt

def node_global_closeness_centrality(g, node, normalize=True):
    """
    Calculates the global closeness centrality of a single node in the network.
    For connected graphs, equivalent to conventional betweenness centrality.
    For disconnected graphs, works around infinite path lengths between nodes
    in different components.

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

    g = nt.authors.coauthors(slice)
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
    Calculates global closeness centrality for all nodes in the network. For
    connected graphs, equivalent to conventional betweenness centrality. For
    disconnected graphs, works around infinite path lengths between nodes in
    different components.

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
