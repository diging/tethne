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
logger.setLevel('INFO')

import numpy as np
import networkx as nx
from scipy.sparse import coo_matrix
from collections import Counter

def cooccurrence(papers, featureset, filter=None, graph=True, **kwargs):
    if filter is None:
        def filter(s, C, DC, N):
            if C > 5 and DC > N*0.05 and len(s) > 4:
                return True
            return False

    graph = nx.Graph()
    
    features = featureset['features']
    index = featureset['index']
    counts = featureset['counts']
    dCounts = featureset['documentCounts']
    
    subset = [ f for f in index.keys()
                    if filter(index[f], counts[f], dCounts[f], len(papers)) ]

    I = []
    J = []
    K = []
    
    ecounts = Counter()
    Npapers = 0
    for paper in papers:
        p = paper['doi']
        try:
            fvect = features[p]
        except KeyError:
            continue

        Npapers += 1
        feats,vals = zip(*fvect)
        feats = list(set(feats) & set(subset))
        Nfeats = len(feats)
        for i in xrange(1,Nfeats):
            for e in zip(feats, feats[i:]):
                e_ = tuple(sorted(e))
                ecounts[e_] += 1

    if not graph:
        return ecounts
    else:
        pass

def pointwise_mutual_information(papers, featureset, filter=None, threshold=0.6, **kwargs):
    graph = nx.Graph()
    ecounts = cooccurrence(papers, featureset, filter=filter, graph=False)

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

    labels = { k:v for k,v in index.iteritems() if k in graph.nodes() }
    nx.set_node_attributes(graph, 'label', labels)

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
    """

    Z = model.top_word.shape[0]
    W = model.top_word.shape[1]

    edges = {}
    for z in xrange(Z):
        word_sub = []
        for w in xrange(W):
            if model.top_word[z,w] >= threshold:
                word_sub.append(w)

        for i in xrange(len(word_sub)):
            for j in xrange(i+1, len(word_sub)):
                w_i = word_sub[i]
                w_j = word_sub[j]
                p_i = model.top_word[z,w_i]
                p_j = model.top_word[z,w_j]
                try:
                    edges[(w_i,w_j)].append((z, (p_i+p_j)/2))
                except KeyError:
                    edges[(w_i,w_j)] = [(z, (p_i+p_j)/2)]
    tc = nx.Graph()

    for e, topics in edges.iteritems():
        weight = sum( [ t[1] for t in topics ] ) / Z
        i_id = model.vocabulary[e[0]]
        j_id = model.vocabulary[e[1]]
        tc.add_edge(i_id, j_id, weight=float(weight), 
                                topics=[t[0] for t in topics])

    return tc