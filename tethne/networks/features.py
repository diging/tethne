"""
Methods for building networks from terms in bibliographic records. This
includes keywords, abstract terms, etc.

.. autosummary::

   keyword_cooccurrence
   topic_coupling
"""

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

import numpy as np
import networkx as nx
from scipy.sparse import coo_matrix
from collections import Counter

def _filter(s, C, DC, N):
    if C > 5 and DC > N*0.05 and len(s) > 4:
        return True
    return False

def cooccurrence(   papers, featureset, filter=_filter, graph=True,
                    threshold=20, indexed_by='doi', **kwargs    ):
    """
    Generates a cooccurrence graph for features in ``featureset``.
    
    ``filter`` is a method applied to each feature, used to determine whether
    a feature should be included in the graph **before** co-occurrence values
    are generated. This can cut down on computational expense. ``filter`` should
    accept the following parameters:
    
    =========   ================================================================
    Parameter   Description
    =========   ================================================================
    ``s``       Representation of the feature (e.g. a string).
    ``C``       The overall frequency of the feature in the
                :class:`.Corpus`\.
    ``DC``      The number of documents in which the feature occurs.
    ``N``       Total number of documents in the :class:`.Corpus`\.
    =========   ================================================================
    
    The default filter is:
    
    .. code-block:: python
    
       >>> def _filter(s, C, DC, N):
       ...     if C > 5 and DC > N*0.05 and len(s) > 4:
       ...         return True
       ...     return False
    
    
    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    featurset : dict
        A featureset from a :class:`.Corpus`\.
    filter : method
        Method applied to each feature; should return True if the feature should
        be included, and False otherwise. See above.
    graph : bool
        (default: True) If False, returns a dictionary of co-occurrence values
        instead of a Graph.
    threshold : int
        (default: 20) Minimum co-occurrence value for inclusion in the Graph. 
        If ``graph`` is False, this has no effect.
    indexed_by : str
        (default: 'doi') Field in :class:`.Paper` used as indexing values in 
        ``featureset``.
        
    Returns
    -------
    networkx.Graph or dict
        See ``graph`` parameter, above.
    """

    if filter is None:  # Turns filtering off (returns True for everything).
        logger.debug('Filtering is disabled.')
        def filter(*args, **kwargs): return True
    
    features = featureset['features']
    index = featureset['index']
    counts = featureset['counts']
    dCounts = featureset['documentCounts']
    
    # Apply the filter to the featureset.
    subset = [ f for f,s in index.iteritems()   # Feature indices and strings.
                    if filter(s, counts[f], dCounts[f], len(papers)) ]

    ecounts = Counter()     # { (f_i, f_j) : int(cc) }
    for paper in papers:
        p = paper[indexed_by]   # features is keyed by paper ID.
        try:                    # Not all papers have features data.
            fvect = features[p]
        except KeyError:        # Raised when there are no data for that paper.
            continue

        feats,vals = zip(*fvect)
        feats = list(set(feats) & set(subset))  # Only keep filtered features.
        Nfeats = len(feats)

        # Generate the upper half of the co-occurrence matrix.
        for i in xrange(1,Nfeats):
            for e in zip(feats, feats[i:]):
                e_ = tuple(sorted(e))   # Matrix is symmetric.
                ecounts[e_] += 1

    if not graph:
        logger.debug('No graph; return coocurrence values only.')
        return ecounts

    else:   # Build an undirected graph, with co-occurrence values as weights.
        logger.debug('Building a graph, with co-occurrence values as weights.')
        g = nx.Graph()
        for e,co in ecounts.iteritems():
            if co >= threshold:
                g.add_edge(e[0], e[1], weight=co)

        # Add node labels.
        labels = { k:v for k,v in index.iteritems() if k in g.nodes() }
        nx.set_node_attributes(g, 'label', labels)

        return g


def mutual_information( papers, featureset, filter=None,
                        threshold=0.5, indexed_by='doi', **kwargs   ):
    """
    Generates a graph of features in ``featureset`` based on normalized 
    `pointwise mutual information (nPMI)
    <http://en.wikipedia.org/wiki/Pointwise_mutual_information>`_.
    
    .. math::
    
       nPMI(i,j)=\\frac{log(\\frac{p_{ij}}{p_i*p_j})}{-1*log(p_{ij})}
    
    ...where :math:`p_i` and :math:`p_j` are the probabilities that features
    *i* and *j* will occur in a document (independently), and :math:`p_{ij}` is
    the probability that those two features will occur in the same document.
    
    
    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` instances.
    featurset : dict
        A featureset from a :class:`.Corpus`\.
    filter : method
        Method applied to each feature prior to calculating co-occurrence.
        See :func:`.cooccurrence`\.
    threshold : float
        (default: 0.5) Minimum nPMI for inclusion the graph.
    indexed_by : str
        (default: 'doi') Field in :class:`.Paper` used as indexing values in
        ``featureset``.
        
    Returns
    -------
    graph : networkx.Graph
    
    Examples
    --------
    
    Using wordcount data from JSTOR Data-for-Research, we can generate a nPMI
    network as follows:
    
    .. code-block:: python
    
       >>> from tethne.readers import dfr               # Prep corpus.
       >>> MyCorpus = dfr.read_corpus(datapath+'/dfr', features=['uni'])
       >>> MyCorpus.filter_features('unigrams', 'u_filtered')
       >>> corpus.transform('u_filtered', 'u_tfidf')
       
       >>> from tethne.networks import features         # Build graph.
       >>> graph = features.mutual_information(MyCorpus.all_papers(), 'u_tfidf')
       
       >>> from tethne.writers.graph import to_graphml  # Export graph.
       >>> to_graphml(graph, '/path/to/my/graph.graphml')
       
    Here's a small cluster from a similar graph, visualized in Cytoscape:
    
    .. figure:: _static/images/nPMI_phosphorus.png
       :width: 400
       :align: center
       
       Edge weight and opacity indicate nPMI values.
       
    
    """
    logger.debug('Build a pointwise mutual information graph.')
    
    graph = nx.Graph()
    ecounts = cooccurrence( papers, featureset, filter=filter,
                            graph=False, indexed_by=indexed_by  )
    logger.debug('Got {0} cooccurrence values'.format(len(ecounts)))
    
    features = featureset['features']
    index = featureset['index']
    counts = featureset['counts']
    dCounts = featureset['documentCounts']

    for k,v in ecounts.iteritems():
        p_i = min(float(dCounts[k[0]])/float(len(papers)), 1.0)
        p_j = min(float(dCounts[k[1]])/float(len(papers)), 1.0)
        p_ij = min(float(v)/float(len(papers)), 1.0)
        P = _nPMI(p_ij, p_i, p_j)

        if P >= threshold:
            
            graph.add_edge(k[0], k[1], weight=float(P))
    logger.debug('Added {0} edges to graph.'.format(len(graph.edges())))

    labels = { k:v for k,v in index.iteritems() if k in graph.nodes() }
    nx.set_node_attributes(graph, 'label', labels)
    logger.debug('Added labels to {0} nodes.'.format(len(labels)))

    return graph

