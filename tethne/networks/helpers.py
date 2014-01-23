"""Methods which provide helper functions for generating networks """

import networkx as nx
#import tethne.utilities as util  # Pylint Warnings
#import tethne.data as ds

def simplify_multigraph(multigraph, time=False):
    """
    Simplifies a graph by condensing multiple edges between the same node pair
    into a single edge, with a weight attribute equal to the number of edges.

    Parameters
    ----------
    graph : networkx.MultiGraph
        E.g. a coauthorship graph.
    time : bool
        If True, will generate 'start' and 'end' attributes for each edge,
        corresponding to the earliest and latest 'date' values for that edge.

    Returns
    -------
    graph : networkx.Graph
        A NetworkX :class:`.graph` .

    """

    graph = nx.Graph()

    for node in multigraph.nodes(data=True):
        u = node[0]
        node_attribs = node[1]
        graph.add_node(u, node_attribs)


        for v in multigraph[u]:
            edges = multigraph.get_edge_data(u, v) # Dict.

            edge_attribs = { 'weight': len(edges) }

            if time:    # Look for a date in each edge.
                start = 3000
                end = 0
                found_date = False
                for edge in edges.values():
                    try:
                        found_date = True
                        if edge['date'] < start:
                            start = edge['date']
                        if edge['date'] > end:
                            end = edge['date']
                    except KeyError:    # No date to be found.
                        pass

                if found_date:  # If no date found, don't add start/end atts.
                    edge_attribs['start'] = start
                    edge_attribs['end'] = end

            graph.add_edge(u, v, edge_attribs)

    return graph



