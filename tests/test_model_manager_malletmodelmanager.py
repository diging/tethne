from settings import *

import unittest

from nltk.corpus import stopwords
import numpy
import os

from tethne import Corpus, HDF5Corpus
from tethne.readers import dfr
from tethne.model.managers import MALLETModelManager

import cPickle as pickle

dfrdatapath = '{0}/dfr'.format(datapath)
D = dfr.read_corpus(dfrdatapath, ['uni'])

def filt(s, C, DC):
    if C > 3 and DC > 1 and len(s) > 2:
        return True
    return False

D.filter_features('uni', 'unigrams', filt)
D.slice('date', 'time_period', window_size=1)

class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):
    

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
        self.assertGreater(os.path.getsize(temppath+'/input.mallet'), 2500)
        
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
        self.assertGreater(os.path.getsize(temppath+'/wt.dat'), 9000)
        
        self.assertIn('model.mallet', os.listdir(outpath))
        self.assertGreater(os.path.getsize(outpath+'/model.mallet'), 9000000)

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
        self.assertGreater(sum(R), 0)

        K,R = self.M.topic_over_time(k, mode='documents', normed=False)
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)  
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))
        self.assertGreater(sum(R), 0)
        
        K,R = self.M.topic_over_time(k, mode='proportions', normed=True)
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))
        self.assertGreater(sum(R), 0)
                
        K,R = self.M.topic_over_time(k, mode='proportions', normed=False)                        
        self.assertIsInstance(K, numpy.ndarray)
        self.assertIsInstance(R, numpy.ndarray)
        self.assertGreater(len(K), 0)
        self.assertGreater(len(R), 0)                
        self.assertEqual(len(R), len(K))
        self.assertGreater(sum(R), 0)
        
        K,R = self.M.topic_over_time(k, mode='documents', plot=True)
        self.assertIn('topic_{0}_over_time.png'.format(k), os.listdir(outpath))
        size = os.path.getsize(outpath+'/topic_{0}_over_time.png'.format(k))
        self.assertGreater(size, 0)
        self.assertGreater(sum(R), 0)

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