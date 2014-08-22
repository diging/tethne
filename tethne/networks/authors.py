"""
Methods for generating networks in which authors are vertices.

.. autosummary::
   :nosignatures:

   author_cocitation
   author_coinstitution
   author_institution
   author_papers
   coauthors

"""

import networkx as nx
from .. import utilities as util
from collections import defaultdict, Counter
from ..classes import Paper


import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

def author_papers(papers, node_id='ayjid', paper_attribs=[], **kwargs):
    """
    Generate an author_papers network NetworkX directed graph.

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Two kinds of nodes with distinguishing "type" attributes:
                       * type = paper    - a paper in papers
                       * type = person   - a person in papers
                       Papers node attributes defined by paper_attribs.
    Edge               Directed, Author -> his/her Paper.
    ==============     =========================================================

    Parameters
    ----------
    papers : list
        A list of wos_objects.
    node_id : string
        A key from :class:`.Paper` used to identify the nodes.
    paper_attribs : list
        List of user-provided optional arguments apart from the provided
        positional arguments.

    Returns
    -------
    author_papers_graph : networkx.DiGraph
        A DiGraph 'author_papers_graph'.

    Raises
    ------
    KeyError : Raised when node_id is not present in Papers.

    """
    author_papers_graph = nx.DiGraph(type='author_papers')

    # Validate node_id.
    meta_dict = Paper()
    meta_keys = meta_dict.keys()
    meta_keys.remove('citations')
    if node_id not in meta_keys:
        raise KeyError('node_id' + node_id + ' cannot be used to identify' +
                       ' papers.')
    for entry in papers:
        # Define paper_attribute dictionary.
        paper_attrib_dict = util.subdict(entry, paper_attribs)
        paper_attrib_dict['type'] = 'paper'
        # Add paper node with attributes.
        author_papers_graph.add_node(entry[node_id], paper_attrib_dict)

        authors = util.concat_list(entry['aulast'], entry['auinit'], ' ')
        for i in xrange(len(authors)):
            # Add person node.
            author_papers_graph.add_node(authors[i], type="person")
            # Draw edges.
            author_papers_graph.add_edge(authors[i], entry[node_id],
                                   date=entry['date'])

    return author_papers_graph

def institutions(papers, threshold=1, edge_attrbs=['ayjid'], 
                 node_attribs=['authors'], geocode=False, **kwargs):
    """
    Generates an institutional network based on coauthorship.
    
    An edge is drawn between two institutional vertices whenever two authors,
    one at each respective institution, coauthor a :class:`.Paper`\.

    .. code-block:: python
    
       >>> I = nt.authors.institutions(papers)
       >>> I
       <networkx.classes.graph.Graph object at 0x10d94cfd0>
       

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Institution name and location.
    Edges              (a,b) in E(G) if coauthors R and S are affiliated with 
                       institutions a and b, respectively.
    ==============     =========================================================
    
    Parameters
    ----------
    papers : list
        A list of :class:`Paper` instances.
    threshold : int
        Minimum number of co-citations required for an edge. (default: 1)
    edge_attribs : list
        List of edge_attributes specifying which :class:`.Paper` keys (from the
        co-authored paper) to use as edge attributes. (default: ['ayjid'])
    node_attribs : list
        List of attributes to attach to author nodes. Presently limited to
        'institution'.
    geocode : bool
        If True, attempts to geocode institutional information for authors, and
        adds latitude, longitude, and precision attributes to each node.
    
    Returns
    -------
    G : networkx.Graph
        An institutional co-authorship network.    
    """

    G = nx.Graph(type='institutions')
    ca = coauthors(papers, threshold=threshold, geocode=geocode, **kwargs)
    
    edges = {}
    nodes = {   'latitude': {},
                'longitude': {},
                'precision': {},
                'authors': {}       }
    
    defaultEdge = { 'authors': list,
                    'ayjid': list,
                    'weight': int     }
    
    for edge in ca.edges(data=True):
        n = { 0: ca.node[edge[0]],
              1: ca.node[edge[1]] }
        
        # If there is no institutional information for an author, skip the edge.
        skip = False    
        try:
            inst = { 0:n[0]['institution'],
                     1:n[1]['institution'] }
        except KeyError:
            skip = True
        
        if not skip:
            if geocode:
                # Add geodata from most recent author at this institution.
                for i in (0,1):
                    nodes['latitude'][inst[i]] = n[i]['latitude']
                    nodes['longitude'][inst[i]] = n[i]['longitude']
                    nodes['precision'][inst[i]] = n[i]['precision']

            # try-except blocks to avoid 'key in dict.keys()' pattern.
            try:
                assert type(edges[(inst[0],inst[1])]) is dict
                key = (inst[0],inst[1])
            except (AssertionError, KeyError):
                try:
                    assert type(edges[(inst[1],inst[0])]) is dict
                    key = (inst[1],inst[0])
                except (AssertionError, KeyError):
                    # Instantiate types to avoid reference issues.
                    edges[(inst[0],inst[1])] = { k:v() for k,v 
                                                   in defaultEdge.iteritems() }
                    key = (inst[0],inst[1])

            # Add authors to institution nodes.
            for i in (0,1):
                try:
                    nodes['authors'][inst[i]].add(edge[i])
                except KeyError:
                    nodes['authors'][inst[i]] = set([edge[i]])

            edges[key]['authors'] += [ (edge[0], edge[1]) ]
            edges[key]['ayjid'] += edge[2]['ayjid']
            edges[key]['weight'] += edge[2]['weight']
    
    for edge, attributes in edges.iteritems():
        G.add_edge(edge[0], edge[1], **attributes)
    
    for key, values in nodes.iteritems():
        if key is 'authors':    # Since many writers don't support sets.
            values = { k:list(v) for k,v in values.iteritems() }
        nx.set_node_attributes(G, key, values)
    nx.set_node_attributes(G, 'size', { k:len(v) for k,v 
                                            in nodes['authors'].iteritems() })
        
    return G

