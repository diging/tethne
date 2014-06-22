# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
cg_path = './callgraphs/'

import unittest

import sys
sys.path.append('../../')
from tethne.model.corpus import dtmmodel

import numpy

class TestLoad(unittest.TestCase):
    def setUp(self):
        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
        self.target_path = '{0}/dtm/model_run'.format(datapath)

    def test_from_gerrish(self):
        """
        :func:`.from_gerrish` should load a :class:`.DTMModel`\.
        """

        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.from_gerrish.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                model = dtmmodel.from_gerrish(  self.target_path,
                                                self.meta_path,
                                                self.vocab_path )
        else:
            model = dtmmodel.from_gerrish(  self.target_path,
                                            self.meta_path,
                                            self.vocab_path )
        
        
        self.assertIsInstance(model, dtmmodel.DTMModel)
        self.assertEqual(model.Z, 5)
        self.assertEqual(model.M, 176)
        self.assertEqual(model.W, 51638)
        self.assertEqual(model.T, 5)

        self.assertIsInstance(model.vocabulary, dict)
        self.assertGreater(len(model.vocabulary), 0)
        self.assertIsInstance(model.vocabulary.keys()[0], int)
        self.assertIsInstance(model.vocabulary.values()[1], str)
        
        self.assertIsInstance(model.metadata, dict)
        self.assertGreater(len(model.metadata), 0)
        self.assertIsInstance(model.metadata.keys()[0], int)

class test_GerrishLoader(unittest.TestCase):
    def setUp(self):
        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
        self.target_path = '{0}/dtm/model_run'.format(datapath)

        self.G = dtmmodel.GerrishLoader(    self.target_path,
                                            self.meta_path,
                                            self.vocab_path )

    def test__handle_metadata(self):
        """
        :func:`._handle_metadata` should return a dict with { i : str } and 
        update ``G.metadata``.
        """
        
        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_metadata.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.G._handle_metadata()
        else:
            result = self.G._handle_metadata()

        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], str)
        self.assertEqual(self.G.metadata, result)

    def test__handle_vocabulary(self):
        """
        :func:`._handle_vocabulary` should return a dict with { i : str }
        and update ``G.vocabulary``.
        """
        
        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_vocabulary.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                result = self.G._handle_vocabulary()
        else:
            result = self.G._handle_vocabulary()
        
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.keys()[0], int)
        self.assertIsInstance(result.values()[0], str)
        self.assertEqual(self.G.vocabulary, result)

    def test__handle_metaparams(self):
        """
        :func:`._handle_metaparams` should update G with alphas, and number of
        topics, words, and time periods.
        """
        
        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_metaparams.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.G._handle_metaparams()
        else:
            self.G._handle_metaparams()

        self.assertEqual(self.G.N_z, 5)
        self.assertEqual(self.G.N_w, 51638)
        self.assertEqual(self.G.N_t, 5)
        self.assertEqual(len(self.G.A), self.G.N_t)
        self.assertEqual(self.G.A[0], '0.01000000000000')

    def test__handle_gammas(self):
        """
        :func:`._handle_gammas` should update ``G.N_d``, and ``G.e_theta`` with 
        shape ``(G.N_z, G.N_d)``.
        """
        
        self.G._handle_metaparams()
        
        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_gammas.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.G._handle_gammas()
        else:
            self.G._handle_gammas()

        self.assertEqual(self.G.N_d, 176)
        self.assertEqual(self.G.e_theta.shape, (self.G.N_z, self.G.N_d))
        self.assertGreater(numpy.sum(self.G.e_theta), 0.)

    def test__handle_prob(self):
        """
        :func:`._handle_prob` should update ``G.tdict[z]``.
        """

        self.G._handle_metaparams()

        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel._handle_prob.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.G._handle_prob('topic-000-var-e-log-prob.dat', 0)
        else:
            self.G._handle_prob('topic-000-var-e-log-prob.dat', 0)

        self.assertEqual(self.G.tdict[0].shape[0], self.G.N_w)
        self.assertEqual(self.G.tdict[0].shape[1], self.G.N_t)
        self.assertIsInstance(self.G.tdict[0], numpy.ndarray)

    def test_load(self):
        """
        Should pass all of the tests for the individual handlers, and return a
        """
        
        if profile:
            pcgpath = cg_path + 'model.corpus.dtmmodel.DTMModel.load.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                model = self.G.load()
        else:
            model = self.G.load()
        
        self.assertIsInstance(model, dtmmodel.DTMModel)
        
        # Model has a vocabulary.
        self.assertIsInstance(model.vocabulary, dict)
        self.assertGreater(len(model.vocabulary), 0)
        self.assertIsInstance(model.vocabulary.keys()[0], int)
        self.assertIsInstance(model.vocabulary.values()[1], str)
        
        # Model has metadata.
        self.assertIsInstance(model.metadata, dict)
        self.assertGreater(len(model.metadata), 0)
        self.assertIsInstance(model.metadata.keys()[0], int)
        
        # Model has metaparams.
        self.assertEqual(model.Z, 5)
        self.assertEqual(model.M, 176)
        self.assertEqual(model.W, 51638)
        self.assertEqual(model.T, 5)        
        
        # Metadata.
        self.assertIsInstance(self.G.metadata, dict)
        self.assertIsInstance(self.G.metadata.keys()[0], int)
        self.assertIsInstance(self.G.metadata.values()[0], str)

        # Vocabulary.
        result = self.G._handle_vocabulary()
        self.assertIsInstance(self.G.vocabulary, dict)
        self.assertIsInstance(self.G.vocabulary.keys()[0], int)
        self.assertIsInstance(self.G.vocabulary.values()[0], str)

        # Metaparams.
        self.assertEqual(self.G.N_z, 5)
        self.assertEqual(self.G.N_w, 51638)
        self.assertEqual(self.G.N_t, 5)
        self.assertEqual(len(self.G.A), self.G.N_t)
        self.assertEqual(self.G.A[0], '0.01000000000000')

        # Gammas.
        self.assertEqual(self.G.N_d, 176)
        self.assertEqual(self.G.e_theta.shape, (self.G.N_z, self.G.N_d))
        self.assertGreater(numpy.sum(self.G.e_theta), 0.)

        # Probs.
        for k in xrange(self.G.N_z):
            self.assertEqual(self.G.tdict[k].shape[0], self.G.N_w)
            self.assertEqual(self.G.tdict[k].shape[1], self.G.N_t)
            self.assertIsInstance(self.G.tdict[k], numpy.ndarray)

if __name__ == '__main__':
    profile = False
    
    datapath = './data'
    temppath = './sandbox/temp'
    outpath = './sandbox/out'
    mallet_path = '/Applications/mallet-2.0.7'
    
    unittest.main()