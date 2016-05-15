import sys
sys.path.append('../tethne')

import unittest

import networkx as nx

from tethne.readers.wos import read
from tethne.networks.papers import *

datapath = './tethne/tests/data/wos2.txt'


class TestAuthorPapers(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)

    def test_direct_citation(self):
        g = direct_citation(self.corpus)

        self.assertIsInstance(g, nx.DiGraph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        types = set([attr['type'] for n, attr in g.nodes(data=True)])
        self.assertEqual(len(types), 2, "Bipartite graph")
        self.assertSetEqual(types, set(['paper', 'citations']),
                            "Containing papers and their citations.")

    def test_bibliographic_coupling(self):
        g = bibliographic_coupling(self.corpus)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)
            self.assertIn('features', attrs)
            for f in attrs['features']:
                self.assertIn(f, self.corpus.indices['citations'])

    def test_cocitation(self):
        g = cocitation(self.corpus, min_weight=2)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)

    def test_author_coupling(self):
        g = author_coupling(self.corpus)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)
            self.assertIn('features', attrs)
            for f in attrs['features']:
                self.assertIn(f, self.corpus.indices['authors'])


class TestAuthorPapersWithStreaming(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, streaming=True)

    def test_direct_citation(self):
        g = direct_citation(self.corpus)

        self.assertIsInstance(g, nx.DiGraph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        types = set([attr['type'] for n, attr in g.nodes(data=True)])
        self.assertEqual(len(types), 2, "Bipartite graph")
        self.assertSetEqual(types, set(['paper', 'citations']),
                            "Containing papers and their citations.")

    def test_bibliographic_coupling(self):
        g = bibliographic_coupling(self.corpus)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)
            self.assertIn('features', attrs)
            for f in attrs['features']:
                self.assertIn(f, self.corpus.indices['citations'])

    def test_cocitation(self):
        g = cocitation(self.corpus, min_weight=2)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)

    def test_author_coupling(self):
        g = author_coupling(self.corpus)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for s, t, attrs in g.edges(data=True):
            self.assertIn('weight', attrs)
            self.assertIn('features', attrs)
            for f in attrs['features']:
                self.assertIn(f, self.corpus.indices['authors'])


if __name__ == '__main__':
    unittest.main()
