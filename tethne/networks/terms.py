"""
Methods for building networks from terms in bibliographic records. This
includes keywords, abstract terms, etc.
"""

import numpy as np

def keyword_cooccurrence(papers, threshold, connected=False):
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
    
    for entry in papers
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