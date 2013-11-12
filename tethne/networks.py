"""
Each network relies on certain meta data in the :class:`.Paper` associated with
each document. Often we wish to construct a network with nodes representing
these documents and edges representing relationships between those documents,
but this is not always the case.

Where it is the case, it is recommended but not required that nodes are 
represented by an identifier from {ayjid, wosid, pmid, doi}. Each has certain
benefits. If the documents to be networked come from a single database source
such as the Web of Science, wosid is most appropriate. If not, using doi
will result in a more accurate, but also more sparse network; while ayjid 
will result in a less accurate, but more complete network.

Any type of meta data from the :class:`.Paper` may be used as an identifier, 
however.

We use "head" and "tail" nomenclature to refer to the members of a directed
edge (x,y), x -> y, xy, etc. by calling x the "tail" and y the "head"
"""
import networkx as nx
import utilities as util
import data as ds

def nx_citations(doc_list, node_id, *node_attribs):
    """
    Create a NetworkX directed graph based on citation records.
    
    **Nodes** -- documents represented by the value of :class:`.Paper` [node_id].
    
    **Edges** -- from one document to its citation.
    
    **Edge attributes** -- date (year) of citation

    Parameters
    ----------
    doc_list : list
        A list of :class:`.Paper` instances.
        
    node_id : int
        A key from :class:`.Paper` to identify the nodes.
        
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
    Perhaps a function that makes use of the :class:`.Paper` keys and produces
    an edge_attribute value is in order, similar to the bibliographic
    coupling networks.
    """
    citation_network = nx.DiGraph(type='citations')
    citation_network_internal = nx.DiGraph(type='citations')

    # Check node_id validity.
    meta_dict = ds.Paper()
    meta_keys = meta_dict.keys()
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
        A key from :class:`.Paper` used to identify the nodes.
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

    # Validate paper_id.
    meta_dict = ds.Paper()
    meta_keys = meta_dict.keys()
    meta_keys.remove('citations')
    if paper_id not in meta_keys:
        raise KeyError('paper_id' + paper_id + ' cannot be used to identify' +
                       ' papers.')

    for entry in doc_list:
        # Define paper_attribute dictionary.
        paper_attrib_dict = util.subdict(entry, paper_attribs)
        paper_attrib_dict['type'] = 'paper'

        # Add paper node with attributes.
        author_papers.add_node(entry[paper_id], paper_attrib_dict)
                               
        authors = util.concat_list(entry['aulast'], entry['auinit'], ' ')
        for i in xrange(len(authors)):
            # Add person node.
            author_papers.add_node(authors[i], type="person")

            # Draw edges.
            author_papers.add_edge(authors[i], entry[paper_id],
                                   date=entry['date'])

    return author_papers


def nx_coauthors(papers, *edge_attribs):
    """
    Generate a co-author network. 
    
    **Nodes** -- author names
    
    **Node attributes** -- none
    
    **Edges** -- (a,b) \in E(G) if a and b are coauthors on the same paper.
       
    Parameters
    ----------
    papers : list
        A list of :class:`Paper` instances.
    edge_attribs : list
        List of edge_attributes specifying which :class:`.Paper` keys (from the 
        co-authored paper) to use as edge attributes.
        
    Returns
    -------
    coauthors : networkx.MultiGraph
        A co-authorship network.
        
    Notes
    -----
    TODO: Check whether papers contains :class:`Papers` instances, and raise
    an exception if not.
    
    """

    coauthors = nx.MultiGraph(type='coauthors')

    for entry in papers:
        if entry['aulast'] is not None:
            # edge_attrib_dict for any edges that get added
            edge_attrib_dict = util.subdict(entry, edge_attribs)

            # make a new list of aulast, auinit names
            full_names = util.concat_list(entry['aulast'], 
                                          entry['auinit'], 
                                          ' ')

            for a in xrange(len(full_names)):
                coauthors.add_node(full_names[a]) # create node for author a
                for b in xrange(a+1, len(entry['aulast'])):
                    coauthors.add_node(full_names[b]) #create node for author b
                    
                    #add edges with specified edge attributes
                    coauthors.add_edge(full_names[a], 
                                       full_names[b],
                                       attr_dict=edge_attrib_dict)

    return coauthors

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
        Simplifies a ``multigraph``.
    
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
                        if edge['date'] < start: start = edge['date']
                        if edge['date'] > end: end = edge['date']
                    except KeyError:    # No date to be found.
                        pass

                if found_date:  # If no date found, don't add start/end atts.
                    edge_attribs['start'] = start
                    edge_attribs['end'] = end

            graph.add_edge(u, v, edge_attribs)

    return graph
            

        
