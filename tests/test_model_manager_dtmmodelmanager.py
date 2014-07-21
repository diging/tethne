from settings import *

import unittest

from nltk.corpus import stopwords
import numpy
import os

from tethne import DataCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import DTMModelManager

import cPickle as pickle
with open('{0}/dfr_DataCollection.pickle'.format(picklepath), 'r') as f:
    D = pickle.load(f)

class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):

        pcgpath = cg_path + 'model.manager.DTMModelManager.__init__.png'
        with Profile(pcgpath):
            self.M = DTMModelManager(D, feature='unigrams',
                                        outpath=outpath,
                                        temppath=temppath,
                                        dtm_path=dtm_path)

    def test_prep(self):
        """
        .prep() should result in four sizeable temporary corpus files.
        """
        
        pcgpath = cg_path + 'model.manager.DTMModelManager.prep.png'
        with Profile(pcgpath):
            self.M.prep()
            
        self.assertIn('tethne-meta.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/tethne-meta.dat'),15000)
        
        self.assertIn('tethne-mult.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/tethne-mult.dat'),1400000)
                
        self.assertIn('tethne-seq.dat', os.listdir(temppath))        
        self.assertGreater(os.path.getsize(temppath+'/tethne-seq.dat'),10)

        self.assertIn('tethne-vocab.dat', os.listdir(temppath))        
        self.assertGreater(os.path.getsize(temppath+'/tethne-vocab.dat'),400000)
    
    def test_build(self):
        """
        .build() should result in new sizeable files in both the temp and out
        directories.
        """
        self.M.prep()
        
        pcgpath = cg_path + 'model.manager.DTMModelManager.build.png'
        with Profile(pcgpath):
            self.M.build(   Z=5, lda_seq_min_iter=2,
                                 lda_seq_max_iter=4,
                                 lda_max_em_iter=4  )

    def test_load(self):
        """
        :func:`._load_model` should execute successfully after :func:`.init`\.
        """

        pcgpath = cg_path + 'model.manager.DTMModelManager._load_model.png'
        with Profile(pcgpath):
            self.M._load_model()
        
        self.assertEqual(self.M.model.e_theta.shape, (5, 176))

    def test_plot_topic_evolution(self):
        """
        :func:`.plot_topic_evolution` should generate a plot given data from
        :func:`.DTMModel.topic_evolution`\.
        """

        k = 3
        self.M._load_model()
        Nwords = 5
    
        pcgpath = cg_path+'model.manager.DTMModelManager.plot_topic_evolution.png'
        with Profile(pcgpath):
            K,R = self.M.plot_topic_evolution(k, Nwords, plot=True)

        self.assertIn('topic_{0}_evolution.png'.format(k), os.listdir(outpath))
        size = os.path.getsize(outpath+'/topic_{0}_evolution.png'.format(k))
        self.assertGreater(size, 0)
        self.assertGreater(sum(R.values()[0]), 0)

    def test_topic_time(self):
        """
        Each mode should generate two numpy.ndarrays of equal non-zero length.
        """
        k = 1
        
        self.M._load_model()
        
        pcgpath = cg_path+'model.manager.DTMModelManager.topic_over_time.png'
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


if __name__ == '__main__':
    unittest.main()