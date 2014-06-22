from settings import *

import unittest

from tethne.model.corpus import ldamodel

import numpy

class TestLoad(unittest.TestCase):
    def setUp(self):
        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)

    def test__handle_top_doc(self):
        """
        :func:`._handle_top_doc` should return a Numpy matrix with non-zero
        values.
        """
    
        pcgpath = cg_path + 'model.corpus.ldamodel._handle_top_doc.png'
        with Profile(pcgpath):
            td = ldamodel._handle_top_doc(self.dt_path)

        self.assertIsInstance(td, numpy.matrixlib.defmatrix.matrix)
        self.assertEqual(td.shape, (241,20))
        self.assertGreater(numpy.sum(td), 0.)
        
    def test__handle_word_top(self):
        """
        :func:`._handle_word_top` should return a Numpy matrix with non-zero
        values.
        """
    
        pcgpath = cg_path + 'model.corpus.ldamodel._handle_word_top.png'
        with Profile(pcgpath):
            wt = ldamodel._handle_word_top(self.wt_path)

        self.assertIsInstance(wt, numpy.matrixlib.defmatrix.matrix)
        self.assertEqual(wt.shape, (20, 51290))
        self.assertGreater(numpy.sum(wt), 0.)
        
    def test__handle_metadata(self):
        """
        :func:`._handle_metadata` should return a dictionary mapping int : str.
        """
    
        pcgpath = cg_path + 'model.corpus.ldamodel._handle_metadata.png'
        with Profile(pcgpath):
            meta = ldamodel._handle_metadata(self.meta_path)
            
        self.assertIsInstance(meta, dict)
        self.assertEqual(len(meta), 241)
        self.assertIsInstance(meta.keys()[0], int)
        self.assertIsInstance(meta.values()[0], str)

    def test_from_mallet(self):
        """
        :func:`.from_mallet` should return a :class:`.LDAModel`.
        """
        
        pcgpath = cg_path + 'model.corpus.ldamodel.from_mallet.png'
        with Profile(pcgpath):
            model = ldamodel.from_mallet(   self.dt_path,
                                            self.wt_path,
                                            self.meta_path  )

        self.assertIsInstance(model, ldamodel.LDAModel)
        self.assertEqual(model.Z, 20)
        self.assertEqual(model.M, 241)
        self.assertEqual(model.W, 51290)

class TestLDAModel(unittest.TestCase):
    def setUp(self):
        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)
        self.model = ldamodel.from_mallet(  self.dt_path,
                                            self.wt_path,
                                            self.meta_path  )

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
    
        self.assertEqual(len(result), 44)
        for r in result:
            self.assertGreaterEqual(r[1], threshold)

if __name__ == '__main__':
    unittest.main()