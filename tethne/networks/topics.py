"""
Build networks from topics in a topic model.
"""

import networkx as nx

def paper_coupling(model, threshold=0.1):
    """
    """
    
    D = model.doc_topic.shape[0]
    Z = model.doc_topic.shape[1]
    
    edges = {}
    for d in xrange(D):
        d_s = model.doc_topic[d,:]
        for i in xrange(Z):
            for j in xrange(i+1, Z):
                if d_s[i] >= threshold and d_s[j] >= threshold:
                    try:
                        edges[(i,j)].append( (d, d_s[i]*d_s[j]/2) )
                    except KeyError:
                        edges[(i,j)] = [(d, d_s[i]*d_s[j]/2)]

    pc = nx.Graph()
    
    for e, papers in edges.iteritems():
        weight = sum( [p[1] for p in papers] ) / D
        pc.add_edge(e[0], e[1], weight=weight, \
                    papers=[model.metadata[p[0]] for p in papers])
        
    for t in pc.nodes():
        pc.node[t]['words'] = model.top_keys[t][1]  # Add list of top words.
        
    return pc

def term_coupling(model, threshold=0.01):
    """
    """
    
    Z = model.top_word.shape[0]
    W = model.top_word.shape[1]
    
    edges = {}
    for w in xrange(W):    
        t_sub = []

        for z in xrange(Z):
            if model.top_word[z,w] >= threshold:
                t_sub.append(z)

        for i in xrange(len(t_sub)):
            for j in xrange(i+1, len(t_sub)):
                t_i = t_sub[i]
                t_j = t_sub[j]
                p_i = model.top_word[t_i,w]
                p_j = model.top_word[t_j,w]          
                try:
                    edges[(t_i,t_j)].append((w, (p_i+p_j)/2))
                except KeyError:
                    edges[(t_i,t_j)] = [(w, (p_i+p_j)/2)]
    tc = nx.Graph()
    
    #print edges
    
    for e, words in edges.iteritems():
        weight = sum( [ w[1] for w in words ] ) / W
        word_list = [model.vocabulary[w[0]] for w in words]
        tc.add_edge(e[0], e[1], weight=weight, words=word_list)
    
    for t in tc.nodes():
        tc.node[t]['words'] = model.top_keys[t][1]  # Add list of top words.
    
    return tc