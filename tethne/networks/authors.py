"""Methods for generating networks in which authors are vertices."""

import networkx as nx
import tethne.utilities as util
import tethne.data as ds

def author_papers(doc_list, paper_id, *paper_attribs):
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
    KeyError : Raised when paper_id is not present in Papers.
    
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

def coauthors(papers, *edge_attribs):
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
    TODO: Check whether papers contains :class:`.Paper` instances, and raise
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

def author_institution(Papers, *edge_attribs):
    
    """
    Generate a bi-partite graph with people and institutions as vertices, and
    edges indicating affiliation. This may be slightly ambiguous for WoS data
    where num authors != num institutions.
    
    **Nodes** -- author names
    
    **Node attributes** -- none
    
    **Edges** -- (a,b) \in E(G) if a and b are authors on the same paper.
    
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
    author_institution : networkx.MultiGraph
        A graph describing institutional affiliations of authors in the corpus.
        
    """
    
    author_institution = nx.MultiGraph(type='author_institution')
    #The Field in Papers which corresponds to authors-institutions affiliation is "institutions"   
    # { 'institutions' : { Authors:[institutions_list]}}
    for paper in Papers:
        if paper['institutions'] is not None:
            auth_inst = paper['institutions']
            edge_attrib_dict = util.subdict(paper, edge_attribs)
            authors = auth_inst.keys()
            for au in authors:
                author_institution.add_node(au,type='author') #add node au
                ins_list = auth_inst[au]
                for ins_str in ins_list:   
                  author_institution.add_node(ins_str,type='institution') #add node ins  
                  #print au ,'---->' , ins_str     
                  author_institution.add_edge(au,ins_str, attr_dict=edge_attrib_dict)
                         
                          
    return author_institution


def author_coinstitution(Papers, threshold=1):
    
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
        A list of :class:`.Paper` objects.
    threshold : int
        Minimum number of shared institutions required for an edge between
        two authors.
        
    Returns
    -------
    coinstitution : NetworkX :class:`.Graph`
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
            coinstitution.add_node(authors[i],type ='author')  
            for j in xrange(len(authors)):
                if i != j:
                    overlap = set(author_institutions[authors[i]]) & set(author_institutions[authors[j]]) #compare 2 author dict elements
                    if len(overlap) >= threshold:
                        coinstitution.add_node(authors[j],type ='author')            
                        coinstitution.add_edge(authors[i], authors[j], overlap=len(overlap))
                    else :
                        pass
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