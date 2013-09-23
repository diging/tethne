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

def nx_citations(doc_list, node_id, *node_attribs):
    """
    Create a NetworkX directed graph based on citation records
    Nodes       - documents represented by the value of meta_dict[node_id]
    Node attr   - specified meta data for a paper in node_attribs
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
    citation_network = nx.DiGraph(type='citations')
    citation_network_internal = nx.DiGraph(type='citations')

    #check general node_id validity
    meta_keys = ds.new_meta_dict().keys()
    if node_id not in meta_keys:
        raise KeyError('node_id:' + node_id + 'is not in the set of' +
                       'meta_keys')

    for entry in doc_list:
        #check the head
        head_has_id = True
        if entry[node_id] is None:
            head_has_id = False

        if head_has_id:
            #then create node to both global and internal networks
            node_attrib_dict = util.subdict(entry, node_attribs)
            citation_network.add_node(entry[node_id], node_attrib_dict)
            citation_network_internal.add_node(entry[node_id], 
                                               node_attrib_dict) 

        if entry['citations'] is not None:
            for citation in entry['citations']:
                #check the tail
                tail_has_id = True
                if citation[node_id] is None:
                    tail_has_id = False

                if tail_has_id:
                    #then create node to global but not internal network
                    node_attrib_dict = util.subdict(citation, node_attribs)
                    citation_network.add_node(citation[node_id], 
                                              node_attrib_dict)

                if head_has_id and tail_has_id:
                    #then draw an edge in the network
                    citation_network.add_edge(entry[node_id], 
                                              citation[node_id],
                                              date=entry['date'])

                    #and check if it can be added to the internal network too
                    if (util.contains (doc_list, 
                                       lambda wos_obj: 
                                       wos_obj[node_id] == citation[node_id])):
                        citation_network_internal.add_edge(
                            entry[node_id], 
                            citation[node_id],
                            date=entry['date'])

    return citation_network, citation_network_internal


def nx_author_papers(doc_list, paper_id, *paper_attribs):
    """
    Generate an author_papers network NetworkX directed graph.
    Nodes - two kinds of nodes with distinguishing "type" attributes
        type = paper    - a paper in doc_list
        type = person   - a person in doc_list
        papers also have node attributes defined by paper_attribs
    Edges - directed Author -> her Paper 
        date    - date of publication

    Input: doc_list list of wos_objects
    Output: author_papers DiGraph 
    """
    author_papers = nx.DiGraph(type='author_papers')

    #validate paper_id
    meta_keys = ds.new_meta_dict().keys()
    meta_keys.remove('citations')
    if paper_id not in meta_keys:
        raise KeyError('paper_id' + paper_id + ' cannot be used to identify' +
                       ' papers.')

    for entry in doc_list:
        #define paper_attribute dictionary
        paper_attrib_dict = util.subdict(entry, paper_attribs)
        paper_attrib_dict['type'] = 'paper'

        #add paper node with attributes
        author_papers.add_node(entry[paper_id], paper_attrib_dict)
                               
        authors = util.concat_list(entry['aulast'], entry['auinit'], ' ')
        for i in xrange(len(authors)):
            #add person node
            author_papers.add_node(authors[i], type="person")

            #draw edges
            author_papers.add_edge(authors[i], entry[paper_id],
                                   date=entry['date'])

    return author_papers


def nx_coauthors(doc_list, *edge_attribs):
    """
    Generate a co-author network. 
    Nodes        - author names
    Node attribs - none
    Edges        - (a,b) \in E(G) if a and b are coauthors on the same paper
    Edge attribs - user provided edge_attribs specifying which meta_dict keys
                   (for the paper they coauthored on) to use as edge attributes
    Input a doc_list list of wos_objects
    Return a simple coauthor network
    """
    coauthors = nx.MultiGraph(type='coauthors')

    for entry in doc_list:
        if entry['aulast'] is not None:
            #edge_attrib_dict for any edges that get added
            edge_attrib_dict = util.subdict(entry, edge_attribs)

            #make a new list of aulast, auinit names
            full_names = util.concat_list(entry['aulast'], 
                                          entry['auinit'], 
                                          ' ')

            #index the authors twice
            for a in xrange(len(full_names)):
                #create node for author a
                coauthors.add_node(full_names[a])

                for b in xrange(a+1, len(entry['aulast'])):
                    #create node for author b
                    coauthors.add_node(full_names[b])

                    #add edges with specified edge attributes
                    coauthors.add_edge(full_names[a], 
                                       full_names[b],
                                       attr_dict=edge_attrib_dict)

    return coauthors


def nx_biblio_coupling(doc_list, citation_id, threshold, node_id, 
                       *node_attribs):
    """
    Generate a simple bibliographic coupling network 
    Nodes - papers represented by node_id and node attributes defined by
            node_attribs (in meta_dict keys) 
    Edges - (a,b) \in E(G) if a and b share x citations where 
            x >= threshold
    Edge attributes - 
        overlap - the number of citations shared
    Input - doc_list of meta_dicts 
            citation_id is how citation overlap is identified
    Return a bibliographic coupling network
    Notes
        lists cannot be attributes? causing errors for both gexf and graphml
        also nodes cannot be none
        copyright (c) 2013 Erick Pierson and Aaron Baker
    """
    bcoupling = nx.Graph(type='biblio_coupling')

    #validate identifiers
    meta_keys = ds.new_meta_dict().keys()
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
        if doc_list[i]['citations'] is not None:
            for citation in doc_list[i]['citations']:
                i_list.append(citation[citation_id])

        #and construct that document's node
        node_i_attribs = util.subdict(doc_list[i], node_attribs)
        bcoupling.add_node(doc_list[i][node_id], node_i_attribs)

        for j in xrange(i+1, len(doc_list)):
            #make a list of citation_id's for each document
            j_list = []
            if doc_list[j]['citations'] is not None:
                for citation in doc_list[j]['citations']:
                    j_list.append(citation[citation_id])

            #and construct that document's node
            node_j_attribs = util.subdict(doc_list[j], node_attribs)
            bcoupling.add_node(doc_list[j][node_id], node_j_attribs)

            #add an edge if the citation overlap is sufficiently high
            overlap = util.overlap(i_list, j_list)
            if len(overlap) >= threshold:
                bcoupling.add_edge(doc_list[i][node_id],
                                   doc_list[j][node_id],
                                   overlap=len(overlap))
    return bcoupling

def nx_author_coupling(doc_list, threshold, node_id, *node_attribs):
    """
    Generate a simple author coupling network
    Nodes        - papers
    Node attribs - specified by node_attribs
    Edges        - (a,b) \in E(G) if a and b share x authors and x >= threshold
    Edge attribs - overlap, the value of x above
    Return a simple author coupling network
    Notes
        copyright (c) 2013 Erick Pierson and Aaron Baker
    """
    acoupling = nx.Graph(type='author_coupling')

    for i in xrange(len(doc_list)):
        #define last name first initial name lists for each document
        name_list_i = util.concat_list(doc_list[i]['aulast'],
                                       doc_list[i]['auinit'], 
                                       ' ')

        #create nodes
        node_attrib_dict = util.subdict(doc_list[i], node_attribs)
        acoupling.add_node(doc_list[i][node_id], node_attrib_dict)

        for j in xrange(i+1, len(doc_list)):
            #define last name first initial name lists for each document
            name_list_j = util.concat_list(doc_list[j]['aulast'],
                                           doc_list[j]['auinit'], 
                                           ' ')

            #create nodes
            node_attrib_dict = util.subdict(doc_list[j], node_attribs)
            acoupling.add_node(doc_list[j][node_id], node_attrib_dict)

            #draw edges as appropriate
            overlap = util.overlap(name_list_i, name_list_j)
            if len(overlap) >= threshold:
                acoupling.add_edge(doc_list[i][node_id], 
                                   doc_list[j][node_id],
                                   overlap=len(overlap))

    return acoupling 


def nx_author_cocitation(meta_list, threshold):
    """
    Create an author cocitation (analysis) network
    Nodes           - Authors
    Node attributes - None
    Edges           - (a, b) if a and b are referenced by the same paper in 
                      the meta_list
    Edge attributes - 'weight' the count of papers that would cause an
                      edge to be drawn between a and b
    Copyright 2013 Aaron Baker
    """
    cocitation = nx.Graph(type='author_cocitation')

    for paper in meta_list:
        for citation in paper['citations']:
            author_list = util.concat_list(citation['aulast'],
                                           citation['auinit'],
                                           ' ')
            num_authors = len(author_list)
            for i in xrange(num_authors):
                cocitation.add_node(author_list[i])
                for j in xrange(i+1, num_authors):
                    try:
                        cocitation[author_list[i]][author_list[j]]['weight'] += 1
                    except KeyError:
                        # then edge doesnt yet exist
                        cocitation.add_edge(author_list[i], author_list[j],
                                            {'weight':1})

    return cocitation 
