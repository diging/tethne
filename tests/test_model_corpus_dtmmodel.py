from settings import *

import unittest

from tethne.model.corpus import dtmmodel

import numpy

class TestPrint(unittest.TestCase):
    def setUp(self):
        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
        self.target_path = '{0}/dtm/model_run'.format(datapath)
        self.model = dtmmodel.from_gerrish(  self.target_path,
                                             self.meta_path,
                                             self.vocab_path )

#    def test_list_topic(self):
#        """
#        :func:`.list_topic` should yield a list with ``Nwords`` words.
#        """
#
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.list_topic.png'
#        with Profile(pcgpath):
#            result = self.model.list_topic(0, 0, Nwords=Nwords)
#
#        self.assertIsInstance(result, list)
#        self.assertIsInstance(result[0], str)
#        self.assertEqual(len(result), Nwords)

    def test_plot_topic_evolution(self):
        Nwords = 5
        K, R = self.model.topic_evolution(2, Nwords=Nwords)

        self.assertIsInstance(K, list)
        self.assertIsInstance(R, dict)
        self.assertIsInstance(R.keys()[0], str) #   Word
        self.assertIsInstance(R.values()[0], list)  # p over time.
        self.assertEqual(len(K), len(R.values()[0]))

#    def test_list_topic_diachronic(self):
#        """
#        :func:`.list_topic_diachronic` should yield a dict with ``T`` entries,
#        each with a list of ``Nwords`` words.
#        """
#
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.list_topic_diachronic.png'
#        with Profile(pcgpath):
#            result = self.model.list_topic_diachronic(0, Nwords=Nwords)
#
#        self.assertIsInstance(result, dict)
#        self.assertEqual(len(result), self.model.T)
#        self.assertIsInstance(result.keys()[0], int)
#        self.assertIsInstance(result[0], list)
#        self.assertEqual(len(result[0]), Nwords)
#
#    def test_print_topic_diachronic(self):
#        """
#        :func:`.print_topic` should yield a string with ``Nwords`` words.
#        """
#    
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.print_topic.png'
#        with Profile(pcgpath):
#            result = self.model.print_topic_diachronic(0, Nwords=Nwords)
#        
#        self.assertIsInstance(result, str)
#        self.assertEqual(len(result.split('\n')), self.model.T)
#
#    def test_print_topic(self):
#        """
#        :func:`.print_topic` should yield a string with ``Nwords`` words.
#        """
#    
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.print_topic.png'
#        with Profile(pcgpath):
#            result = self.model.print_topic(0, 0, Nwords=Nwords)
#        
#        self.assertIsInstance(result, str)
#        self.assertEqual(len(result.split(', ')), Nwords)
#
#    def test_list_topics(self):
#        """
#        :func:`.list_topics` should yield a dict { k : [ w ], }.
#        """
#
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.list_topics.png'
#        with Profile(pcgpath):
#            result = self.model.list_topics(0, Nwords=Nwords)
#
#        self.assertIsInstance(result, dict)
#        self.assertIsInstance(result.keys()[0], int)
#        self.assertIsInstance(result.values()[0], list)
#        self.assertIsInstance(result.values()[0][0], str)
#        self.assertEqual(len(result), self.model.Z)
#
#    def test_print_topics(self):
#        Nwords = 10
#
#        pcgpath = cg_path + 'model.corpus.DTMModel.print_topics.png'
#        with Profile(pcgpath):
#            result = self.model.print_topics(0, Nwords=Nwords)
#
#        self.assertIsInstance(result, str)
#        self.assertEqual(len(result.split('\n')), self.model.Z)
#
#
#class TestLoad(unittest.TestCase):
#    def setUp(self):
#        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
#        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
#        self.target_path = '{0}/dtm/model_run'.format(datapath)
#    
#    def test_from_gerrish(self):
#        """
#        :func:`.from_gerrish` should load a :class:`.DTMModel`\.
#        """
#
#        pcgpath = cg_path + 'model.corpus.dtmmodel.from_gerrish.png'
#        with Profile(pcgpath):
#            model = dtmmodel.from_gerrish(  self.target_path,
#                                            self.meta_path,
#                                            self.vocab_path )
#        
#        self.assertIsInstance(model, dtmmodel.DTMModel)
#        self.assertEqual(model.Z, 5)
#        self.assertEqual(model.M, 176)
#        self.assertEqual(model.W, 51638)
#        self.assertEqual(model.T, 5)
#
#        self.assertIsInstance(model.vocabulary, dict)
#        self.assertGreater(len(model.vocabulary), 0)
#        self.assertIsInstance(model.vocabulary.keys()[0], int)
#        self.assertIsInstance(model.vocabulary.values()[1], str)
#        
#        self.assertIsInstance(model.metadata, dict)
#        self.assertGreater(len(model.metadata), 0)
#        self.assertIsInstance(model.metadata.keys()[0], int)
#
#class test_GerrishLoader(unittest.TestCase):
#    def setUp(self):
#        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
#        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
#        self.target_path = '{0}/dtm/model_run'.format(datapath)
#
#        self.G = dtmmodel.GerrishLoader(    self.target_path,
#                                            self.meta_path,
#                                            self.vocab_path )
#
#    def test__handle_metadata(self):
#        """
#        :func:`._handle_metadata` should return a dict with { i : str } and 
#        update ``G.metadata``.
#        """
#        
#        pcgpath = cg_path +'model.corpus.dtmmodel.DTMModel._handle_metadata.png'
#        with Profile(pcgpath):
#            result = self.G._handle_metadata()
#
#        self.assertIsInstance(result, dict)
#        self.assertIsInstance(result.keys()[0], int)
#        self.assertIsInstance(result.values()[0], dict)
#        self.assertIsInstance(result.values()[0]['id'], str)
#        self.assertEqual(self.G.metadata, result)
#
#    def test__handle_vocabulary(self):
#        """
#        :func:`._handle_vocabulary` should return a dict with { i : str }
#        and update ``G.vocabulary``.
#        """
#        
#        pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_vocabulary.png'
#        with Profile(pcgpath):
#            result = self.G._handle_vocabulary()
#        
#        self.assertIsInstance(result, dict)
#        self.assertIsInstance(result.keys()[0], int)
#        self.assertIsInstance(result.values()[0], str)
#        self.assertEqual(self.G.vocabulary, result)
#
#    def test__handle_metaparams(self):
#        """
#        :func:`._handle_metaparams` should update G with alphas, and number of
#        topics, words, and time periods.
#        """
#        
#        pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_metaparams.png'
#        with Profile(pcgpath):
#            self.G._handle_metaparams()
#
#        self.assertEqual(self.G.N_z, 5)
#        self.assertEqual(self.G.N_w, 51638)
#        self.assertEqual(self.G.N_t, 5)
#        self.assertEqual(len(self.G.A), self.G.N_t)
#        self.assertEqual(self.G.A[0], '0.01000000000000')
#
#    def test__handle_gammas(self):
#        """
#        :func:`._handle_gammas` should update ``G.N_d``, and ``G.e_theta`` with 
#        shape ``(G.N_z, G.N_d)``.
#        """
#        
#        self.G._handle_metaparams()
#        
#        pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_gammas.png'
#        with Profile(pcgpath):
#            self.G._handle_gammas()
#
#        self.assertEqual(self.G.N_d, 176)
#        self.assertEqual(self.G.e_theta.shape, (self.G.N_z, self.G.N_d))
#        self.assertGreater(numpy.sum(self.G.e_theta), 0.)
#
#    def test__handle_prob(self):
#        """
#        :func:`._handle_prob` should update ``G.tdict[z]``.
#        """
#
#        self.G._handle_metaparams()
#
#        pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_prob.png'
#        with Profile(pcgpath):
#            self.G._handle_prob('topic-000-var-e-log-prob.dat', 0)
#
#        self.assertEqual(self.G.tdict[0].shape[0], self.G.N_w)
#        self.assertEqual(self.G.tdict[0].shape[1], self.G.N_t)
#        self.assertIsInstance(self.G.tdict[0], numpy.ndarray)
#
#    def test_load(self):
#        """
#        Should pass all of the tests for the individual handlers, and return a
#        """
#        
#        pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel.load.png'
#        with Profile(pcgpath):
#            model = self.G.load()
#        
#        self.assertIsInstance(model, dtmmodel.DTMModel)
#        
#        # Model has a vocabulary.
#        self.assertIsInstance(model.vocabulary, dict)
#        self.assertGreater(len(model.vocabulary), 0)
#        self.assertIsInstance(model.vocabulary.keys()[0], int)
#        self.assertIsInstance(model.vocabulary.values()[1], str)
#        
#        # Model has metadata.
#        self.assertIsInstance(model.metadata, dict)
#        self.assertGreater(len(model.metadata), 0)
#        self.assertIsInstance(model.metadata.keys()[0], int)
#        
#        # Model has metaparams.
#        self.assertEqual(model.Z, 5)
#        self.assertEqual(model.M, 176)
#        self.assertEqual(model.W, 51638)
#        self.assertEqual(model.T, 5)        
#        
#        # Metadata.
#        self.assertIsInstance(self.G.metadata, dict)
#        self.assertIsInstance(self.G.metadata.keys()[0], int)
#        self.assertIsInstance(self.G.metadata.values()[0], dict)
#        self.assertIsInstance(self.G.metadata.values()[0]['id'], str)
#
#        # Vocabulary.
#        result = self.G._handle_vocabulary()
#        self.assertIsInstance(self.G.vocabulary, dict)
#        self.assertIsInstance(self.G.vocabulary.keys()[0], int)
#        self.assertIsInstance(self.G.vocabulary.values()[0], str)
#
#        # Metaparams.
#        self.assertEqual(self.G.N_z, 5)
#        self.assertEqual(self.G.N_w, 51638)
#        self.assertEqual(self.G.N_t, 5)
#        self.assertEqual(len(self.G.A), self.G.N_t)
#        self.assertEqual(self.G.A[0], '0.01000000000000')
#
#        # Gammas.
#        self.assertEqual(self.G.N_d, 176)
#        self.assertEqual(self.G.e_theta.shape, (self.G.N_z, self.G.N_d))
#        self.assertGreater(numpy.sum(self.G.e_theta), 0.)
#
#        # Probs.
#        for k in xrange(self.G.N_z):
#            self.assertEqual(self.G.tdict[k].shape[0], self.G.N_w)
#            self.assertEqual(self.G.tdict[k].shape[1], self.G.N_t)
#            self.assertIsInstance(self.G.tdict[k], numpy.ndarray)

if __name__ == '__main__':
    unittest.main()