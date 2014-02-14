"""
Methods for generating networks in which papers are vertices.

Methods
```````

.. autosummary::

   author_coupling
   bibliographic_coupling
   cocitation
   direct_citation   
"""

import networkx as nx
import tethne.utilities as util
import helpers as hp
import operator
import tethne.data as ds

def direct_citation(doc_list, node_id='ayjid', node_attribs=['date']):
    """
    Create a traditional directed citation network.

    Direct-citation graphs are `directed acyclic graphs`__ in which vertices are
    documents, and each (directed) edge represents a citation of the target 
    paper by the source paper. The :func:`.networks.papers.direct_citation` 
    method generates both a global citation graph, which includes all cited and 
    citing papers, and an internal citation graph that describes only citations 
    among papers in the original dataset.

    .. _dag: http://en.wikipedia.org/wiki/Directed_acyclic_graph

    __ dag_

    To generate direct-citation graphs, use the 
    :func:`.networks.papers.direct_citation` method. Note the size difference 
    between the global and internal citation graphs.

    .. code-block:: python

       >>> gDC, iDC = nt.papers.direct_citation(papers)
       >>> len(gDC)
       5998
       >>> len(iDC)
       163

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Documents represented by the value of node_id in 
                       :class:`.Paper` 
    Edge               From a document to a cited reference.
    Edge Attribute     Publication date of the citing document.
    ==============     =========================================================
    
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

def bibliographic_coupling(doc_list, citation_id='ayjid', threshold=1,
                           node_id='ayjid', node_attribs=['date'], 
                           weighted=False):
    """
    Generate a bibliographic coupling network.
    
    Two papers are **bibliographically coupled** when they both cite the same, 
    third, paper. You can generate a bibliographic coupling network using the 
    :func:`.networks.papers.bibliographic_coupling` method.

    .. code-block:: python

       >>> BC = nt.papers.bibliographic_coupling(papers)
       >>> BC
       <networkx.classes.graph.Graph object at 0x102eec710>

    Especially when working with large datasets, or disciplinarily narrow 
    literatures, it is usually helpful to set a minimum number of shared 
    citations required for two papers to be coupled. You can do this by setting 
    the **`threshold`** parameter.

    .. code-block:: python

       >>> BC = nt.papers.bibliographic_coupling(papers, threshold=1)
       >>> len(BC.edges())
       1216
       >>> BC = nt.papers.bibliographic_coupling(papers, threshold=2)
       >>> len(BC.edges())
       542

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Papers represented by node_id.
    Node Attributes    node_attribs in :class:`.Paper`
    Edge               (a,b) in E(G) if a and b share x citations where x >=
                       threshold.
    Edge Attributes    overlap: the number of citations shared
    ===============    ========================================================= 
    

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
    weighted : bool
        If True, edge attribute `overlap` is a float in {0-1} calculated as
        :math:`\cfrac{N_{ij}}{\sqrt{N_{i}N_{j}}}` where :math:`N_{i}` and 
        :math:`N_{j}` are the number of references in :class:`.Paper` *i* and 
        *j*, respectively, and :math:`N_{ij}` is the number of references 
        shared by papers *i* and *j*.

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

        for j in xrange(i+1, len(doc_list)):
            # Make a list of citation_id's for each document...
            j_list = []
            if doc_list[j]['citations'] is not None:
                for citation in doc_list[j]['citations']:
                    j_list.append(citation[citation_id])

            # ...and construct that document's node.
            node_j_attribs = util.subdict(doc_list[j], node_attribs)

            # Add nodes and edge if the citation overlap is sufficiently high.
            overlap = util.overlap(i_list, j_list)
            
            if weighted:
                if len(overlap) > 0:
                    w = (float(len(i_list)) * float(len(j_list)))**0.5
                    similarity = float(len(overlap)) / w
                else:
                    similarity = 0
            else:
                similarity = len(overlap)
                
            if similarity >= threshold:
                bcoupling.add_node(doc_list[i][node_id], node_i_attribs)
                bcoupling.add_node(doc_list[j][node_id], node_j_attribs)
                #nx.set_node_attributes(bcoupling,"",node_i_attribs)

                bcoupling.add_edge(doc_list[i][node_id],
                                   doc_list[j][node_id],
                                   similarity=similarity)
    return bcoupling

