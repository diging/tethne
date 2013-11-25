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
    
    """
    
                    
    # Co-citation function starts here
    paper_references = {}         #keys: ayjid of each paper, values: a list of cited references of that paper (ayjid of citations) 
    for paper in meta_list:
            if paper['ayjid'] is not None:
                authors= paper['ayjid']
                #print authors, '\n'
                cit_str = "" 
                final_cit =""
                for cited_paper in paper['citations']:  
                      cit_str = cited_paper['ayjid']    # field ayjid in the citations sub-dict is going to be the vertex of the Network graph.
                      final_cit = cit_str.upper() + ',' + final_cit    # upper case
                      cit_list= final_cit.split(',')    # to create a list
                      paper_references[authors] = cit_list  # created a dictionary whose structure is given below.
                        
    #To check if its correct                    
    for key,val in paper_references.iteritems():
       # print key,'->',  val , '\n'
        pass


    # Example
    #{CHEN T 2013 ADVANCES IN ENGINEERING SOFTWARE : ['Zhang QF 2004 ENG COMPUTATION', 'Witten IH 2005 DATA MINING PRACTICA', 'Tu ZG 2004 IEEE T EVOLUT COMPUT', 
                                                     #'Toksari MD 2006 APPL MATH COMPUT', 'Schwefel H-P 1977 NUMERICAL OPTIMIZATI', 'Rechenberg I. 1973 EVOLUTIONSSTRATEGIE'] }
        
    papers = paper_references.keys()
    references = paper_references.values()

    for each_paper in papers:
                no_of_references= len(paper_references[each_paper]) # how many reference papers in each 'article'
                reference_list = paper_references[each_paper]  # create a list to traverse pairs of references,
                print reference_list
                print no_of_references , '---------' , '\n'
                for i in range(no_of_references) :
                        for j in range(no_of_references-1) :
                            #print reference_list[i], ',', reference_list[j]
                               # yet to do
                               #Here I need to pick up pairs of i and j from the reference_list and compare it with the other paper's cited references. 
                               #if I am able to find the cited pair in another paper, I keep increasing the weight/index.
                               #Add 2 nodes i and j , when the pair i and j has traversed the full list of references and add an edge between themby checking the condition if index>= threshold.
                            pass  