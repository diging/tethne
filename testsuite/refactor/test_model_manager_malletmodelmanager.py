# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
cg_path = './callgraphs/'

import unittest

import sys
sys.path.append('../../')

from nltk.corpus import stopwords
import numpy
import os

from tethne import DataCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import MALLETModelManager

import logging
logging.basicConfig()
logger = logging.getLogger('tethne.classes.datacollection')
logger.setLevel('ERROR')


class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):
        dfrdatapath = '{0}/dfr'.format(datapath)
        
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')
        self.D = DataCollection(papers, features={'unigrams': ngrams},
                                        index_by='doi',
                                        exclude=set(stopwords.words()))
        self.D.slice('date', 'time_period', window_size=10)
        
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.MALLETModelManager.__init__.png')):
            self.M = MALLETModelManager(self.D, outpath=outpath,
                                    temppath=temppath,
                                    mallet_path=mallet_path)
        
    def test_prep(self):
        """
        .prep() should result in three sizeable temporary corpus files.
        """

        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.MALLETModelManager.prep.png')):
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
        
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.MALLETModelManager.build.png')):
            self.M.build(max_iter=50)
        
        self.assertIn('dt.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/dt.dat'), 100000)
        
        self.assertIn('wt.dat', os.listdir(temppath))
        self.assertGreater(os.path.getsize(temppath+'/wt.dat'), 900000)
        
        self.assertIn('model.mallet', os.listdir(outpath))
        self.assertGreater(os.path.getsize(outpath+'/model.mallet'), 9000000)

    def test_topic_time(self):
        """
        Each mode should generate two numpy.ndarrays of equal non-zero length.
        """
        k = 0
        
        self.M.prep()
        self.M.build(max_iter=50)
        
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.MALLETModelManager.topic_over_time.png')):
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

        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.MALLETModelManager._load_model.png')):
            self.M._load_model()
        
        self.assertEqual(self.M.model.theta.shape, (241, 20))

if __name__ == '__main__':
    datapath = './data'
    temppath = './sandbox/temp'
    outpath = './sandbox/out'
    mallet_path = '/Applications/mallet-2.0.7'
    unittest.main()