import networkx as nx
import utilities as util

def nx_citations(wos_list):
    """
    Create a NetworkX directed graph based on citation records
    Nodes       - 
    Node attr   - 
    Edges       -
    Edge attr   -

    Input:
        a list of wos_dicts
    Output:
        a tuple t with
        t(0): global citation network (all citations), and an 
        t(1): internal citation network where only the papers in the data 
            library are nodes in the network
    """
    citation_network = nx.DiGraph()
    citation_network_internal = nx.DiGraph()
    for entry in wos_list:
        if entry['citations'] is not None:
            for citation in entry['citations']:
                citation_network.add_edge(entry['identifier'], 
                                               citation,
                                               rel="citation",
                                               year=entry['year'])
                if (util.contains (wos_list, 
                                   lambda wos_obj: 
                                       wos_obj['identifier'] == citation)):
                    citation_network_internal.add_edge(
                        entry['identifier'], 
                        citation,
                        rel="citation",
                        year=entry['year'])

    return citation_network, citation_network_internal


def nx_author_papers(wos_list):
        """
        Generate an author_papers network NetworkX directed graph.
        Nodes - two kinds of nodes with distinguishing "type" attributes
            type = paper    - a paper in wos_list
            type = person   - a person in wos_list
        Edges - directed Author -> her Paper 
            year    - date of publication

        Input: wos_list list of wos_objects
        Output: author_papers DiGraph 
        """
        author_papers = nx.DiGraph()
        for entry in wos_list:
            author_papers.add_node(entry['identifier'], year=entry['year'],
                                   type="paper")
            for author in entry['AU']:
                author_papers.add_node(author,
                                       type="person")

                author_papers.add_edge(author, entry['identifier'],
                                       year=entry['year'])
        return author_papers

def nx_coauthors(wos_list):
    """
    Generates a co-author network 
    Nodes - author names
    Edges - (a,b) \in E(G) if a and b are coauthors on the same paper
    Edge attributes -
        year - date of publication
        paper - wos CR string describing the paper
    Input: wos_list list of wos_objects
    Output: simple coauthor network
    """
    coauthors = nx.Graph()
    for entry in wos_list:
        for a in xrange(len(entry['meta']['AU'])):
            # index all authors in author list
            for b in xrange(a+1, len(entry['meta']['AU'])):
                # secondary author index
                coauthors.add_edge(entry['meta']['AU'][a], 
                                   entry['meta']['AU'][b],
                                   year=entry['year'],
                                   paper=entry['identifier'])
                                   

    return coauthors


def nx_biblio_coupling(wos_list, threshold):
    """
    Generate a simple bibliographic coupling network 
    Nodes - CR-like string of papers 
    Node attributes -
        wosid - web of science identification number 
        year - date of publication
    Edges - (a,b) \in E(G) if a and b share x citations where 
        x >= threshold
    Edge attributes - 
        overlap - the number of citations shared
    Input -
        wos_list list of wos_objects
        threshold int 
    Output - bibliographic coupling network
    """
    bcoupling = nx.Graph()
    for i in xrange(len(wos_list)):
        for j in xrange(i+1, len(wos_list)):
            overlap = util.overlap(wos_list[i]['citations'], 
                                   wos_list[j]['citations'])
            if len(overlap) >= threshold:
                bcoupling.add_node(wos_list[i]['identifier'],
                                   wosid=wos_list[i]['wosid'],
                                   year=wos_list[i]['year'])
                bcoupling.add_node(wos_list[j]['identifier'],
                                   wosid=wos_list[j]['wosid'],
                                   year=wos_list[j]['year'])
                bcoupling.add_edge(wos_list[i]['identifier'],
                                   wos_list[j]['identifier'],
                                   overlap=len(overlap))
    return bcoupling

def nx_author_coupling(wos_list, threshold):
    """
    Generate a simple author coupling network
    Nodes - papers represented by CR-like strings
    Node attributes -
        wosid - web of science paper identification number
        year - date of publication
    Edges - (a,b) \in E(G) if a and b share x authors and x >= threshold
    Edge attributes - 
        rel - description of edge relation
        overlap - number of shared authors
    Input - wos_library.library list  
    Output - simple author coupling network
    """
    acoupling = nx.Graph()
    for i in xrange(len(wos_list)):
        for j in xrange(i+1, len(wos_list)):
            overlap = util.overlap(wos_list[i]['meta']['AU'],
                                   wos_list[j]['meta']['AU'])
            if len(overlap) >= threshold:
                acoupling.add_node(wos_list[i]['identifier'],
                                   wosid=wos_list[i]['wosid'],
                                   year=wos_list[i]['year'])
                acoupling.add_node(wos_list[j]['identifier'],
                                   wosid=wos_list[j]['wosid'],
                                   year=wos_list[j]['year'])
                acoupling.add_edge(wos_list[i]['identifier'], 
                                   wos_list[j]['identifier'],
                                   rel="shareAuthor",
                                   overlap=len(overlap))
    return acoupling 


