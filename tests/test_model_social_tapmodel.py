from settings import *

import unittest
import numpy as np
import networkx as nx
import random
import csv

from tethne.model.social.tapmodel import TAPModel
from tethne.readers import wos, dfr
from tethne import GraphCollection
from tethne.networks.authors import coauthors
from tethne.model.managers import MALLETModelManager, TAPModelManager

N = 10  # nodes
E = 20  # edges
Z = 5   # topics

class TestTAPModelTestData(unittest.TestCase):
    def test_build(self):
        edgepath = '/Users/erickpeirson/Downloads/Topic-Affinity-Propagation/edge.txt'
        distpath = '/Users/erickpeirson/Downloads/Topic-Affinity-Propagation/distribution.txt'

        graph = nx.Graph()

        # Load edge data into Graph.
        with open(edgepath, 'r') as f:
            reader = csv.reader(f, delimiter=' ')
            for line in reader:
                try:
                    graph.add_edge(int(line[1]), int(line[2]), weight=float(line[3]))
                except:
                    pass
        authors = { n:n for n in graph.nodes() }

        # Load dist data into atheta.
        atheta = {}
        with open(distpath, 'r') as f:
            reader = csv.reader(f, delimiter=' ')
            i = 0
            for line in reader:
                data = line[1:-1]
                if len(data) > 0:
                    if i in graph.nodes():
                        atheta[i] = np.array([ float(d) for d in data ])
                    i += 1


        # Estimate params.
        tapmodel = TAPModel(graph, atheta)
        tapmodel.build()

class TestTAPModelRealData(unittest.TestCase):
    def test_build(self):
        corpus = dfr.read_corpus(datapath + '/dfr', features=['uni'])
        def filt(s, C, DC):
            if C > 3 and DC > 1 and len(s) > 3:
                return True
            return False
        corpus.filter_features('unigrams', 'unigramsF', filt)
        corpus.slice('date', 'time_period', window_size=3)

        G = GraphCollection().build(corpus, 'date', 'authors', 'coauthors')
        graph = G.graphs[1965]

        manager = MALLETModelManager(corpus, 'unigramsF', mallet_path=mallet_path)
        manager.prep()
        model = manager.build(Z=20, max_iter=100)

        tmanager = TAPModelManager(corpus, model=model)
        authors = { n[1]['label']:n[0] for n in graph.nodes(data=True) }
        atheta = tmanager.author_theta(corpus.all_papers(), authors, indexed_by='doi')
        atheta[17][0] = 0.999
        atheta[14][0] = 0.555

        tapmodel = TAPModel(graph, atheta)

        before = np.sum(tapmodel.r[11])
        tapmodel._update_r()
        after = np.sum(tapmodel.r[11])
        self.assertNotEqual(before, after)

        before = np.sum(tapmodel.a[11])
        tapmodel._update_a()
        after = np.sum(tapmodel.a[11])
        self.assertNotEqual(before, after)

        tapmodel.iteration = 100

        tapmodel.build()

        mu = tapmodel._calculate_mu()
        sampleweight = tapmodel.MU[0].edges(data=True)[0][2]['weight']
        sampletheta = tapmodel.MU[0].nodes(data=True)[0][1]['theta']
        self.assertEqual(type(sampleweight), float)
        self.assertEqual(type(sampletheta), float)

class TestTAPModel(unittest.TestCase):
    def setUp(self):
        self.graph = nx.gnm_random_graph(N,E)
        for e in self.graph.edges():
            self.graph[e[0]][e[1]]['weight'] = random.random()
        
        self.atheta = { n : np.random.random((Z))/Z for n in self.graph.nodes() }
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel.__init__.png'
        with Profile(pcgpath):
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
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._update_r.png'
        with Profile(pcgpath):
            self.T._update_r()

        after = np.sum(self.T.r[0])
        self.assertNotEqual(before, after)

    def test_update_a(self):
        """
        values in a should change after an update.
        """
        before = np.max(self.T.a[0])
        self.T._update_r()
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._update_a.png'
        with Profile(pcgpath):
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
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._check_convergence.png'
        with Profile(pcgpath):
            nc,cont = self.T._check_convergence(0)
        
        self.assertIsInstance(nc, int)
        self.assertIsInstance(cont, bool)

    def test_calculate_mu(self):
        """
        should generate a dictionary of DiGraphs, T.MU, of size Z.
        """

        self.T._update_r()
        self.T._update_a()
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._calculate_mu.png'
        with Profile(pcgpath):
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
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel.prime.png'
        with Profile(pcgpath):
            T_.prime(self.T.r, self.T.a, self.graph)

    def test_item_description(self):
        """
        should return a list of ( t , w ) tuples.
        """
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._item_description.png'
        with Profile(pcgpath):
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
        
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel._item_relationship.png'
        with Profile(pcgpath):
            description = self.T._item_relationship(i,j)
        
        self.assertIsInstance(description, list)
        self.assertIsInstance(description[0], tuple)
        self.assertIsInstance(description[0][0], int)
        self.assertIsInstance(description[0][1], float)

    def test_build(self):
        pcgpath = cg_path + 'model.social.tapmodel.TAPModel.build.png'
        with Profile(pcgpath):
            self.T.build()

if __name__ == '__main__':
    unittest.main()