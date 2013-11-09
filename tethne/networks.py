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
    Create a NetworkX directed graph based on citation records.
    
    **Nodes** -- documents represented by the value of meta_dict[node_id].
    
    **Edges** -- from one document to its citation.
    
    **Edge attributes** -- date (year) of citation

    Parameters
    ----------
    doc_list : list
        A list of :py:func:`meta_dicts <tethne.data_struct.new_meta_dict>`.
        
    node_id : int
        A key from meta_dict to identify the nodes.
        
    node_attribs : list
        List of user provided optional arguments apart from the provided 
        positional arguments.
        
    Returns
    -------
    citation_network : networkx.DiGraph
        Global citation network (all citations).
    citation_network_internal : networkx.DiGraph
        Internal citation network where only the papers in the list are nodes in
        the network.
    
    Raises
    ------
    KeyError : If node_id is not present in the meta_list.
    
    Notes
    -----
    Should we allow for node attribute definition?
    Perhaps a function that makes use of the meta_dict keys and produces
    an edge_attribute value is in order, similar to the bibliographic
    coupling networks.
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
    
    **Nodes** -- Two kinds of nodes with distinguishing "type" attributes.
        * type = paper    - a paper in doc_list
        * type = person   - a person in doc_list

    Papers also have node attributes defined by paper_attribs.
    
    **Edges** -- Directed, Author -> her Paper 
    
    Parameters
    ----------
    doc_list : list
        A list of wos_objects.
    paper_id : string
        A key from meta_dict, used to identify the nodes.
    paper_attribs : list
        List of user-provided optional arguments apart from the provided 
        positional arguments. 
        
    Returns
    -------
    author_papers : networkx.DiGraph
        A DiGraph 'author_papers'.
    
    Raises
    ------
    KeyError : Raised when paper_id is not present in the meta_list.
    
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
    
    **Nodes** -- author names
    
    **Node attributes** -- none
    
    **Edges** -- (a,b) \in E(G) if a and b are coauthors on the same paper.
       
    Parameters
    ----------
    doc_list : list
        A list of wos_objects.
    edge_attribs : list
        List of edge_attributes specifying which meta_dict keys (from the 
        co-authored paper) to use as edge attributes.
        
    Returns
    -------
    coauthors : networkx.MultiGraph
        A co-authorship network.
    
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
    Generate a bibliographic coupling network.
    
    **Nodes** -- papers represented by node_id and node attributes defined by
    node_attribs (in meta_dict keys).
    
    **Edges** -- (a,b) \in E(G) if a and b share x citations where x >= 
    threshold.
    
    **Edge attributes** -- overlap, the number of citations shared
        
   
    Parameters
    ----------
    doc_list : list
        A list of wos_objects.
    citation_id: string
        A key from meta_dict to identify the citation overlaps.
    threshold : int
        Minimum number of shared citations to consider two papers "coupled".
    node_id : string
        Field in meta_dict used to identify the nodes.
    node_attribs : list
        List of fields in meta_dict to include as node attributes in graph.
        
    Returns
    -------
    bcoupling : networkx.Graph
        A bibliographic coupling network.
    
    Raises
    ------
    KeyError : Raised when citation_id is not present in the meta_list.
   
    Notes
    -----
    Lists cannot be attributes? causing errors for both gexf and graphml also 
    nodes cannot be none.
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
    Generate a simple author coupling network, where vertices are papers and
    an edge indicates that two papers share a common author.
    
    **Nodes** -- Papers.
    
    **Edges** -- (a,b) \in E(G) if a and b share x authors and x >= threshold
    
    **Edge attributes** -- overlap, the value of x (above).

    Parameters
    ----------
    doc_list : list
        A list of wos_objects.
    threshold : int
        Minimum number of co-citations required to draw an edge between two
        authors.
    node_id : string
        Field in meta_dict used to identify nodes.    
    node_attribs : list
        List of fields in meta_dict to include as node attributes in graph.
        
    Returns
    -------
    acoupling : networkx.Graph
        An author-coupling network.
           
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
                a= acoupling.add_edge(doc_list[i][node_id], 
                                   doc_list[j][node_id],
                                   overlap=len(overlap))
                print ' final :' , a

    return acoupling 


