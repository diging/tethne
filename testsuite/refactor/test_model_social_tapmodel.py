# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
cg_path = './callgraphs/'

import unittest
import numpy as np
import networkx as nx
import random

import sys
sys.path.append('../../')

from tethne.model.social.tapmodel import TAPModel

import logging
logging.basicConfig()
logger = logging.getLogger('tethne.model.social.tapmodel')
logger.setLevel('ERROR')

N = 10  # nodes
E = 20  # edges
Z = 5   # topics

class TestTAPModel(unittest.TestCase):
    def setUp(self):
        self.graph = nx.gnm_random_graph(N,E)
        for e in self.graph.edges():
            self.graph[e[0]][e[1]]['weight'] = random.random()
        
        self.atheta = { n : np.random.random((Z))/Z for n in self.graph.nodes() }
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel.__init__.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.T = TAPModel(self.graph, self.atheta)
        else:
            self.T = TAPModel(self.graph, self.atheta)

    def test_init(self):
        # should infer N nodes and T topics.
        self.assertEqual(self.T.N, N)
        self.assertEqual(self.T.T, Z)

        self.assertEqual(len(self.T.yold), N)

        
    def test_calculate_g(self):
        # g, b, r, a should each have N entries (1 per node).
        self.assertEqual(len(self.T.g), N)

        # g and b should each sum > 0.
        self.assertTrue(np.sum(self.T.g) > 0.)

    def test_calculate_b(self):
        # g, b, r, a should each have N entries (1 per node).
        self.assertEqual(len(self.T.b), N)
        self.assertEqual(len(self.T.r), N)
        self.assertEqual(len(self.T.a), N)

        # g and b should each sum > 0.
        self.assertTrue(np.sum(self.T.b) > 0.)

    def test_update_r(self):
        """
        values in r should change after an update.
        """
        before = np.sum(self.T.r[0])
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._update_r.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.T._update_r()
        else:
            self.T._update_r()

        after = np.sum(self.T.r[0])
        self.assertNotEqual(before, after)

    def test_update_a(self):
        """
        values in a should change after an update.
        """
        before = np.max(self.T.a[0])
        self.T._update_r()
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._update_a.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.T._update_a()
        else:
            self.T._update_a()

        after = np.max(self.T.a[0])
        self.assertNotEqual(before, after)

    def test_check_convergence(self):
        """
        should return a tuple nc(int), cont(bool).
        """
        self.T._update_r()
        self.T._update_a()
        self.T.iteration = 0
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._check_convergence.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                nc,cont = self.T._check_convergence(0)
        else:
            nc,cont = self.T._check_convergence(0)
        
        self.assertIsInstance(nc, int)
        self.assertIsInstance(cont, bool)

    def test_calculate_mu(self):
        """
        should generate a dictionary of DiGraphs, T.MU, of size Z.
        """

        self.T._update_r()
        self.T._update_a()
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._calculate_mu.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.T._calculate_mu()
        else:
            self.T._calculate_mu()

        self.assertIsInstance(self.T.MU, dict)
        self.assertEqual(len(self.T.MU), Z)
        self.assertIsInstance(self.T.MU[0], nx.DiGraph)

    def test_prime(self):
        """
        Assigns values from r and a
        """
        self.T._update_r()
        self.T._update_a()

        graph_ = nx.gnm_random_graph(N,E)
        for e in graph_.edges():
            graph_[e[0]][e[1]]['weight'] = random.random()

        atheta_ = { n : np.random.random((Z))/Z for n in xrange(N) }

        T_ = TAPModel(graph_, atheta_)
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel.prime.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                T_.prime(self.T.r, self.T.a, self.graph)
        else:
            T_.prime(self.T.r, self.T.a, self.graph)

    def test_item_description(self):
        """
        should return a list of ( t , w ) tuples.
        """
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._item_description.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                description = self.T._item_description(0)
        else:
            description = self.T._item_description(0)
        
        self.assertIsInstance(description, list)
        self.assertIsInstance(description[0], tuple)
        self.assertIsInstance(description[0][0], int)
        self.assertIsInstance(description[0][1], float)
        
    def test_item_relationship(self):
        """
        should return a list of ( t , w ) tuples.
        """
        
        # Requires values for mu.
        self.assertRaises(RuntimeError, self.T._item_relationship, 0, 1)
        
        self.T._update_r()
        self.T._update_a()
        self.T._calculate_mu()
        
        e = self.T.MU[0].edges()[0]
        i,j = e[0], e[1]
        
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel._item_relationship.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                description = self.T._item_relationship(i,j)
        else:
            description = self.T._item_relationship(i,j)
        
        self.assertIsInstance(description, list)
        self.assertIsInstance(description[0], tuple)
        self.assertIsInstance(description[0][0], int)
        self.assertIsInstance(description[0][1], float)

    def test_build(self):
        if profile:
            pcgpath = cg_path + 'model.social.tapmodel.TAPModel.build.png'
            with PyCallGraph(output=GraphvizOutput(output_file=pcgpath)):
                self.T.build()
        else:
            self.T.build()

if __name__ == '__main__':
    profile = False

    datapath = './data'
    unittest.main()