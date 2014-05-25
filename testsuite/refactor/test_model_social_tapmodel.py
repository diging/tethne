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
        self.atheta = np.random.random((N,Z))/10    # so that rows sum < 1.
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
        self.T._update_r()
        after = np.sum(self.T.r[0])
        self.assertNotEqual(before, after)

    def test_update_a(self):
        """
        values in a should change after an update.
        """
        before = np.max(self.T.a[0])
        self.T._update_r()
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
        nc,cont = self.T._check_convergence(0)
        self.assertIsInstance(nc, int)
        self.assertIsInstance(cont, bool)

    def test_calculate_mu(self):
        """
        should generate a dictionary of DiGraphs, T.MU, of size Z.
        """

        self.T._update_r()
        self.T._update_a()
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
        atheta_ = np.random.random((N,Z))/10    # so that rows sum < 1.

        T_ = TAPModel(graph_, atheta_)
        T_.prime(self.T.r, self.T.a, self.graph)

    def test_item_description(self):
        """
        should return a list of ( t , w ) tuples.
        """
        
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
        description = self.T._item_relationship(i,j)
        self.assertIsInstance(description, list)
        self.assertIsInstance(description[0], tuple)
        self.assertIsInstance(description[0][0], int)
        self.assertIsInstance(description[0][1], float)

#    def test_build(self):
#        T.build()

if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()