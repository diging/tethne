import networkx as nx

def contains(l, f):
    """Searches list l for a pattern specified in a lambda function f."""
    for x in l:
        if f(x):
            return True
    return False


def nx_citations(wos_list):
    """
    Create a NetworkX directed graph based on citation records
    Nodes       - 
    Node attr   - 
    Edges       -
    Edge attr   -

    Input:
        a list of wos_objects
    Output:
        a tuple t with
        t(0): global citation network (all citations), and an 
        t(1): internal citation network where only the papers in the data 
            library are nodes in the network
    """
    citation_network = nx.DiGraph()
    citation_network_internal = nx.DiGraph()
    for entry in wos_list:
        if entry.citations is not None:
            for citation in entry.citations:
                citation_network.add_edge(entry.identifier, 
                                               citation,
                                               rel="citation",
                                               year=entry.year)
                if (contains (wos_list, 
                              lambda wos_obj: 
                                  wos_obj.identifier == citation)):
                    citation_network_internal.add_edge(
                        entry.identifier, 
                        citation,
                        rel="citation",
                        year=entry.year)

    return citation_network, citation_network_internal


