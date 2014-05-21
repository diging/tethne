# -*- coding: utf-8 -*-
# <nbformat>3.0</nbformat>

# <codecell>

class SocialModelManager(object):
    """
    Base class for social model managers.
    """
    
    def __init__(self, **kwargs):
        pass
        
    def build(self, max_iter=1000, **kwargs):
        self._run_model(max_iter, **kwargs)
        self._load_model()

# <codecell>

class TAPModelManager(SocialModelManager):
    """
    For managing the :class:`.TAPModel` .
    """
    
    def __init__(self, D, G, M, **kwargs):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        G : :class:`.GraphCollection`
        M : :class:`.ModelCollection`
        """

        super(TAPModelManager, self).__init__(**kwargs)
        self.D = D
        self.M = M
        self.G = G
        self.SM = ModelCollection()
        self.SG = GraphCollection()
        
    def author_theta(self, papers, model, indexed_by='doi'):
        """
        Generates distributions over topics for authors, based on distributions
        over topics for their papers.
        """
        
        a_topics = {}

        for p in papers:
            try:
                t = model.topics_in_doc(p[indexed_by])
                dist = np.zeros(( len(t) ))
                for i,v in t:
                    dist[i] = v

                for author in p.authors():
                    if author in a_topics:
                        a_topics[author].append(dist)
                    else:
                        a_topics[author] = [ dist ]
            except KeyError:    # May not be corpus model repr for all papers.
                pass

        a_theta = np.zeros(( len(a_topics), model.num_topics() ))
        a = 0
        for author, dists in a_topics.iteritems():
            a_dist = np.zeros(( model.num_topics() ))
            for dist in dists:
                a_dist += dist
            a_dist = a_dist/len(dists)
            a_theta[a, :] = a_dist/np.sum(a_dist)   # Should sum to <= 1.0.

        
        return a_theta
    
    def _run_model(self, max_iter=1000, sequential=True, **kwargs):
        print 'run model'

        axis = kwargs.get('axis', None) # e.g. 'date'

        if axis is None:
            # single model.
            pass
        else:
            # model for each slice.
            if axis not in D.get_axes():
                raise RuntimeError('No such axis in DataCollection.')
                
            s = 0
            for slice in sorted(D.get_slices(axis).keys()):
                print 'modeling slice {0}'.format(slice) # TODO: logging.

                if s > 0 and sequential:
                    alt_r, alt_a, alt_G = model.r, model.a, model.G

                papers = D.get_slice(axis, slice, papers=True)

                theta = self.author_theta(papers, self.M[slice])
                model = TAPModel(self.G[slice], theta)
                
                if s > 0 and sequential:
                    model.prime(alt_r, alt_a, alt_G)
                
                model.build()
                self.SM[slice] = model
                
                s += 1
                
    
    def graph_collection(self, k):
        C = GraphCollection()
        for slice in self.SM.keys():
            C[slice] = self.SM[slice].graph(k)
    
        return C
                    
    
    def _load_model(self):
        pass

# <codecell>

import os
import sys
from nltk.corpus import stopwords
import matplotlib.pyplot as plt

# <codecell>

from collections import Counter

# <codecell>

sys.path.append("/Users/erickpeirson/tethne")

# <codecell>

import tethne.readers as rd
from tethne.builders import DFRBuilder
from tethne.data import DataCollection, ModelCollection, GraphCollection
import tethne.writers as wr

# <codecell>

datapath = '/Users/erickpeirson/Desktop/Topic Modeling/Ecology/DfR Results'

# <codecell>

import time

# <codecell>

vocab = {}
with open('/Users/erickpeirson/dtm_temp/ecology-vocab.dat', 'r') as f:
    i = 0
    for line in f:
        vocab[i] = line.strip()
        i += 1

# <codecell>

sw = stopwords.words()

# <codecell>

len(vocab)

# <codecell>

vocab.values()[0:10]

# <codecell>

i = 0
vocab_filtered = {}
vocab_reverse = {}
for v in vocab.values():
    if v not in sw:
        vocab_filtered[i] = v
        vocab_reverse[v] = i
        i += 1

# <codecell>

len(vocab_filtered)

# <codecell>

vocab_filtered.values()[0:10]

# <codecell>

def tokenize(ngrams, min_tf=2, min_df=2, min_len=4, vocab=None):

    vocab_ = {}
    word_tf = Counter()
    word_df = Counter()
    token_tf = Counter()
    token_df = Counter()
    t_ngrams = {}
    
    # Get global word counts, first.
    for grams in ngrams.values():
        for g,c in grams:
            word_tf[g] += c
            word_df[g] += 1
            
    # Now tokenize.
    NG = float(len(grams))
    
    for doi,grams in ngrams.iteritems():
        
        t_ngrams[doi] = []
        for g,c in grams:
            ignore = False
                        
            # Ignore extremely rare words (probably garbage).
            if word_tf[g] < min_tf or word_df[g] < min_df or len(g) < min_len:
                ignore = True

            if not ignore:
                try:
                    i = vocab[g]
                except KeyError:
                    continue

                token_df[i] += 1
                t_ngrams[doi].append( (i,c) )

    return t_ngrams, vocab, token_tf

# <codecell>

bob = { 1: [ ('asdf', 2), ('fdsa', 3), ('ccraasdfka', 1) ], 2: [('asdf',3), ('fdsa',1), ('aaaa',1)] }

# <codecell>

test_data = { k:v for k,v in gram_data.items()[0:500] }

# <codecell>

q,w,r = tokenize(test_data, vocab=vocab_reverse)#, apply_stoplist=True)

# <markdowncell>

# ## Social influence model

# <codecell>

papers = []
for dirname in os.listdir(datapath):
    if dirname != '.DS_Store':
        print dirname
        datasetpath = '{0}/{1}'.format(datapath, dirname)
        papers += rd.dfr.read(datasetpath)

# <codecell>

import tethne.builders as bd
from tethne.model import TAPModel
import networkx as nx

# <codecell>

D = DataCollection(papers, index_by='doi')

# <codecell>

D.slice('date', 'time_period', window_size=1, cumulative=True)

# <codecell>

builder = bd.authorCollectionBuilder(D)

# <codecell>

G = builder.build('date', 'coauthors', threshold=1)

# <codecell>

A = G.nodes()

# <codecell>

a_dict = { A[i]:i for i in xrange(len(A)) }
a_dict_ = { i:A[i] for i in xrange(len(A)) }

# <codecell>

G_ = GraphCollection()

# <codecell>

G.graphs[1950].edges(data=True)[0]

# <codecell>

for k,g in G.graphs.iteritems():
    g_ = nx.Graph()
    for edge in g.edges(data=True):
        g_.add_edge(a_dict[edge[0]], a_dict[edge[1]], edge[2])
    
    G_.graphs[k] = g_

# <codecell>

td = '/Users/erickpeirson/lda_temp/doc-topics_400.dat'
wt = '/Users/erickpeirson/lda_temp/word-topic_400.dat'
tk = '/Users/erickpeirson/lda_temp/topic-keys_400.dat'
Z = 400
md = '/Users/erickpeirson/lda_temp/ecology_meta.csv'

# <codecell>

model = rd.mallet.load(td, wt, tk, Z, md)

# <codecell>

M = ModelCollection()

# <codecell>

M.models = { k:model for k in D.axes['date'].keys() }

# <codecell>

TAPMM = TAPModelManager(D, G_, M)

# <codecell>

TAPMM.build(axis='date')

# <codecell>

papers = []
gram_data = {}
for dirname in os.listdir(datapath):
    if dirname != '.DS_Store':
        print dirname
        datasetpath = '{0}/{1}'.format(datapath, dirname)
        papers += rd.dfr.read(datasetpath)
        gram_data.update( rd.dfr.ngrams(datasetpath, N='uni') )

# <codecell>

import cPickle

# <codecell>

cPickle.dump((papers, gram_data), open('/Users/erickpeirson/Desktop/ecology_temp.pickle', 'w'))

# <codecell>

with open('/Users/erickpeirson/Desktop/ecology_temp.pickle', 'r') as f:
    papers, gram_data = cPickle.load(f)

# <codecell>

close('/Users/erickpeirson/Desktop/ecology_temp.pickle')

# <codecell>

g_tok, vocab, counts = tokenize(gram_data, vocab=vocab_reverse)#, apply_stoplist=True)

# <codecell>

D = DataCollection(papers, grams={'uni': (g_tok, vocab, counts) }, index_by='doi')

# <codecell>

kw = { 'method': 'time_window',
       'window_size': 1,
       'step_size': 1 }

# <codecell>

D.slice('date', **kw)

# <codecell>

wr.corpora.to_documents('/Users/erickpeirson/lda_temp/ecology', g_tok, papers=D.papers(), vocab=vocab_filtered, fields=['date', 'atitle', 'jtitle'])

# <codecell>

wr.corpora.to_dtm_input('/Users/erickpeirson/dtm_temp2/ecology', D, g_tok, vocab, fields=['date', 'atitle', 'jtitle'])

# <codecell>

len(vocab)

# <codecell>

len( [ c for c in counts.values() if c == 1 ])

# <codecell>

completeness = []
for year, dois in D.get_slices('date').iteritems():
    completeness.append(float(len ( [ d for d in dois if len(g_tok[d]) > 0 ] ))/len(dois))
plt.plot(D.get_slices('date').keys(), completeness)
plt.xlim(1940, 1971)
plt.ylim(0.95, 1.0)
plt.show()

# <codecell>

vocab_reverse['ecotype']

# <codecell>

len(D.get_slice('date', 1940))

# <codecell>

[ len(v) for k,v in D.get_slices('date').iteritems() ]

# <codecell>

terms = [ ('canalization', 'canalized', 'canalisation', 'canalised'), 
          ('stability', 'stable', 'stabilization'),
          ('plasticity','plastic'),
          ('flexibility','flexible'),
          ('control',),
          ('homeostasis', 'homeostatic'),
          ('environment', 'environmental'),
          ('response', 'responds', 'responded', 'responding'),
          ('development', 'developmental'),
          ('constraint', 'constrained', 'constrain'),
          ('symmetry', 'symmetrical', 'symmetric', 'asymmetric', 'asymmetrical', 'asymmetry'),
          ('yield',),
          ('fitness', 'fit'),
          ('evolved', 'evolve'),
          ('differentiation', 'differentiate', 'diverge', 'divergence'),
          ('genetic', 'gene', 'genetical')]

# <codecell>

T = len(D.get_slices('date'))

# <codecell>

Nt = len(terms)

# <codecell>

co_terms = np.zeros(( T, Nt, Nt ))

# <codecell>

co_terms.shape

# <codecell>

for year, dois in D.get_slices('date').iteritems():
    y = year-1940
    print year
    for d in dois:
        for i in xrange(Nt):
            i_found = False        
            for t in terms[i]:
                try:
                    if vocab_reverse[t] in [ r for r,v in g_tok[d['doi']] ]:
                        i_found = True
                except KeyError:
                    pass
            for j in xrange(i, Nt):
                j_found = False
                for t in terms[j]:
                    try:
                        if vocab_reverse[t] in [ r for r,v in g_tok[d['doi']] ]:
                            j_found = True
                    except KeyError:
                        pass
            
                if i_found and j_found:
                    co_terms[ y, i, j ] += 1.

# <codecell>

nPMI = np.zeros(( T, Nt, Nt ))
P_ij = np.zeros(( T, Nt, Nt ))
for year, dois in D.get_slices('date').iteritems():
    y = year-1940
    N = len(dois)
    for d in dois:
        for i in xrange(Nt):
            p_i = co_terms[y, i, i]/N
            for j in xrange(i, Nt):
                p_j = co_terms[y, j, j]/N                
                p_ij = co_terms[y, i, j]/N
                
                if p_ij == 0.:
                    if i == j:
                        npmi = 1.
                    else:
                        npmi = 0.
                else:
                    npmi = np.log( p_ij/ ( p_i * p_j ) ) / ( -1. * np.log( p_ij ) )
                    
                nPMI[y, i, j] = npmi
                P_ij[y, i, j] = p_ij

# <codecell>

plt.figure(figsize=(30, 20))
for i in xrange(Nt):
    for j in xrange(i+1, Nt):
        s = j + Nt*i - i 
        sub = plt.subplot(Nt-1, Nt-1, s)
        sub.plot(range(1940, 1940+T), nPMI[:, i, j])
        plt.ylim(0, 1.1)
        
        if j == i+1:
            plt.ylabel(terms[i][0])
        if i == 0:
            plt.title(terms[j][0])

# <codecell>

plt.plot(D.get_slices('date').keys(), ecotype)
plt.xlim(1940, 1971)
plt.show()

# <codecell>

coauthors = []
n_coauthors = []
for year, papers in D.get_slices('date').iteritems():
#    papers = [ D.data[d] for d in dois ]
    coauthors.append( float ( len([ p for p in papers if len(p['aulast']) > 1 ]) )/len(papers) )
    n_coauthors.append( len(set ( [ a for p in papers for a in p.authors() ] )) )

# <codecell>

p.authors()

# <codecell>

plt.plot(D.get_slices('date').keys(), coauthors)
plt.xlim(1940, 1971)
plt.show()

# <codecell>

plt.plot(D.get_slices('date').keys(), n_coauthors)
plt.xlim(1940, 1971)
plt.show()

# <codecell>


