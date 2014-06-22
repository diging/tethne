from settings import *

# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

import unittest

from nltk.corpus import stopwords
import numpy
import os

from tethne import DataCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import DTMModelManager

import cPickle as pickle
picklepath = './data/pickles'
with open('{0}/dfr_DataCollection.pickle'.format(picklepath), 'r') as f:
    D = pickle.load(f)

class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.__init__.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.M = DTMModelManager(D, outpath=outpath,
                                            temppath=temppath,
                                            dtm_path=dtm_path)
        else:
            self.M = DTMModelManager(D, outpath=outpath,
                                        temppath=temppath,
                                        dtm_path=dtm_path)

    def test_list_topic(self):
        """
        :func:`.list_topic` should yield a list with ``Nwords`` words.
        """

        Nwords = 10
        
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.list_topic.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.list_topic(0, 0, Nwords=Nwords)
        else:
            result = self.M.list_topic(0, 0, Nwords=Nwords)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], str)
        self.assertEqual(len(result), Nwords)

    def test_list_topic_diachronic(self):
        """
        :func:`.list_topic_diachronic` should yield a dict with ``T`` entries,
        each with a list of ``Nwords`` words.
        """

        Nwords = 10
        
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.list_topic_diachronic.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.list_topic_diachronic(0, Nwords=Nwords)
        else:
            result = self.M.list_topic_diachronic(0, Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), self.M.model.T)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), Nwords)

    def test_print_topic_diachronic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
    
        Nwords = 10
        
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.print_topic.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.print_topic_diachronic(0, Nwords=Nwords)
        else:
            result = self.M.print_topic_diachronic(0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.M.model.T)

    def test_print_topic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
    
        Nwords = 10
        
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.print_topic.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.print_topic(0, 0, Nwords=Nwords)
        else:
            result = self.M.print_topic(0, 0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split(', ')), Nwords)

    def test_list_topics(self):
        """
        :func:`.list_topics` should yield a dict { k : [ w ], }.
        """

        Nwords = 10
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.list_topics.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.list_topics(0, Nwords=Nwords)
        else:
            result = self.M.list_topics(0, Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], list)
        self.assertIsInstance(result.values()[0][0], str)
        self.assertEqual(len(result), self.M.model.Z)

    def test_print_topics(self):
        Nwords = 10
        self.M._load_model()

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.print_topics.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.M.print_topics(0, Nwords=Nwords)
        else:
            result = self.M.print_topics(0, Nwords=Nwords)

        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.M.model.Z)

    def test_prep(self):
        """
        .prep() should result in four sizeable temporary corpus files.
        """
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.DTMModelManager.prep.png')):
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
        
        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager.build.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.M.build(   Z=5, lda_seq_min_iter=2,
                                     lda_seq_max_iter=4,
                                     lda_max_em_iter=4  )
        else:
            self.M.build(   Z=5, lda_seq_min_iter=2,
                                 lda_seq_max_iter=4,
                                 lda_max_em_iter=4  )

    def test_load(self):
        """
        :func:`._load_model` should execute successfully after :func:`.init`\.
        """

        if profile:
            pcgpath = cg_path + 'model.manager.DTMModelManager._load_model.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.M._load_model()
        else:
            self.M._load_model()
        
        self.assertEqual(self.M.model.e_theta.shape, (5, 176))


if __name__ == '__main__':
    unittest.main()