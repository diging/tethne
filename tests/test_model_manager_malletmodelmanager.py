from settings import *

import unittest

from nltk.corpus import stopwords
import numpy
import os

from tethne import DataCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import MALLETModelManager

import cPickle as pickle
picklepath = '{0}/pickles'.format(datapath)
with open('{0}/dfr_DataCollection.pickle'.format(picklepath), 'r') as f:
    D = pickle.load(f)

class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):
        dfrdatapath = '{0}/dfr'.format(datapath)

        pcgpath = cg_path + 'model.manager.MALLETModelManager.__init__.png'
        with Profile(pcgpath):
            self.M = MALLETModelManager(D, feature='unigrams',
                                           outpath=outpath,
                                           temppath=temppath,
                                           mallet_path=mallet_path)

    def test_prep(self):
        """
        .prep() should result in three sizeable temporary corpus files.
        """

        pcgpath = cg_path + 'model.manager.MALLETModelManager.prep.png'
        with Profile(pcgpath):
            self.M.prep()

        self.assertIn('input.mallet', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/input.mallet'), 2500000)
        
        self.assertIn('tethne_docs.txt', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/tethne_docs.txt'), 5000000)
                
        self.assertIn('tethne_meta.csv', os.listdir(temppath))        
        self.assertGreater(os.path.getsize(temppath+'/tethne_meta.csv'), 10000)

    def test_build(self):
        """
        .build() should result in new sizeable files in both the temp and out
        directories.
        """
        
        self.M.prep()
        
        pcgpath = cg_path + 'model.manager.MALLETModelManager.build.png'
        with Profile(pcgpath):
            self.M.build(max_iter=50)
        
        self.assertIn('dt.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/dt.dat'), 100000)
        
        self.assertIn('wt.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/wt.dat'), 900000)
        
        self.assertIn('model.mallet', os.listdir(outpath))
        self.assertGreater(os.path.getsize(outpath+'/model.mallet'), 9000000)

    def test_list_topic(self):
        """
        :func:`.list_topic` should yield a list with ``Nwords`` words.
        """
        Nwords = 10
        self.M._load_model()
        
        pcgpath = cg_path + 'model.manager.MALLETModelManager.list_topic.png'
        with Profile(pcgpath):
            result = self.M.list_topic(0, Nwords=Nwords)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], str)
        self.assertEqual(len(result), Nwords)

    def test_print_topic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
        Nwords = 10
        self.M._load_model()
        
        pcgpath = cg_path + 'model.manager.MALLETModelManager.print_topic.png'
        with Profile(pcgpath):
            result = self.M.print_topic(0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split(', ')), Nwords)

    def test_list_topics(self):
        """
        :func:`.list_topics` should yield a dict { k : [ w ], }.
        """

        Nwords = 10
        self.M._load_model()

        pcgpath = cg_path + 'model.manager.MALLETModelManager.list_topics.png'
        with Profile(pcgpath):
            result = self.M.list_topics(Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], list)
        self.assertIsInstance(result.values()[0][0], str)
        self.assertEqual(len(result), self.M.model.Z)

    def test_print_topics(self):
        Nwords = 10
        self.M._load_model()

        pcgpath = cg_path + 'model.manager.MALLETModelManager.print_topics.png'
        with Profile(pcgpath):
            result = self.M.print_topics(Nwords=Nwords)

        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.M.model.Z)

    def test_topic_time(self):
        """
        Each mode should generate two numpy.ndarrays of equal non-zero length.
        """
        k = 0
        
        self.M.prep()
        self.M.build(max_iter=50)
        
        pcgpath = cg_path+'model.manager.MALLETModelManager.topic_over_time.png'
        with Profile(pcgpath):
            K,R = self.M.topic_over_time(k, mode='documents', normed=True)

        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))

        K,R = self.M.topic_over_time(k, mode='documents', normed=False)
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)  
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))                            
        
        K,R = self.M.topic_over_time(k, mode='proportions', normed=True)
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))                
                
        K,R = self.M.topic_over_time(k, mode='proportions', normed=False)                        
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))    
        
        K,R = self.M.topic_over_time(k, mode='documents', plot=True)
        self.assertIn('topic_{0}_over_time.png'.format(k), os.listdir(outpath))
        size = os.path.getsize(outpath+'/topic_{0}_over_time.png'.format(k))
        self.assertGreater(size, 0)

    def test_load(self):
        """
        :func:`._load_model` should execute successfully after :func:`.init`\.
        """

        pcgpath = cg_path + 'model.manager.MALLETModelManager._load_model.png'
        with Profile(pcgpath):
            self.M._load_model()
        
        self.assertEqual(self.M.model.theta.shape, (241, 20))

if __name__ == '__main__':
    unittest.main()