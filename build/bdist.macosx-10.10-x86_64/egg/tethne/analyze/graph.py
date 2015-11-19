"""
Methods for network analysis.

.. autosummary::
   :nosignatures:
   
   global_closeness_centrality
   
"""

import networkx as nx

def global_closeness_centrality(g, node=None, normalize=True):
    """
    Calculates global closeness centrality for one or all nodes in the network.

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

    if not node:
        C = {}
        for node in g.nodes():
            C[node] = global_closeness_centrality(g, node, normalize=normalize)
        return C

    values = nx.shortest_path_length(g, node).values()
    c = sum([1./pl for pl in values if pl != 0.]) / len(g)

    if normalize:
        ac = 0
        for sg in nx.connected_component_subgraphs(g):
            if len(sg.nodes()) > 1:
                aspl = nx.average_shortest_path_length(sg)
                ac += (1./aspl) * (float(len(sg)) / float(len(g))**2 )
        c = c/ac

    return c
