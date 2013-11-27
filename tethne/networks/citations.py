import networkx as nx
import tethne.utilities as util
import tethne.data as ds

def direct_citation(doc_list, node_id, *node_attribs):
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

def bibliographic_coupling(doc_list, citation_id, threshold, node_id,
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


def author_cocitation(meta_list, threshold):
    
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



def cocitation(meta_list, timeslice, threshold):
    
    """
    A cocitation network is a network in which vertices are papers, and edges
    indicate that two papers were cited by the same third paper. Should slice
    the dataset into timeslices (as indicated) based on the publication date of
    the citing papers in the dataset. Each time-slice should result in a
    separate networkx Graph in which vertices are the _cited_ papers. Separate
    graphs allows to analyze each timeslice separately.
    
    **Nodes** -- papers
    
    **Node attributes** -- None
    
    **Edges** -- (a, b) if a and b are cited by the same paper. 
    
    **Edge attributes** -- 'weight', number of times two papers are co-cited together.
                      
    
    Parameters
    ----------
    meta_list : list
        a list of :class:`.Paper` objects.
        
    threshold : int
        A random value provided by the user. If its greater than zero two nodes 
        should share something common.
    timeslice : int
    
        Ex: 2013, 1997 - proper year values
            
    Returns
    -------
    cocitation : networkx.Graph
        A cocitation network.
                      
    Notes
    -----
    should be able to specify a threshold -- number of co-citations required to 
    draw an edge.

    
    """
    
    cocitation_graph = nx.Graph(type='author_cocitation')
     
    # We'll use tuples as keys. Values are the number of times each pair
    #  of papers is co-cited.   
    
    cocitations = {}    

    for paper in meta_list:
        # Some papers don't have citations.
        if paper['citations'] is not None:
            # n is the number of papers in the provided list of Papers.
            n = len(paper['citations'])
            if n > 1:     # No point in proceeding if there is only one citation.
                for i in xrange(0, n):
                    # Start inner loop at i+1, to avoid redundancy and self-loops.
                    for j in xrange(i+1, n):
                        papers_pair     = ( paper['citations'][i]['ayjid'].upper(), paper['citations'][j]['ayjid'].upper() )                  
                        papers_pair_inv = ( paper['citations'][j]['ayjid'].upper(), paper['citations'][i]['ayjid'].upper() )                
                        # Have these papers been co-cited before?
                        # try blocks are much more efficient than checking
                        #  cocitations.keys() every time.           
                        try: 
                            cocitations[ papers_pair] += 1
                            cocitation_graph.add_node(papers_pair[0])
                            cocitation_graph.add_node(papers_pair[1]) #add the node only if KeyError is not thrown
                        except KeyError: 
                            # May have been entered in opposite order.
                            try:
                                cocitations[papers_pair_inv ] += 1
                                # Networkx will ignore add_node if those nodes are already present
                                cocitation_graph.add_node(papers_pair_inv[0]) 
                                cocitation_graph.add_node(papers_pair_inv[1]) 
                            except KeyError:
                                # First time these papers have been co-cited.
                                cocitations[papers_pair] = 1
                                cocitation_graph.add_node(papers_pair[0])   
                                cocitation_graph.add_node(papers_pair[1])    #This loop gets executed mostly
    
    for key,val in cocitations.iteritems():
        if val >= threshold : # If the weight is greater or equal to the user I/P threshold 
            cocitation_graph.add_edge(key[0],key[1]) #add edge between the 2 co-cited papers
            
    
    return cocitation_graph

#trying DAG's for citations

# for paper nodes - i.e outflow
def descendants(G, source):
    """Return all nodes reachable from `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G

    Returns
    -------
    des : set()
       The descendants of source in G
    """

    if not G.has_node(source):
        raise nx.NetworkXError("The node %s is not in the graph." % source)
    
    des = set(nx.shortest_path_length(G, source=source).keys()) - set([source])
    return des 

#For cited nodes - i.e inflow
def ancestors(G, source):
    """Return all nodes having a path to `source` in G.

    Parameters
    ----------
    G : NetworkX DiGraph
    source : node in G

    Returns
    -------
    ancestors : set()
       The ancestors of source in G
    """
    if not G.has_node(source):
        raise nx.NetworkXError("The node %s is not in the graph." % source)
    anc = set(nx.shortest_path_length(G, target=source).keys()) - set([source])
    return anc
