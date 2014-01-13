"""Methods for generating networks in which papers are vertices."""

import networkx as nx
import tethne.utilities as util
import tethne.data as ds
import operator

def citation_count(papers, key='ayjid', verbose=True):
    """Generates citation counts for all of the papers cited by papers.
    
    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    key : str
        Property to use as node key. Default is 'ayjid' (recommended).
    
    Returns
    -------
    counts : dict
        Citation counts for all papers cited by papers.
    """
    
    if verbose:
        print "Generating citation counts for "+str(len(papers))+" papers..."
    
    counts = {}
    for P in papers:
        if P['citations'] is not None:
            for p in P['citations']:
                try:
                    counts[p[key]] += 1
                except KeyError:
                    counts[p[key]] = 1

    return counts

def top_cited(papers, topn=20, verbose=True):
    """Generates a list of the topn most cited papers.
    
    Parameters    
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    topn : int
        Number of top-cited papers to return.
    
    Returns
    -------
    top : list
        A list of 'ayjid' keys for the topn most cited papers.
    counts : dict
        Citation counts for all papers cited by papers.        
    """
    
    if verbose:
        print "Finding top "+str(topn)+" most cited papers..."    
    
    counts = citation_count(papers, verbose=verbose)
    top = dict(sorted(counts.iteritems(),
                       key=operator.itemgetter(1),
                       reverse=True)[:topn]).keys()
    
    return top, counts
    
def top_parents(papers, topn=20, verbose=True):
    """Returns a list of :class:`.Paper` objects that cite the topn most cited
    papers."""
    
    if verbose:
        print "Getting parents of top "+str(topn)+" most cited papers."
        
    top, counts = top_cited(papers, topn=topn, verbose=verbose)
    papers = [ P for P in papers if P['citations'] is not None ]
    parents = [ P for P in papers if len(
                    set([ c['ayjid'] for c in P['citations'] ]) &
                    set(top) ) > 0 ]
                    
    if verbose:
        print "Found " + str(len(parents)) + " parents."
    return parents, top, counts
    

