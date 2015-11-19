"""
Helper functions for generating networks.

.. autosummary::
   :nosignatures:

   citation_count
   simplify_multigraph
   top_cited
   top_parents

"""

import networkx as nx
import operator
import numpy as np
#import tethne.utilities as util  # Pylint Warnings
#import tethne.data as ds

from collections import Counter

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


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

def citation_count(papers, key='ayjid', verbose=False):
    """
    Generates citation counts for all of the papers cited by papers.

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    key : str
        Property to use as node key. Default is 'ayjid' (recommended).
    verbose : bool
        If True, prints status messages.

    Returns
    -------
    counts : dict
        Citation counts for all papers cited by papers.
    """

    if verbose:
        print "Generating citation counts for "+unicode(len(papers))+" papers..."

    counts = Counter()
    for P in papers:
        if P['citations'] is not None:
            for p in P['citations']:
                counts[p[key]] += 1

    return counts

def top_cited(papers, topn=20, verbose=False):
    """
    Generates a list of the topn (or topn%) most cited papers.

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    topn : int or float {0.-1.}
        Number (int) or percentage (float) of top-cited papers to return.
    verbose : bool
        If True, prints status messages.

    Returns
    -------
    top : list
        A list of 'ayjid' keys for the topn most cited papers.
    counts : dict
        Citation counts for all papers cited by papers.
    """

    if verbose:
        print "Finding top "+unicode(topn)+" most cited papers..."

    counts = citation_count(papers, verbose=verbose)

    if type(topn) is int:
        n = topn
    elif type(topn) is float:
        n = int(np.around(topn*len(counts), decimals=-1))
    top = dict(sorted(counts.items(),
                       key=operator.itemgetter(1),
                       reverse=True)[:n]).keys()

    return top, counts

def top_parents(papers, topn=20, verbose=False):
    """
    Returns a list of :class:`.Paper` that cite the topn most cited papers.

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` objects.
    topn : int or float {0.-1.}
        Number (int) or percentage (float) of top-cited papers.
    verbose : bool
        If True, prints status messages.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.
    top : list
        A list of 'ayjid' keys for the topn most cited papers.
    counts : dict
        Citation counts for all papers cited by papers.
    """

    if verbose:
        print "Getting parents of top "+unicode(topn)+" most cited papers."

    top, counts = top_cited(papers, topn=topn, verbose=verbose)
    papers = [ P for P in papers if P['citations'] is not None ]
    parents = [ P for P in papers if len(
                    set([ c['ayjid'] for c in P['citations'] ]) &
                    set(top) ) > 0 ]

    if verbose:
        print "Found " + unicode(len(parents)) + " parents."

    return parents, top, counts
