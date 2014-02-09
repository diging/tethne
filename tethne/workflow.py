"""
Methods for network analysis.
"""

from tethne.data import DataCollection, GraphCollection
from tethne.builders import graphCollectionBuilder
import tethne.analyze as az

# [#60463184]
def closeness_introgression(papers, node, window_size, normalize = False):
    """
    Analyzes the global closeness centrality of a node over time.

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    node : any
        Handle of the node to analyze.
    window_size : int
        Size of time-window.
    normalize : bool
        If True, normalizes global closeness centrality for each year against
        the average closeness centrality for that year. This will require
        substantially more processing time, and values will usually be >> 0.

    Returns
    -------
    trajectory : dict
        Global closeness centrality for node over specified period.

    """

    D = DataCollection(papers)
    D.slice('date', 'time_window', window_size=window_size)
    builder = authorCollectionBuilder(D)
    C = builder.build('date', 'coauthors')
    trajectory = az.collection.node_global_closeness_centrality(C, node)
    
    return trajectory