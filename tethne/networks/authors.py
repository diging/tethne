"""Methods for generating networks in which authors are vertices."""

import networkx as nx
import tethne.utilities as util
import tethne.data as ds
from collections import defaultdict

# MACRO for printing the 'print' statement values.
# 0 prints nothing in the console.
# 1 prints all print statements in the console.
DEBUG = 1

def author_papers(doc_list, paper_id, *paper_attribs):
    """
    Generate an author_papers network NetworkX directed graph.

    **Nodes** -- Two kinds of nodes with distinguishing "type" attributes.
        * type = paper    - a paper in doc_list
        * type = person   - a person in doc_list

    Papers also have node attributes defined by paper_attribs.

    **Edges** -- Directed, Author -> his/her Paper

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
    author_papers_graph : networkx.DiGraph
        A DiGraph 'author_papers_graph'.

    Raises
    ------
    KeyError : Raised when paper_id is not present in Papers.

    """
    author_papers_graph = nx.DiGraph(type='author_papers')

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
        author_papers_graph.add_node(entry[paper_id], paper_attrib_dict)

        authors = util.concat_list(entry['aulast'], entry['auinit'], ' ')
        for i in xrange(len(authors)):
            # Add person node.
            author_papers_graph.add_node(authors[i], type="person")
            # Draw edges.
            author_papers_graph.add_edge(authors[i], entry[paper_id],
                                   date=entry['date'])

    return author_papers_graph

def coauthors(papers, *edge_attribs):
    """
    Generate a co-author network.

    **Nodes** -- author names

    **Node attributes** -- none

    **Edges** -- (a,b) in E(G) if a and b are coauthors on the same paper.

    Parameters
    ----------
    papers : list
        A list of :class:`Paper` instances.
    edge_attribs : list
        List of edge_attributes specifying which :class:`.Paper` keys (from the
        co-authored paper) to use as edge attributes.

    Returns
    -------
    coauthors_graph : networkx.MultiGraph
        A co-authorship network.

    Notes
    -----
    TODO: Check whether papers contains :class:`.Paper` instances, and raise
    an exception if not.

    """
    coauthors_graph = nx.Graph(type='coauthors')
    edge_att = {}
    #edge_listdict={}
    coauthor_dict = {}
    for entry in papers:
        if entry['aulast'] is not None:
            # edge_att dictionary has the atributes given by user input \
            # for any edges that get added
            edge_att = util.subdict(entry, edge_attribs)
            # make a new list of aulast, auinit names
            full_names = util.concat_list(entry['aulast'],
                                          entry['auinit'],
                                          ' ')
            for a in xrange(len(full_names)):
                for b in xrange(a+1 , len(entry['aulast'])):
                    #Create tuples of authors names and authors names inverse \
                    #They will be the keys of coauthor_dict.
                    authors = full_names[a], full_names[b]
                    authors_inv = full_names[b], full_names[a]
                    #To check if the authors are already in the 'dict' keys
                    if(authors in coauthor_dict.keys()):
                        # Now create a dict of lists
                        # i.e., append the current values of edge attributes\
                        # to values of same author pair if already present.
                        # use the defaultdict python module
                        edge_listdict = defaultdict(list)
                        for combined_dict in (coauthor_dict[authors], edge_att):
                            for key, val in combined_dict.iteritems():
                                edge_listdict[key].append(val)
                        # To check if authors keys are in same order
                        try:
                            coauthor_dict[authors] = edge_listdict
                        except KeyError:
                            coauthor_dict[authors] = edge_att

                    # Checking if the authors names in the dict keys are in \
                    # inverse order. This is not handled in the aforegiven \
                    # loop for some specific reason.
                    elif(authors_inv in coauthor_dict.keys()):
                        # Now create a list of dicts
                        # i.e., append the current values of edge attributes\
                        # to the edge attribs of same author pair
                        # if already present.
                        # use the defaultdict python module
                        edge_listdict = defaultdict(list)
                        for combined_dict in (coauthor_dict[authors_inv], \
                                              edge_att):
                            for key, val in combined_dict.iteritems():
                                edge_listdict[key].append(val)
                        # To check if authors_inv keys are in same order
                        try:
                            coauthor_dict[authors_inv] = edge_listdict
                        except KeyError:
                            coauthor_dict[authors_inv] = edge_att
                    #if the authors or authors_inv are already not keys of \
                    # coauhor dict, then add them.
                    else:
                        try:
                            coauthor_dict[authors] = edge_att
                        except KeyError:
                            try:
                                coauthor_dict[authors_inv] = edge_att
                            except:
                                coauthor_dict[authors] = edge_att
    #add edges with specified edge attributes
    for key, val in coauthor_dict.iteritems():
        #print "Starting the Map:",key , "---- >" ,val
        coauthors_graph.add_edge(key[0],
        key[1],
        attr_dict =  val)

    return coauthors_graph