def nx_author_cocitation(meta_list, threshold):
    
    """
    Creates an author cocitation network. Vertices are authors, and an edge
    implies that two authors have been cited (via their publications) by in at
    least one paper in the dataset.
    
    **Nodes** -- Authors
    
    **Node attributes** -- None
    
    **Edges** -- (a, b) if a and b are referenced by the same paper in the 
    meta_list
    
    **Edge attributes** -- 'weight', the number of papers that co-cite two 
    authors.
                      
    Parameters
    ----------
    meta_list : list
        a list of wos_objects.
        
    threshold : int
        A random value provided by the user. If its greater than zero two nodes 
        should share something common.
        
    Returns
    -------
    cocitation : networkx.Graph
        A cocitation network.
                      
    Notes
    -----
    should be able to specify a threshold -- number of co-citations required to 
    draw an edge.
    
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

def nx_author_institution(meta_list):
    
    """
    Create a bi-partite graph with people and institutions as vertices, and
    edges indicating affiliation. This may be slightly ambiguous for WoS data
    where num authors != num institutions.
    
    Story #57746740
    
    Parameters
    ----------
    meta_list : list
        A list of meta_dict dictionaries.
    
    Returns
    -------
    author_institution : networkx.DiGraph
        A graph describing institutional affiliations of authors in the corpus.
        
    
    
    """
    
#===============================================================================
#     author_institution = nx.DiGraph(type='author_institution')
# 
#     for meta_dict in meta_list:
#         name_list = util.concat_list(meta_dict['aulast'],
#                                      meta_dict['auinit'],
#                                      ' ')
#         for i in xrange(len(name_list)):
#             name = name_list[i]
#             institution meta_dict['institution'][i]
#===============================================================================

            # Create nodes
            # Draw edges
            # Add edge attributes

    return author_institution


def nx_author_coinstitution(meta_list,threshold):
    
    """
    Create a graph with people as vertices, and edges indicating affiliation
    with the same institution. This may be slightly ambiguous for WoS data
    where num authors != num institutions.
    
    
    Nodes           - Authors
    Node attributes - affiliation ID (fuzzy identifier) # not considered as of now.
    Edges           - (a, b) if a and b are share the same affiliated institution 
                      the meta_list
                      (a, b) if a and b are share the same affiliated country 
                      the meta_list
                      
                      
    Edge attributes - 'weight' the count of shared  institutions, shared country between 2 authors that would cause an
                       edge to be drawn between a and b
                      
    Args:
        meta_list : a list of wos_objects.
        threshold : A random value provided by the user. If its greater than zero two nodes 
                    should share something common.
        
    Returns: 
        A coinstitution network.
    
    Raises:
        None.                     
                   
    
    """
#    coinstitution = nx.Graph(type='author_coinstitution')
#    
#    let the metalist have 10 metadicts
#        take the 1 st meta dict and retrieve the key of institutions
#             continue till the number of authors in that field (let it be 5)
                
    
    

    #The Field in meta_list which corresponds to the affiliation is "C1" - Authors Address
    for author in meta_list:
        if author[address] != "":
            for institution in author['address']:
               
                author_list = util.concat_list(institution['aulast'],
                                               institution['auinit'],
                                               institution['country'])
                num_authors = len(author_list)
                for i in xrange(num_authors):                           
                    coinstitution.add_node(author_list[i])              #add node attributes
                    for j in xrange(i+1, num_authors):
                        try:
                            coinstitution[author_list[i]][author_list[j]]['weight'] += 1
                        except KeyError:
                            # then edge doesn't yet exist
                            cocitation.add_edge(author_list[i], author_list[j],   #add edge attributes
                                                {'weight':1})
    
    return cocitation


def nx_cocitation(meta_list, timeslice, threshold):
    
    """
    A cocitation network is a network in which vertices are papers, and edges
    indicate that two papers were cited by the same third paper. Should slice
    the dataset into timeslices (as indicated) based on the publication date of
    the citing papers in the dataset. Each time-slice should result in a
    separate networkx Graph in which vertices are the _cited_ papers. Separate
    graphs allows to analyze each timeslice separately.
    
    """
    
    pass
