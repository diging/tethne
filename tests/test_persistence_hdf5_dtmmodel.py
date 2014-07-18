from settings import *

import unittest

from tethne.model.corpus import dtmmodel
from tethne.persistence.hdf5 import HDF5DTMModel

import numpy

import os

class TestHDF5DTMModelInit(unittest.TestCase):
    def test_init(self):
    
        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
        self.target_path = '{0}/dtm/model_run'.format(datapath)
        self.lmodel = dtmmodel.from_gerrish(  self.target_path,
                                             self.meta_path,
                                             self.vocab_path )
    
        self.h5name = 'test_HDF5DTMModel.h5'
        self.h5path = temppath+'/'+self.h5name
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.__init__.png'
        with Profile(pcgpath):
            self.model = HDF5DTMModel(self.lmodel.e_theta, self.lmodel.phi,
                                      self.lmodel.metadata,
                                      self.lmodel.vocabulary,
                                      datapath=self.h5path)
    def tearDown(self):
        os.remove(self.h5path)


class TestPrint(unittest.TestCase):
    def setUp(self):
        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
        self.target_path = '{0}/dtm/model_run'.format(datapath)
        self.lmodel = dtmmodel.from_gerrish(  self.target_path,
                                             self.meta_path,
                                             self.vocab_path )
    
        self.h5name = 'test_HDF5DTMModel.h5'
        self.h5path = temppath+'/'+self.h5name
        self.model = HDF5DTMModel(self.lmodel.e_theta, self.lmodel.phi,
                                  self.lmodel.metadata, self.lmodel.vocabulary,
                                  datapath=self.h5path)

    def test_list_topic(self):
        """
        :func:`.list_topic` should yield a list with ``Nwords`` words.
        """

        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.list_topic.png'
        with Profile(pcgpath):
            result = self.model.list_topic(0, 0, Nwords=Nwords)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], str)
        self.assertEqual(len(result), Nwords)

    def test_topic_evolution(self):
        """
        :func:`.topic_evolution` should return time index keys, and a 
        dictionary containing words and p(w|z) series.
        """

        Nwords = 5
        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.topic_evolution.png'
        with Profile(pcgpath):
            K, R = self.model.topic_evolution(2, Nwords=Nwords)

        self.assertIsInstance(K, list)
        self.assertIsInstance(R, dict)
        self.assertIsInstance(R.keys()[0], str) #   Word
        self.assertIsInstance(R.values()[0], list)  # p over time.
        self.assertEqual(len(K), len(R.values()[0]))

    def test_list_topic_diachronic(self):
        """
        :func:`.list_topic_diachronic` should yield a dict with ``T`` entries,
        each with a list of ``Nwords`` words.
        """

        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.list_topic_diachronic.png'
        with Profile(pcgpath):
            result = self.model.list_topic_diachronic(0, Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertEqual(len(result), self.model.T)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result[0], list)
        self.assertEqual(len(result[0]), Nwords)

    def test_print_topic_diachronic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
    
        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.print_topic.png'
        with Profile(pcgpath):
            result = self.model.print_topic_diachronic(0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.model.T)

    def test_print_topic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
    
        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.print_topic.png'
        with Profile(pcgpath):
            result = self.model.print_topic(0, 0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split(', ')), Nwords)

    def test_list_topics(self):
        """
        :func:`.list_topics` should yield a dict { k : [ w ], }.
        """

        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.list_topics.png'
        with Profile(pcgpath):
            result = self.model.list_topics(0, Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], list)
        self.assertIsInstance(result.values()[0][0], str)
        self.assertEqual(len(result), self.model.Z)

    def test_print_topics(self):
        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.print_topics.png'
        with Profile(pcgpath):
            result = self.model.print_topics(0, Nwords=Nwords)

        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.model.Z)

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()