def author_institution(Papers, *edge_attribs):
    """
    Generate a bi-partite graph with people and institutions as vertices, and
    edges indicating affiliation. This may be slightly ambiguous for WoS data
    where num authors != num institutions.

    **Nodes** -- author names

    **Node attributes** -- none

    **Edges** -- (a,b) in E(G) if a and b are authors on the same paper.

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
                ins_list = auth_inst[au]
                for ins_str in ins_list:
                  #add node of type 'institutions'
                    author_institution_graph.add_node(ins_str, \
                                                      type='institution')
                  #print au ,'---->' , ins_str
                    author_institution_graph.add_edge(au, ins_str, \
                                              attr_dict=edge_attrib_dict)


    return author_institution_graph


def author_coinstitution(Papers, threshold):

    """
    Create a graph with people as vertices, and edges indicating affiliation
    with the same institution. This may be slightly ambiguous for WoS data
    where num authors != num institutions.

    **Nodes** -- Authors.

    **Node attributes** -- type (string). 'author' or 'institution'.

    **Edges** -- (a, b) where a and b are affiliated with the same institution.

    **Edge attributes** - overlap (int). number of shared institutions.

    Parameters
    ----------
    Papers : list
    a list of wos_objects.
    threshold : A random value provided by the user.
                If its greater than zero,two nodes
                should share something common.

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
            #coinstitution.add_node(authors[i],type ='author')
            for j in xrange(len(authors)):
                if i != j:
                     #compare 2 author dict elements
                    overlap = (set(author_institutions[authors[i]])
                                &
                                set(author_institutions[authors[j]]))
                    if len(overlap) >= threshold:
                        #commented these because 'add_edge' adds nodes aswell.
                        #coinstitution.add_node(authors[i],type ='author')
                        #coinstitution.add_node(authors[j],type ='author')
                        #print authors[i] + "->" + authors[j]
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
    Should be able to specify a threshold -- number of co-citations required to
    draw an edge.

    """

    author_cocitations = nx.Graph(type='author_cocitation')

    # We'll use tuples as keys. Values are the number of times each pair
    # of 2 authors is co-cited.

    cocitations = {}
    delim = ' '

    for paper in meta_list:
        #print '----New paper---'
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
                    
                    # commented the following line
                    # because of some issues in MAP.
                    # Now uncommenting back as issue is handled in wos.py
                    ai_i_str=\
                        ''.join(map(str,(paper['citations'][i]['auinit'])))
                    #-------------------------------------------------
                    # last_name_list = paper['citations'][i]['auinit']
                    # Last name of author i, converted to str.
                    # ai_i_str = str(last_name_list).strip('[]')
                    #-------------------------------------------------
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
                        
                        # commented the following line \
                        # because of some issues in MAP.
                        # Now uncommenting back as issue is handled in wos.py
                        ai_j_str=''.join(map(str, \
                                           (paper['citations'][j]['auinit'])))
                        #-------------------------------------------------
                        # last_name_list = paper['citations'][j]['auinit']
                        # last name of author i, converted to str.
                        # ai_j_str = str(last_name_list).strip('[]')
                        #-------------------------------------------------
                        
                        # Making it a tuple so that it becomes the key for
                        # cocitations dict
                        author_j_str = al_j_str + delim + ai_j_str

                        # 2 tuples which are going to be the keys of the dict.
                        authors_pair = (author_i_str.upper(), \
                                                author_j_str.upper())
                        authors_pair_inv = (author_j_str.upper(), \
                                                author_i_str.upper())
                        
                        if DEBUG:
                            print "Authors Pairs: ",authors_pair
                            print "Authors Pairs inv: ",authors_pair_inv

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