def coauthors(  papers, threshold=1, edge_attribs=['ayjid'],
                node_attribs=['institution'], geocode=False, auuri=False,
                                                                **kwargs    ):
    """
    Generate a co-author network.

    As the name suggests, edges are drawn between two author-vertices in the
    case that those authors published a paper together. Co-authorship networks
    are popular models for studying patterns of collaboration in scientific
    communities.

    To generate a co-authorship network, use the
    :func:`.networks.authors.coauthors` method:
    
    Author institutional affiliation is included as a node attribute, if 
    possible.

    .. code-block:: python

       >>> CA = nt.authors.coauthors(papers)
       >>> CA
       <networkx.classes.graph.Graph object at 0x10d94cfd0>

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Author name.
    Edges              (a,b) in E(G) if a and b are coauthors on the same paper.
    ==============     =========================================================

    Parameters
    ----------
    papers : list
        A list of :class:`Paper` instances.
    threshold : int
        Minimum number of co-citations required for an edge. (default: 1)
    edge_attribs : list
        List of edge_attributes specifying which :class:`.Paper` keys (from the
        co-authored paper) to use as edge attributes. (default: ['ayjid'])
    node_attribs : list
        List of attributes to attach to author nodes. Presently limited to
        'institution'.
    geocode : bool
        If True, attempts to geocode institutional information for authors, and
        adds latitude, longitude, and precision attributes to each node.        

    Returns
    -------
    G : networkx.Graph
        A co-authorship network.

    """

    # TODO: Check whether papers contains :class:`.Paper` instances, and raise
    #  an exception if not.
    
    caller = logger.findCaller()
    logger.debug("{0}: start building coauthors graph".format(caller[1]))

    G = nx.Graph(type='coauthors')
    edge_att = {}
    #edge_listdict={}
    coauthor_dict = {}

    author_inst = {}
    
    for entry in papers:
        if auuri:
            authors = entry['auuri']
        else:
            authors = entry.authors()

        if authors is not None:
            # edge_att dictionary has the atributes given by user input
            #  for any edges that get added
            edge_att = util.subdict(entry, edge_attribs)

            Nauthors = len(authors)
            for a in xrange(Nauthors):
                # Update global author-institution mappings.
                n = authors[a]
                if entry['institutions'] is not None:
                    try:
                        inst = entry['institutions'][n]
                        try:
                            author_inst[n] += inst
                        except KeyError:
                            author_inst[n] = inst
                    except KeyError:
                        pass
                    
                for b in xrange(a+1, Nauthors):
                    au_pair = tuple(sorted((authors[a], authors[b])))
                    
                    if au_pair not in coauthor_dict:
                        coauthor_dict[au_pair] = { k:[] for k in edge_att.keys() }
                        coauthor_dict[au_pair]['weight'] = 0
                    coauthor_dict[au_pair]['weight'] += 1

                    for k, v in edge_att.iteritems():
                        coauthor_dict[au_pair][k].append(v)

    caller = logger.findCaller()
    logger.debug("{0}: done iterating over papers".format(caller[1]))
    
    # Add edges with specified edge attributes.
    for key, val in coauthor_dict.iteritems():
        if val['weight'] >= threshold:
            G.add_edge(key[0], key[1], attr_dict=val)

    caller = logger.findCaller()
    logger.debug("{0}: done adding edges".format(caller[1]))
        
    # Load GeoCoder here, to avoid excessive cache read/write operations.
    if geocode:
        from tethne.services.geocode import GoogleCoder
        gc = GoogleCoder()
        caller = logger.findCaller()
        logger.debug("{0}: loaded geocoder".format(caller[1]))
    
    if 'institution' in node_attribs:
        # Include institutional affiliations as node attributes, if possible.
        
        # Find most likely institution for each author. This won't work well if 
        #  the author only occurs once in the dataset and there was no explicit
        #  author-instituion mapping.
        
        caller = logger.findCaller()
        logger.debug("{0}: adding institutional information".format(caller[1]))
        
        for k,v in author_inst.iteritems():
            top_inst = max(Counter(v))
            try:    # If an author has no coauthors, they will not appear in G.
                G.node[k]['institution'] = top_inst
                
                # Optionally, include positional information, if possible.
                if geocode:

                    location = gc.code_this(top_inst)
            
                    if location is None:
                        location = gc.code_this(top_inst.split(',')[-1])
                        precision = 'country'
                    else:
                        precision = 'institution'
                    if location is not None:
                        G.node[k]['latitude'] = location.latitude
                        G.node[k]['longitude'] = location.longitude
                        G.node[k]['precision'] = precision
        
            except KeyError:
                pass
    
    caller = logger.findCaller()
    logger.debug("{0}: done building coauthors graph".format(caller[1]))
    
    return G

