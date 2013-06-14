import networkx as nx
import utilities as util

def nx_citations(doc_list):
    """
    Create a NetworkX directed graph based on citation records
    Nodes       - 
    Node attr   - 
    Edges       -
    Edge attr   -

    Input:  doc_list, a list of meta_dicts
    Output:
        a tuple t with
        t(0): global citation network (all citations), and an 
        t(1): internal citation network where only the papers in the
            list are nodes in the network
    """
    citation_network = nx.DiGraph()
    citation_network_internal = nx.DiGraph()
    warning = False
    for entry in doc_list:
        if 'citations' is not None:
            for citation in entry['citations']:
                citation_network.add_edge(entry['ayid'], 
                                          citation['ayid'],
                                          rel="citation",
                                          year=entry['year'])
                if (util.contains (doc_list, 
                                   lambda wos_obj: 
                                       wos_obj['ayid'] == citation)):
                    citation_network_internal.add_edge(
                        entry['ayid'], 
                        citation['ayid'],
                        rel="citation",
                        year=entry['year'])
        else:
            warning = True

    if warning == True:
        print ('Warning: Some records lack citation data; graph may be more' +
               'sparse than expected.')

    return citation_network, citation_network_internal


def nx_author_papers(doc_list):
    """
    Generate an author_papers network NetworkX directed graph.
    Nodes - two kinds of nodes with distinguishing "type" attributes
        type = paper    - a paper in doc_list
        type = person   - a person in doc_list
    Edges - directed Author -> her Paper 
        year    - date of publication

    Input: doc_list list of wos_objects
    Output: author_papers DiGraph 
    """
    author_papers = nx.DiGraph()
    for entry in doc_list:
        author_papers.add_node(entry['ayid'], year=entry['year'],
                               type="paper")
        for author in entry['AU']:
            author_papers.add_node(author,
                                   type="person")

            author_papers.add_edge(author, entry['ayid'],
                                   year=entry['year'])
    return author_papers


def nx_coauthors(doc_list):
    """
    Generates a co-author network 
    Nodes - author names
    Edges - (a,b) \in E(G) if a and b are coauthors on the same paper
    Edge attributes -
        year - date of publication
        paper - wos CR string describing the paper
    Input: doc_list list of wos_objects
    Output: simple coauthor network
    """
    coauthors = nx.Graph()
    for entry in doc_list:
        if entry['aulast'] is not None:
            for a in xrange(len(entry['aulast'])):
                # index all authors in author list
                for b in xrange(a+1, len(entry['aulast'])):
                    # secondary author index
                    coauthors.add_edge(entry['aulast'][a], 
                                       entry['aulast'][b],
                                       year=entry['date'],
                                       paper=entry['ayid'])

    return coauthors


def nx_biblio_coupling(doc_list, threshold):
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
        doc_list list of wos_objects
        threshold int 
    Output - bibliographic coupling network
    """
    bcoupling = nx.Graph()
    for i in xrange(len(doc_list)):
        for j in xrange(i+1, len(doc_list)):
            overlap = util.overlap(doc_list[i]['citations']['ayid'], 
                                   doc_list[j]['citations']['ayid'])
            if len(overlap) >= threshold:
                bcoupling.add_edge(doc_list[i]['ayid'],
                                   doc_list[j]['ayid'],
                                   overlap=len(overlap))
    return bcoupling

def nx_author_coupling(doc_list, threshold):
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
    for i in xrange(len(doc_list)):
        for j in xrange(i+1, len(doc_list)):
            overlap = util.overlap(doc_list[i]['aulast'],
                                   doc_list[j]['aulast'])
            if len(overlap) >= threshold:
                acoupling.add_edge(doc_list[i]['ayid'], 
                                   doc_list[j]['ayid'],
                                   rel="shareAuthor",
                                   overlap=len(overlap))
    return acoupling 


