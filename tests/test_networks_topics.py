from settings import *

import unittest
from tethne.readers import dfr
from tethne.model.managers import MALLETModelManager
from tethne.analyze import features
from tethne.networks.topics import distance

import os
import networkx
from nltk.corpus import stopwords

corpus = dfr.read_corpus(datapath+'/dfr', features=['uni'])
corpus.filter_features('unigrams', 'u_filt')
corpus.apply_stoplist('u_filt', 'u_stop', stopwords.words())

manager = MALLETModelManager(   corpus, feature='u_stop',
                                outpath=outpath, temppath=temppath,
                                mallet_path=mallet_path)
manager.prep()
manager.build(Z=20, max_iter=100)

methods = [
    'braycurtis',
    'canberra',
    'chebyshev',
    'cityblock',
    'correlation',
    'cosine',
    'dice',
    'euclidean',
    'kulsinski',
    'matching',
    'rogerstanimoto',
    'russellrao',
    'sokalmichener',
    'sokalsneath',
    'sqeuclidean',
    'yule'
    ]

nonsense_methods = [
    'hamming',
    'jaccard',
    ]

class TestDistanceNetwork(unittest.TestCase):
    def test_kl_divergence(self):
        testgraph = distance(manager.model, method='cosine')
        self.assertEqual(len(testgraph.edges()), 2892)
    
    def test_cosine(self):
        testgraph = distance(manager.model, method='cosine')
        self.assertEqual(len(testgraph.edges()), 2892)
        
    def test_braycurtis(self):
        testgraph = distance(manager.model, method='braycurtis')
        self.assertEqual(len(testgraph.edges()), 2892)
        
    def test_chebyshev(self):
        testgraph = distance(manager.model, method='chebyshev')
        self.assertEqual(len(testgraph.edges()), 2892)
    
    def test_cityblock(self):
        testgraph = distance(manager.model, method='cityblock')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_correlation(self):
        testgraph = distance(manager.model, method='correlation')
        self.assertEqual(len(testgraph.edges()), 2892)
        
    def test_dice(self):
        testgraph = distance(manager.model, method='dice')
        self.assertEqual(len(testgraph.edges()), 2892)
        
    def test_euclidean(self):
        testgraph = distance(manager.model, method='euclidean')
        self.assertEqual(len(testgraph.edges()), 2892)
        
    def test_kulsinski(self):
        testgraph = distance(manager.model, method='kulsinski')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_matching(self):
        testgraph = distance(manager.model, method='matching')
        self.assertEqual(len(testgraph.edges()), 2892)
    
    def test_rogerstanimoto(self):
        testgraph = distance(manager.model, method='rogerstanimoto')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_russellrao(self):
        testgraph = distance(manager.model, method='russellrao')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_sokalmichener(self):
        testgraph = distance(manager.model, method='sokalmichener')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_sokalsneath(self):
        testgraph = distance(manager.model, method='sokalsneath')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_sqeuclidean(self):
        testgraph = distance(manager.model, method='sqeuclidean')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_yule(self):
        testgraph = distance(manager.model, method='yule')
        self.assertEqual(len(testgraph.edges()), 2892)

    def test_hamming(self):
        with self.assertRaises(RuntimeError):
            testgraph = distance(manager.model, method='hamming')

    def test_jaccard(self):
        with self.assertRaises(RuntimeError):
            testgraph = distance(manager.model, method='jaccard')

if __name__ == '__main__':
    unittest.main()