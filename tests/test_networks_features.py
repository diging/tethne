from settings import *

import unittest
from tethne.readers import dfr
from tethne.networks.features import *
from tethne.writers.graph import to_graphml
from tethne.model.corpus import ldamodel

import os
import networkx

corpus = dfr.read_corpus(datapath+'/dfr', features=['uni'])

def filt(s, C, DC):
    if len(s) > 5 and C > 5 and DC > 100:
        return True
    return False

corpus.filter_features('unigrams', 'unigrams_filt', filt=filt)
corpus.transform('unigrams_filt', 'unigrams_tfidf')

class TestPMI(unittest.TestCase):
    def test_cooccurrence_graph(self):
        featureset = corpus.features['unigrams_tfidf']
        papers = corpus.all_papers()

        graph = cooccurrence(papers, featureset)
        self.assertIsInstance(graph, networkx.Graph)
        self.assertGreater(len(graph.nodes()), 0)
        self.assertGreater(len(graph.edges()), 0)

    def test_cooccurrence_values(self):
        featureset = corpus.features['unigrams_tfidf']
        papers = corpus.all_papers()

        co = cooccurrence(papers, featureset, graph=False)
        self.assertIsInstance(co, dict)
        self.assertGreater(len(co), 0)

    def test_mutual_information(self):
        featureset = corpus.features['unigrams_tfidf']
        papers = corpus.all_papers()

        graph = mutual_information(papers, featureset, threshold=0.5)
        self.assertIsInstance(graph, networkx.Graph)
        self.assertGreater(len(graph.nodes()), 0)
        self.assertGreater(len(graph.edges()), 0)

class TestTopicCoupling(unittest.TestCase):
    def setUp(self):
        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)
    
    def test_lda(self):
        model = ldamodel.from_mallet(   self.dt_path,
                                        self.wt_path,
                                        self.meta_path  )

        graph = topic_coupling(model)
        self.assertIsInstance(graph, networkx.Graph)
        self.assertGreater(len(graph.nodes()), 0)
        self.assertGreater(len(graph.edges()), 0)
        self.assertIn('weight', graph.edges(data=True)[0][2])
        self.assertIn('topics', graph.edges(data=True)[0][2])

        to_graphml(graph, datapath+'test_model_graph.graphml')

    def tearDown(self):
        os.remove(datapath+'test_model_graph.graphml')



if __name__ == '__main__':
    unittest.main()