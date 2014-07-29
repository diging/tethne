from settings import *

import unittest

from tethne.persistence.hdf5.ldamodel import HDF5LDAModel, from_hdf5, to_hdf5
from tethne.model.corpus import ldamodel

import os

class TestHDF5LDAModelInit(unittest.TestCase):

    def setUp(self):
        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)
        self.lmodel = ldamodel.from_mallet(  self.dt_path,
                                             self.wt_path,
                                             self.meta_path  )
    
        self.h5name = 'test_HDF5LDAModel.h5'
        self.h5path = temppath+'/'+self.h5name
        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.__init__.png'
        with Profile(pcgpath):
            self.model = HDF5LDAModel(self.lmodel.theta, self.lmodel.phi,
                                      self.lmodel.metadata,
                                      self.lmodel.vocabulary,
                                      datapath=self.h5path)
                
        self.assertIn(self.h5name, os.listdir(temppath))

    def test_from_hdf5_object(self):
        tmodel = from_hdf5(self.model)
    
        self.assertIsInstance(tmodel, ldamodel.LDAModel)
        self.assertEqual(tmodel.theta, self.model.theta)
        self.assertEqual(tmodel.phi, self.model.phi)
        self.assertEqual(tmodel.metadata, self.model.metadata)
        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)

    def test_from_hdf5_datapath(self):
        tmodel = from_hdf5(self.model.path)
        self.assertIsInstance(tmodel, ldamodel.LDAModel)
        self.assertEqual(tmodel.theta.shape, self.model.theta.shape)
        self.assertEqual(tmodel.theta[0].all(), self.model.theta[0].all())
        self.assertEqual(tmodel.phi.shape, self.model.phi.shape)
        self.assertEqual(tmodel.phi[0].all(), self.model.phi[0].all())
        self.assertEqual(tmodel.metadata, self.model.metadata)
        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)

    def test_to_hdf5(self):
        hmodel = to_hdf5(self.lmodel)

        self.assertIsInstance(hmodel, HDF5LDAModel)
        self.assertEqual(self.lmodel.theta[0].all(), hmodel.theta[0].all())
        self.assertEqual(self.lmodel.phi[0].all(), hmodel.phi[0].all())
        self.assertEqual(self.lmodel.metadata, hmodel.metadata)
        self.assertEqual(self.lmodel.vocabulary, hmodel.vocabulary)

    def tearDown(self):
        os.remove(self.h5path)


class TestHDF5LDAModel(unittest.TestCase):
    def setUp(self):
        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)
        self.lmodel = ldamodel.from_mallet(  self.dt_path,
                                             self.wt_path,
                                             self.meta_path  )
    
        self.h5name = 'test_HDF5LDAModel.h5'
        self.h5path = temppath+'/'+self.h5name
        self.model = HDF5LDAModel(self.lmodel.theta, self.lmodel.phi,
                                  self.lmodel.metadata, self.lmodel.vocabulary,
                                  datapath=self.h5path)

    def test_list_topic(self):
        """
        :func:`.list_topic` should yield a list with ``Nwords`` words.
        """
        Nwords = 10
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.list_topic.png'
        with Profile(pcgpath):
            result = self.model.list_topic(0, Nwords=Nwords)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], str)
        self.assertEqual(len(result), Nwords)
        
    def test_print_topic(self):
        """
        :func:`.print_topic` should yield a string with ``Nwords`` words.
        """
        Nwords = 10
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.print_topic.png'
        with Profile(pcgpath):
            result = self.model.print_topic(0, Nwords=Nwords)
        
        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split(', ')), Nwords)

    def test_list_topics(self):
        """
        :func:`.list_topics` should yield a dict { k : [ w ], }.
        """

        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.list_topics.png'
        with Profile(pcgpath):
            result = self.model.list_topics(Nwords=Nwords)

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], list)
        self.assertIsInstance(result.values()[0][0], str)
        self.assertEqual(len(result), self.model.Z)

    def test_print_topics(self):
        Nwords = 10

        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.print_topics.png'
        with Profile(pcgpath):
            result = self.model.print_topics(Nwords=Nwords)

        self.assertIsInstance(result, str)
        self.assertEqual(len(result.split('\n')), self.model.Z)

    def test__item_description(self):
        result = self.model._item_description(0)
    
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)
        self.assertIsInstance(result[0][0], int)
        self.assertIsInstance(result[0][1], float)
        self.assertEqual(len(result), self.model.Z)

    def test__dimension_description(self):
        result = self.model._dimension_description(0)

        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)
        self.assertIsInstance(result[0][0], int)
        self.assertIsInstance(result[0][1], float)
        self.assertEqual(len(result), self.model.W)

    def test__dimension_items(self):
        """
        With threshold=0., should return a list with model.M entries.
        """
        result = self.model._dimension_items(0, threshold=0.)
    
        self.assertIsInstance(result, list)
        self.assertIsInstance(result[0], tuple)
        self.assertIsInstance(result[0][0], str)
        self.assertIsInstance(result[0][1], float)
        self.assertEqual(len(result), self.model.M)

    def test__dimension_items_threshold(self):
        """
        With threshold=0.05, should return a shorter list.
        """
        
        threshold = 0.05
        result = self.model._dimension_items(0, threshold=threshold)
    
        self.assertEqual(len(result), 83)
        for r in result:
            self.assertGreaterEqual(r[1], threshold)

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()
