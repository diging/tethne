"""
Methods for building networks from terms in bibliographic records. This
includes keywords, abstract terms, etc.

.. autosummary::

   keyword_cooccurrence
   topic_coupling
"""

import numpy as np
import networkx as nx

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