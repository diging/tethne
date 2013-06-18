"""
Each network relies on certain meta data in the meta_dict associated with
each document. Often we wish to construct a network with nodes representing
these documents and edges representing relationships between those documents,
but this is not always the case.

Where it is the case, it is recommended but not required that nodes are 
represented by an identifier from {ayjid, wosid, pmid, doi}. Each has certain
benefits. If the documents to be networked come from a single database source
such as the Web of Science, wosid is most appropriate. If not, using doi
will result in a more accurate, but also more sparse network; while ayjid 
will result in a less accurate, but more complete network.

Any type of meta data from the meta_dict may be used as an identifier, however.

We use "head" and "tail" nomenclature to refer to the members of a directed
edge (x,y), x -> y, xy, etc. by calling x the "tail" and y the "head"
"""
import networkx as nx
import utilities as util
import data_struct as ds

def nx_citations(doc_list, node_id):
    """
    Create a NetworkX directed graph based on citation records
    Nodes       - documents represented by the value of meta_dict[node_id]
    Node attr   - none 
    Edges       - from one document to its citation
    Edge attr   - date (year) of citation

    Input  
        doc_list - a list of meta_dicts
        node_id  - a key from meta_dict to identify the nodes
    Return a tuple t with
        t(0): global citation network (all citations), and an 
        t(1): internal citation network where only the papers in the
            list are nodes in the network
    Notes
        Should we allow for node attribute definition?
        Perhaps a function that makes use of the meta_dict keys and produces
            an edge_attribute value is in order, similar to the bibliographic
            coupling networks
    """
    citation_network = nx.DiGraph()
    citation_network_internal = nx.DiGraph()

    #check general node_id validity
    dummy_dict = ds.new_meta_dict()
    if node_id not in dummy_dict.iterkeys():
        raise KeyError('node_id:' + node_id + 'is not in the set of' +
                       'expected key names')

    for entry in doc_list:
        #check the head
        head_has_id = True
        if entry[node_id] is None:
            head_has_id = False
        if entry['citations'] is not None:

            for citation in entry['citations']:
                #check the tail
                tail_has_id = True
                if citation[node_id] is None:
                    tail_has_id = False

                if head_has_id and tail_has_id:
                    #then draw an edge in the network
                    citation_network.add_edge(entry[node_id], 
                                              citation[node_id],
                                              year=entry['date'])

                    #and check if it can be added to the internal network too
                    if (util.contains (doc_list, 
                                       lambda wos_obj: 
                                       wos_obj[node_id] == citation[node_id])):
                        citation_network_internal.add_edge(
                            entry[node_id], 
                            citation[node_id],
                            year=entry['date'])

    return citation_network, citation_network_internal


def nx_author_papers(doc_list, paper_id, *paper_attribs):
    """
    Generate an author_papers network NetworkX directed graph.
    Nodes - two kinds of nodes with distinguishing "type" attributes
        type = paper    - a paper in doc_list
        type = person   - a person in doc_list
        papers also have node attributes defined by paper_attribs
    Edges - directed Author -> her Paper 
        year    - date of publication

    Input: doc_list list of wos_objects
    Output: author_papers DiGraph 
    """
    author_papers = nx.DiGraph()

    #validate paper attributes
    dummy_dict = ds.new_meta_dict()
    meta_keys = dummy_dict.keys()
    valid_attribs = []
    for attrib in paper_attribs:
        if attrib in meta_keys:
            valid_attribs.append(attrib)

    for entry in doc_list:
        #define node_attribute dictionary
        node_attrib_dict = {}
        for attrib in valid_attribs:
            node_attrib_dict[attrib] = entry[attrib]
        node_attrib_dict['type'] = 'paper'
        print node_attrib_dict

        #add paper node with attributes
        author_papers.add_node(entry[paper_id], node_attrib_dict)
                               
        for i in xrange(len(entry['aulast'])):
            author = entry['aulast'][i] + ' ' + entry['auinit'][i]
            author_papers.add_node(author, type="person")

            author_papers.add_edge(author, entry[paper_id],
                                   year=entry['date'])
    return author_papers