def author_institution(Papers, edge_attribs=[], **kwargs):
    """
    Generate a bi-partite graph connecting authors and their institutions.
    
    This may be slightly ambiguous for WoS data where there is no explicit
    author-institution mapping. Edge weights are the number of co-associations
    between an author and an institution, which should help resolve this
    ambiguity (the more data the better).

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Author name.
    Edge               (a,b) in E(G) if a and b are authors on the same paper.
    ==============     =========================================================

    Parameters
    ----------
    Papers : list
        A list of :class:`.Paper` instances.
    edge_attribs : list
        List of edge_attributes specifying which :class:`.Paper` keys (from the
        authored paper) to use as edge attributes. For example, the 'date' key
        in :class:`.Paper` .

    Returns
    -------
    author_institution_graph : networkx.MultiGraph
        A graph describing institutional affiliations of authors in the corpus.
    """

    author_institution_graph = nx.MultiGraph(type='author_institution')
    #The Field in Papers which corresponds to authors and affliated institutions
    # is "institutions"
    # { 'institutions' : { Authors:[institutions_list]}}
    for paper in Papers:
        if paper['institutions'] is not None:
            auth_inst = paper['institutions']
            edge_attrib_dict = util.subdict(paper, edge_attribs)
            authors = auth_inst.keys()
            for au in authors:
                #add node of type 'author'
                author_institution_graph.add_node(au, type='author')
                ins_list = Counter(auth_inst[au])
                for ins_str,count in ins_list.iteritems():
                    # Add node of type 'institutions'.
                    author_institution_graph.add_node(ins_str, \
                                                      type='institution')

                    author_institution_graph.add_edge(au, ins_str, \
                                              attr_dict=edge_attrib_dict, \
                                              weight=count )


    return author_institution_graph

def author_coinstitution(Papers, threshold=1, **kwargs):
    """
    Generate a co-institution graph, where edges indicate shared affiliation.

    Some bibliographic datasets, including data from the Web of Science,
    includes the institutional affiliations of authors. In a co-institution
    graph, two authors (vertices) have an edge between them if they share an
    institutional affiliation in the dataset. Note that data about institutional
    affiliations varies in the WoS database so this will yield more reliable
    results for more recent publications.

    To generate a co-institution network, use the
    :func:`.networks.authors.author_coinstitution` method:

    .. code-block:: python

       >>> ACI = nt.authors.author_coinstitution(papers)
       >>> ACI
       <networkx.classes.graph.Graph object at 0x106571190>

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Node               Authors.
    Node Attribute     type (string). 'author' or 'institution'.
    Edges              (a, b) where a and b are affiliated with the same
                       institution.
    Edge attribute     overlap (int). number of shared institutions.
    ==============     =========================================================

    Parameters
    ----------
    Papers : list
        A list of wos_objects.
    threshold : int
        Minimum institutional overlap required for an edge.

    Returns
    -------
    coinstitution : NetworkX :class:`.graph`
        A coinstitution network.

    """
    coinstitution = nx.Graph(type='author_coinstitution')


    # The Field in Papers which corresponds to the affiliation is "institutions"
    #  { 'institutions' : { Authors:[institutions_list]}}
    author_institutions = {}  # keys: author names, values: list of institutions
    for paper in Papers:
        if paper['institutions'] is not None:
            for key, value in paper['institutions'].iteritems():
                try:
                    author_institutions[key] += value
                except KeyError:
                    author_institutions[key] = value
        authors = author_institutions.keys()
        for i in xrange(len(authors)):
            for j in xrange(len(authors)):
                if i != j:
                    # Compare 2 author dict elements.
                    overlap = (set(author_institutions[authors[i]])
                                &
                                set(author_institutions[authors[j]]))
                    if len(overlap) >= threshold:
                        coinstitution.add_edge(authors[i], authors[j], \
                                               overlap=len(overlap))
                    else :
                        pass
        #62809656
        attribs_dict = {}
        for node in coinstitution.nodes():
            attribs_dict[node] = 'author'
        nx.set_node_attributes( coinstitution, 'type', attribs_dict )


    return coinstitution