def cocitation(papers, threshold, node_id='ayjid', topn=None, verbose=False):
    """
    Generate a cocitation network.
    
    A **cocitation network** is a network in which vertices are papers, and 
    edges indicate that two papers were cited by the same third paper. 
    `CiteSpace <http://cluster.cis.drexel.edu/~cchen/citespace/doc/jasist2006.pdf>`_
    is a popular desktop application for co-citation analysis, and you can read 
    about the theory behind it 
    `here <http://cluster.cis.drexel.edu/~cchen/citespace/>`_. Co-citation
    analysis is generally performed with a temporal component, so building a
    :class:`.GraphCollection` from a :class`.DataCollection` sliced by ``date``
    is recommended.

    You can generate a co-citation network using the 
    :func:`.networks.papers.cocitation` method:

    .. code-block:: python

       >>> CC = nt.papers.cocitation(papers)
       >>> CC
       <networkx.classes.graph.Graph object at 0x102eec790>

    For large datasets, you may wish to set a minimum number of co-citations 
    required for an edge between two papers Keep in mind that all of the 
    references in a single paper are co-cited once, so a threshold of at least 
    2 is prudent. Note the dramatic decrease in the number of edges when the 
    threshold is changed from 2 to 3.

    .. code-block:: python

       >>> CC = nt.papers.cocitation(papers, threshold=2)
       >>> len(CC.edges())
       8889
       >>> CC = nt.papers.cocitation(papers, threshold=3)
       >>> len(CC.edges())
       1493    

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Cited papers represented by :class:`.Paper` ayjid.
    Edge               (a, b) if a and b are cited by the same paper.
    Edge Attributes    weight: number of times two papers are co-cited
                       together.
    ===============    =========================================================

    Parameters
    ----------
    papers : list
        a list of :class:`.Paper` objects.
    threshold : int
        Minimum number of co-citations required to create an edge.
    topn : int or None
        If provided, only the topn most cited papers will be included in the
        cocitation network. Otherwise includes all cited papers.
    verbose : bool
        If True, prints status messages.

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
    citations_count = {}

    # 61670334: networks.citations.cocitation should have a "top cited"
    #  parameter.
    if topn is not None:
        parents, include, citations_count = hp.top_parents(papers, topn=topn)
        N = len(include)
    else:
        citations_count = hp.citation_count(papers)
        N = len(citations_count.keys())

    if verbose:
        print "Generating a cocitation network with " + str(N) + " nodes..."

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

    for key , val in cocitations.iteritems():
        if val >= threshold: # and key[0] in include and key[1] in include:
            cocitation_graph.add_edge(key[0], key[1], weight=val)

    if verbose:
        print "Done building co-citation graph, adding attributes..."

    # 62657522: Nodes in co-citation graph should have attribute containing
    #  number of citations.
    n_cit = { k:v for k,v in citations_count.iteritems()
                if k in cocitation_graph.nodes() }
    nx.set_node_attributes( cocitation_graph, 'citations', n_cit )

    return cocitation_graph

def author_coupling(doc_list, threshold, node_attribs, node_id='ayjid'):
    """
    Vertices are papers and edges indicates shared authorship.

    ===============    =========================================================
    Element            Description
    ===============    =========================================================
    Node               Documents, represented by node_id.
    Edge               (a,b) in E(G) if a and b share x authors and x >= 
                       threshold
    Edge Attributes    overlap: the value of x (above).
    ===============    =========================================================

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
                acoupling.add_edge(doc_list[i][node_id],
                                   doc_list[j][node_id],
                                   overlap=len(overlap))
    return acoupling