def nx_coauthors(doc_list, *edge_attribs):
    """
    Generate a co-author network 
    Nodes        - author names
    Node attribs - none
    Edges        - (a,b) \in E(G) if a and b are coauthors on the same paper
    Edge attribs - user provided tuple specifying which meta_dict keys
                   (for the paper they coauthored on) to use as edge attributes
    Input a doc_list list of wos_objects
    Return a simple coauthor network
    """
    coauthors = nx.Graph()

    #edge_attribs that are keys in the meta_dict structure are valid
    valid_edge_attribs = []
    meta_keys = ds.new_meta_dict().keys()
    for attrib in edge_attribs:
        if attrib in meta_keys:
            valid_edge_attribs.append(attrib)

    for entry in doc_list:
        if entry['aulast'] is not None:
            #index the authors twice
            for a in xrange(len(entry['aulast'])):
                for b in xrange(a+1, len(entry['aulast'])):
                    coauthors.add_edge(entry['aulast'][a], entry['aulast'][b])

                    #add edges with specified edge attributes
                    for attrib in valid_edge_attribs:
                        coauthors[entry['aulast'][a]][entry['aulast'][b]][attrib] = entry[arg]

    return coauthors


def nx_biblio_coupling(doc_list, citation_id, threshold, node_id, 
                       *node_attribs):
    """
    Generate a simple bibliographic coupling network 
    Nodes - papers represented by node_id and node attributes defined by
            all arguments (in meta_dict keys) after the 4th argument provided
    Edges - (a,b) \in E(G) if a and b share x citations where 
            x >= threshold
    Edge attributes - 
        overlap - the number of citations shared
    Input - doc_list of meta_dicts; citation_id is how citation overlap
            is identified
    Return a bibliographic coupling network
    Notes
        lists cannot be attributes? causing errors for both gexf and graphml
        also nodes cannot be none
    """
    bcoupling = nx.Graph()

    #validate citation_id, node_id, and node attribs
    dummy_dict = ds.new_meta_dict()
    meta_keys = dummy_dict.keys()
    valid_attribs = []
    for attrib in node_attribs:
        if attrib in meta_keys:
            valid_attribs.append(attrib)

    if node_id not in meta_keys:
        raise KeyError('node_id' + node_id + ' is not a meta_dict key.')

    #citations is the only invalid meta_key for citation_id
    meta_keys.remove('citations')
    if citation_id not in meta_keys:
        raise KeyError('citation_id' + citation_id + ' is not a meta_dict' +
                       ' key or otherwise cannot be used to detect citation' +
                       ' overlap.')
    
    for i in xrange(len(doc_list)):
        #make a list of citation_id's for each document
        i_list = []
        for citation in doc_list[i]['citations']:
            i_list.append(citation[citation_id])

        #and construct that document's node
        i_attribs = {}
        for attrib in valid_attribs:
            if doc_list[i][attrib] is not None:
                i_attribs[attrib] = doc_list[i][attrib]
        bcoupling.add_node(doc_list[i][node_id], i_attribs)

        for j in xrange(i+1, len(doc_list)):
            #make a list of citation_id's for each document
            j_list = []
            for citation in doc_list[j]['citations']:
                j_list.append(citation[citation_id])

            #and construct that document's node
            j_attribs = {}
            for attrib in valid_attribs:
                if doc_list[j][attrib] is not None:
                    j_attribs[attrib] = doc_list[i][attrib]
            bcoupling.add_node(doc_list[i][node_id], j_attribs)

            #add an edge if the citation overlap is sufficiently high
            overlap = util.overlap(i_list, j_list)
            if len(overlap) >= threshold:
                bcoupling.add_edge(doc_list[i][node_id],
                                   doc_list[j][node_id],
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
                acoupling.add_edge(doc_list[i]['ayjid'], 
                                   doc_list[j]['ayjid'],
                                   rel="shareAuthor",
                                   overlap=len(overlap))
    return acoupling 


