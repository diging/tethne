"""
Methods for network analysis.
"""

import tethne.analyze.graph as g #changed by Ramki

# Pylint Warnings.
#import networkx as nx
#import tethne.networks as nt
#import tethne.data as ds

# [#60463184]
def closeness_introgression(papers, node, start, end, chunk, normalize = False):
    """
    Analyzes the global closeness centrality of a node over time.

    Parameters
    ----------
    papers : list
        A list of :class:`Paper` instances.
    node : any
        Handle of the node to analyze.
    start : int
        Year to start analysis.
    end : int
        Start year of final time-window.
    chunk : int
        Size of time-window.
    normalize : bool
        If True, normalizes global closeness centrality for each year against
        the average closeness centrality for that year. This will require
        substantially more processing time, and values will usually be >> 0.

    Returns
    -------
    trajectory : list
        Global closeness centrality for node over specified period.

    """

    trajectory = []
    for i in xrange(start, end):
        papers_slice = [ m for m in papers if i <= m['date'] < i+chunk ]
        trajectory.append(graph.node_global_closeness_centrality(g, node))
    return trajectory