def _nPMI(p_ij, p_i, p_j):
    return ( np.log( p_ij/(p_i*p_j) ) ) / ( -1* np.log(p_ij) )

def keyword_cooccurrence(papers, threshold, connected=False, **kwargs):
    """
    Generates a keyword cooccurrence network.

    Parameters
    ----------
    papers : list
        A list of :class:`.Paper` objects.
    threshold : int
        Minimum number of occurrences for a keyword pair to appear in graph.
    connected : bool
        If True, returns only the largest connected component.

    Returns
    -------
    k_coccurrence :  networkx.Graph
        A keyword coccurrence network.
        
    Notes
    -----
    Not thoroughly tested.
    
    **TODO**
    
    * Incorporate this into the featureset framework.

    """

    # Extract keywords from papers.
    keywords = {}
    for entry in papers:
        if 'keywords' in entry.keys():
            keywords[entry['wosid']] = entry['keywords']

    # Generate the complete set of keywords in the dataset.
    wordset = set([])
    for entry in papers:
        try:
            for kw in keywords[entry['wosid']]:
                wordset.add(kw)
        except:
            pass

    # Mapping of integer indices to keywords.
    i = 0
    dictionary = {}
    dictionary_ = {}
    for word in wordset:
        dictionary[word] = i
        dictionary_[i] = word
        i += 1

    cooccurrence = np.zeros((len(wordset), len(wordset)))
    frequencies = np.zeros((len(wordset),))

    for entry in papers:
        if entry['keywords'] in keywords.keys():
            for word in keywords[entry['wosid']]:
                frequencies[dictionary[word]] += 1
                for word_ in keywords[entry['wosid']]:
                    i = dictionary[word]
                    j = dictionary[word_]
                    if i != j:
                        cooccurrence[i, j] += 1

    G = nx.Graph()
    for i in xrange(len(wordset)):
        for j in xrange(i, len(wordset)):
            if cooccurrence[i, j] > 1 and i != j:
                G.add_edge(dictionary_[i], dictionary_[j], weight=int(cooccurrence[i, j]))

    if connected:   # Return only the first connected component.
        return nx.connected_component_subgraphs(G)[0]
    else:
        return G    # Return the whole graph.

def topic_coupling(model, threshold=0.005, **kwargs):
    """
    Creates a network of words connected by implication in a common topic(s).

    Parameters
    ----------
    model : :class:`.LDAModel`
    threshold : float
        Minimum P(W|T) for coupling.

    Returns
    -------
    tc : networkx.Graph
        A topic-coupling graph, where nodes are terms.
        
    Examples
    --------
    
    .. code-block:: python

      >>> from tethne.networks import features
      >>> g = features.topic_coupling(MyLDAModel, threshold=0.015)

    Here's a similar network, visualized in Cytoscape:
    
    .. image:: _static/images/mallet/semantic_network.png
       :width: 600
       :align: center
       
    For details, see :ref:`mallet-tutorial`.

    """

    Z = model.Z
    W = model.W
    
    logger.debug('topic_coupling for {0} features, {1} topics.'.format(W,Z))
    logger.debug('threshold: {0}'.format(threshold))

    edges = {}
    for z in xrange(Z):
        word_sub = []
        dimension = model.dimension(z, asmatrix=True)
        for w in dimension.nonzero()[1]:
            if dimension[0,w] >= threshold:
                word_sub.append(w)
        
        logger.debug('topic {0} generated {1} edges.'.format(z, len(word_sub)))

        for i in xrange(len(word_sub)):
            for j in xrange(i+1, len(word_sub)):
                w_i = word_sub[i]
                w_j = word_sub[j]
                p_i = dimension[0, w_i]
                p_j = dimension[0, w_j]
                try:
                    edges[(w_i,w_j)].append((z, (p_i+p_j)/2))
                except KeyError:
                    edges[(w_i,w_j)] = [(z, (p_i+p_j)/2)]
                    
    logger.debug('generated {0} edges'.format(len(edges)))
    
    tc = nx.Graph()

    for e, topics in edges.iteritems():
        weight = sum( [ t[1] for t in topics ] ) / Z
        i_id = model.vocabulary[e[0]]
        j_id = model.vocabulary[e[1]]
        tc.add_edge(i_id, j_id, weight=float(weight), 
                                topics=[t[0] for t in topics])
    
    logger.debug('done')

    return tc