def author_cocitation(papers, threshold=1, **kwargs):
    """
    Generates an author co-citation network; edges indicate co-citation of
    authors' papers.

    Similar to :func:`.papers.cocitation`\, except that vertices are authors
    rather than papers. To generate an author co-citation network, use the
    :func:`.networks.authors.author_cocitation` method:

    .. code-block:: python

       >>> ACC = nt.authors.author_cocitation(papers)
       >>> ACC
       <networkx.classes.graph.Graph object at 0x106571190>

    ==============     =========================================================
    Element            Description
    ==============     =========================================================
    Nodes              Author name.
    Edge               (a, b) if a and b are referenced by the same paper in
                       papers
    Edge attribute     'weight', the number of papers that co-cite a and b.
    ==============     =========================================================

    Parameters
    ----------
    papers : list
        a list of :class:`.Paper` objects.
    threshold : int
        Minimum number of co-citations required to create an edge between
        authors.

    Returns
    -------
    cocitation : :class:`.networkx.Graph`
        A cocitation network.

    """

    author_cocitations = nx.Graph(type='author_cocitation')

    # We'll use tuples as keys. Values are the number of times each pair
    # of 2 authors is co-cited.

    cocitations = {}
    delim = ' '

    for paper in papers:
        # Some papers don't have citations.
        if paper['citations'] is not None:
            # n is the number of papers in the provided list of Papers.
            n = len(paper['citations'])
            found_authors = []  # To avoid extra incrementation of author pairs.
            if n > 1:   # No point in proceeding if there is only one citation.
                for i in xrange(0, n):

                    # al_i_str is the author i's last name.
                    # converting list to str
                    al_i_str = ''.join(map(str, \
                                            (paper['citations'][i]['aulast'])))

                    # ai_i_str is the author i's first name
                    # converting list to str

                    ai_i_str = \
                        ''.join(map(str,(paper['citations'][i]['auinit'])))

                    # Making it a tuple,that it becomes key for cocitations dict
                    author_i_str = al_i_str + delim + ai_i_str

                    # Start inner loop at i+1,\
                    # to avoid redundancy and self-loops.

                    for j in xrange(i+1, n):
                        # al_j_str is the last name of author j
                        al_j_str = ''.join(map(str, \
                                            (paper['citations'][j]['aulast'])))

                        # ai_j_str is the author j's first name
                        # converting list to str

                        ai_j_str = ''.join(map(str, \
                                           (paper['citations'][j]['auinit'])))

                        # Making it a tuple so that it becomes the key for
                        # cocitations dict
                        author_j_str = al_j_str + delim + ai_j_str

                        # 2 tuples which are going to be the keys of the dict.
                        authors_pair = (author_i_str.upper(), \
                                                author_j_str.upper())
                        authors_pair_inv = (author_j_str.upper(), \
                                                author_i_str.upper())

                        # Have these authors been co-cited before?
                        try:
                            # check if author pair is not already \
                            # in the list and
                            # if the pair and inverse are not same. This is done
                            # to avoid drawing edges between same authors(nodes)

                            if (authors_pair not in found_authors
                                    and (authors_pair != authors_pair_inv)):
                                cocitations[authors_pair] += 1
                                found_authors.append(authors_pair)

                        except KeyError:
                            try: # May have been entered in opposite order.
                                if (authors_pair_inv not in found_authors
                                    and (authors_pair != authors_pair_inv)):
                                    cocitations[authors_pair_inv] += 1
                                    found_authors.append(authors_pair_inv)
                                # Networkx will ignore add_node
                                # if those nodes are already present
                            except KeyError:
                                # First time these papers have been co-cited.
                                cocitations[authors_pair] = 1
                                found_authors.append(authors_pair)

    # Create the network.
    for key, val in cocitations.iteritems():
        # If the weight is greater or equal to the user I/P threshold
        if val >= threshold :
            # Add edge between the 2 co-cited authors
            author_cocitations.add_edge(key[0], key[1], weight=val)

    return author_cocitations