def nx_biblio_coupling(doc_list, citation_id, threshold, node_id, 
                       *node_attribs):
    """
    Generate a bibliographic coupling network.
    
    **Nodes** -- papers represented by node_id and node attributes defined by
    node_attribs (in :class:`.Paper` keys).
    
    **Edges** -- (a,b) \in E(G) if a and b share x citations where x >= 
    threshold.
    
    **Edge attributes** -- overlap, the number of citations shared
        
   
    Parameters
    ----------
    doc_list : list
        A list of wos_objects.
    citation_id: string
        A key from :class:`.Paper` to identify the citation overlaps.
    threshold : int
        Minimum number of shared citations to consider two papers "coupled".
    node_id : string
        Field in :class:`.Paper` used to identify the nodes.
    node_attribs : list
        List of fields in :class:`.Paper` to include as node attributes in 
        graph.
        
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

    # Validate identifiers.
    meta_dict = ds.Paper()
    meta_keys = meta_dict.keys()
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
        Field in :class:`.Paper` used to identify nodes.    
    node_attribs : list
        List of fields in :class:`.Paper` to include as node attributes in graph.
        
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
        a list of :class:`.Paper` objects.
        
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
        A list of :class:`.Paper` instances.
    
    Returns
    -------
    author_institution : networkx.DiGraph
        A graph describing institutional affiliations of authors in the corpus.
        
    
    
    """
    
    author_institution = nx.DiGraph(type='author_institution')
     #The Field in meta_list which corresponds to the affiliation is "institutions"   { 'institutions' : { Authors:[institutions_list]}}
    
#===============================================================================
#          #The Field in meta_list which corresponds to the affiliation is "institutions"   
#      # { 'institutions' : { Authors:[institutions_list]}}
#     author_institutions = {}  # keys: author names, values: list of institutions
#     for paper in meta_list:
#         for key, value in paper['institutions'].iteritems():
#             try:
#                 author_institutions[key] += value
#             except KeyError:
#                 author_institutions[key] = value
#                 
#     authors = author_institutions.keys()
#     for i in xrange(len(authors)):
#         coinstitution.add_node(authors[i])
#         institutions = author_institutions.values() # pull out the values of institutions
#         for i in xrange(len(institutions)):
#             
#       
#                 overlap = set(author_institutions[authors[i]]) & set(author_institutions[authors[j]]) #compare 2 author dict elements
#                 if len(overlap) > threshold:
#                     if coinstitution.has_node(j):           
#                         print ' has node already'  
#                         print authors[i] + "->" + authors[j]
#                         coinstitution.add_edge(authors[i], authors[j],threshold=overlap)
#                     else:
#                         print ' node J needs to be created'   
#                         coinstitution.add_node(authors[j])            
#                         print authors[i] + "->" + authors[j]
#                         coinstitution.add_edge(authors[i], authors[j],threshold=overlap)
#                 else :
#                     print 'there are no shared affliations between', authors[i], ' and' , authors[j] , 'overlap is ', overlap
#                 
#                 
#     return coinstitution
# 
# 
#     return author_institution
#===============================================================================


def nx_author_coinstitution(meta_list,threshold):
    
    """
    Create a graph with people as vertices, and edges indicating affiliation
    with the same institution. This may be slightly ambiguous for WoS data
    where num authors != num institutions.
    
    
    Nodes           - Authors
    Node attributes - affiliation ID (fuzzy identifier)
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
    coinstitution = nx.Graph(type='author_coinstitution')

     #The Field in meta_list which corresponds to the affiliation is "institutions"   
     # { 'institutions' : { Authors:[institutions_list]}}
    author_institutions = {}  # keys: author names, values: list of institutions
    for paper in meta_list:
        for key, value in paper['institutions'].iteritems():
            try:
                author_institutions[key] += value
            except KeyError:
                author_institutions[key] = value
                
    authors = author_institutions.keys()
    for i in xrange(len(authors)):
        coinstitution.add_node(authors[i])  
        for j in xrange(len(authors)):
            if i != j:
                overlap = set(author_institutions[authors[i]]) & set(author_institutions[authors[j]]) #compare 2 author dict elements
                if len(overlap) > threshold:
                    if coinstitution.has_node(j):           
                        print ' has node already'  
                        print authors[i] + "->" + authors[j]
                        coinstitution.add_edge(authors[i], authors[j],threshold=overlap)
                    else:
                        print ' node J needs to be created'   
                        coinstitution.add_node(authors[j])            
                        print authors[i] + "->" + authors[j]
                        coinstitution.add_edge(authors[i], authors[j],threshold=overlap)
                else :
                    print 'there are no shared affliations between', authors[i], ' and' , authors[j] , 'overlap is ', overlap
                
                
    return coinstitution


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