def direct_citation(doc_list, node_id='ayjid', *node_attribs):
    """
    Create a NetworkX directed graph based on citation records.
    
    **Nodes** -- documents represented by the value of :class:`.Paper` 
    [node_id].
    
    **Edges** -- from one document to its citation.
    
    **Edge attributes** -- date (year) of citation

    Parameters
    ----------
    doc_list : list
        A list of :class:`.Paper` instances.
        
    node_id : int
        A key from :class:`.Paper` to identify the nodes. Default is 'ayjid'.
        
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
        # Check the head.
        head_has_id = True
        if entry[node_id] is None:
            head_has_id = False

        if head_has_id:
            # Then create node to both global and internal networks.
            node_attrib_dict = util.subdict(entry, node_attribs)
            citation_network.add_node(entry[node_id], node_attrib_dict)
            citation_network_internal.add_node(entry[node_id], 
                                               node_attrib_dict) 
        if entry['citations'] is not None:
            for citation in entry['citations']:
                # Check the tail.
                tail_has_id = True
                if citation[node_id] is None:
                    tail_has_id = False

                if tail_has_id:
                    # Then create node to global but not internal network.
                    node_attrib_dict = util.subdict(citation, node_attribs)
                    citation_network.add_node(citation[node_id], 
                                              node_attrib_dict)
     
                if head_has_id and tail_has_id:
                    # Then draw an edge in the network.
                    citation_network.add_edge(entry[node_id], 
                                              citation[node_id],
                                              date=entry['date'])

                    # And check if it can be added to the internal network, too.
                    if (util.contains (doc_list, 
                                       lambda wos_obj: 
                                       wos_obj[node_id] == citation[node_id])):
                        citation_network_internal.add_edge(
                            entry[node_id], 
                            citation[node_id],
                            date=entry['date'])
        
    # Checking if both the graphs are Directed Acyclic Graphs.
    if not nx.is_directed_acyclic_graph(citation_network):
        raise nx.NetworkXError("Citation graph is not a DAG.")
    elif not nx.is_directed_acyclic_graph(citation_network_internal):
        raise nx.NetworkXError("Internal citation graph is not a DAG.")
    else:
        return citation_network, citation_network_internal 

def bibliographic_coupling(doc_list, citation_id='ayjid', threshold='1',
                           node_id='ayjid', *node_attribs):
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
        A key from :class:`.Paper` to identify the citation overlaps.  Default 
        is 'ayjid'.
    threshold : int
        Minimum number of shared citations to consider two papers "coupled".
    node_id : string
        Field in :class:`.Paper` used to identify the nodes. Default is 'ayjid'.
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

    # 'citations' is the only invalid meta_key for citation_id
    meta_keys.remove('citations')
    if citation_id not in meta_keys:
        raise KeyError('citation_id' + citation_id + ' is not a meta_dict' +
                       ' key or otherwise cannot be used to detect citation' +
                       ' overlap.')
    
    for i in xrange(len(doc_list)):
        # Make a list of citation_id's for each document...
        i_list = []
        if doc_list[i]['citations'] is not None:
            for citation in doc_list[i]['citations']:
                i_list.append(citation[citation_id])
        
        # ...and construct that document's node.
        node_i_attribs = util.subdict(doc_list[i], node_attribs)
        #print node_i_attribs
        for j in xrange(i+1, len(doc_list)):
            # Make a list of citation_id's for each document...
            j_list = []
            if doc_list[j]['citations'] is not None:
                for citation in doc_list[j]['citations']:
                    j_list.append(citation[citation_id])

            # ...and construct that document's node.
            node_j_attribs = util.subdict(doc_list[j], node_attribs)
            #print "n j ", node_j_attribs
            # Add nodes and edge if the citation overlap is sufficiently high.
            overlap = util.overlap(i_list, j_list)
            if len(overlap) >= threshold:
                bcoupling.add_node(doc_list[i][node_id], node_i_attribs)
                bcoupling.add_node(doc_list[j][node_id], node_j_attribs)
                #nx.set_node_attributes(bcoupling,"",node_i_attribs)
                
                bcoupling.add_edge(doc_list[i][node_id],
                                   doc_list[j][node_id],
                                   overlap=len(overlap))
    return bcoupling

def cocitation(papers, threshold, topn=None, verbose=True):
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
    
    **Edge attributes** -- 'weight', number of times two papers are co-cited 
    together.
                      
    
    Parameters
    ----------
    papers : list
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
    
    cocitation_graph = nx.Graph(type='cocitation')
     
    # We'll use tuples as keys. Values are the number of times each pair
    #  of papers is co-cited.   
    
    cocitations = {}    
    citations_count={}

    # 61670334: networks.citations.cocitation should have a "top cited" 
    #  parameter.    
    if topn is not None:
        parents, include, citations_count = top_parents(papers, topn=topn)
    else:
        citations_count = citation_count(papers)

    if verbose:
        print "Generating a cocitation network..."

    for paper in papers:
        if paper['citations'] is not None:  # Some papers don't have citations.
            n = len(paper['citations'])
            for i in xrange(0, n):

                paper_i = paper['citations'][i]['ayjid']
                
                if topn is not None and paper_i not in include:
                    pass
                else:
                    for j in xrange(i+1, n):
                        paper_j = paper['citations'][j]['ayjid']

                        if topn is not None and paper_j not in include:
                            pass
                        else:
                            
                            pp = ( paper_i, paper_j ) 
                            pp_inv = ( paper_j, paper_i )
                            
                            try: # Have these papers been co-cited before?
                                cocitations[pp] += 1
                            except KeyError: 
                                try: # Maybe in opposite order?
                                    cocitations[pp_inv] += 1
                                except KeyError:
                                    # First time these papers are co-cited.
                                    cocitations[pp] = 1
    
    if verbose:
        print "Co-citation matrix generated, building Graph..."
    
    for key,val in cocitations.iteritems():
        if val >= threshold: # and key[0] in include and key[1] in include:
            cocitation_graph.add_edge(key[0], key[1], weight=val)
    
    if verbose:
        print "Done building co-citation graph, adding attributes..."
        
    # 62657522: Nodes in co-citation graph should have attribute containing 
    #  number of citations.
    for key,val in citations_count.iteritems():   
        attribs = { k:v for k,v in citations_count.iteritems() 
                    if k in cocitation_graph.nodes() }
        nx.set_node_attributes( cocitation_graph, 
                                'number_of_cited_times', 
                                attribs ) 

    if verbose:
        print True
    return cocitation_graph

def author_coupling(doc_list, threshold, node_id, *node_attribs):
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
        List of fields in :class:`.Paper` to include as node attributes in 
        graph.
        
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
                #print ' final :' , a

    return acoupling

