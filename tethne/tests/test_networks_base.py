import sys
sys.path.append('./')

import unittest

from tethne.networks.base import cooccurrence, coupling, multipartite
from tethne.classes.corpus import Corpus
from tethne.classes.streaming import StreamingCorpus
from tethne.readers.wos import WoSParser

import networkx as nx

datapath = './tethne/tests/data/wos.txt'


class TestBaseNetworkMethods(unittest.TestCase):
    def setUp(self):
        papers = WoSParser(datapath).parse()
        self.corpus = Corpus(papers, index_features=['authors', 'citations'])

    def test_coocurrence(self):
        g = cooccurrence(self.corpus, 'authors')

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)

    def test_coocurrence_feature(self):
        g = cooccurrence(self.corpus.features['authors'])

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)

    def test_coupling(self):
        g = coupling(self.corpus, 'citations')
        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)
        for s, t, attrs in g.edges(data=True):
            self.assertEqual(len(attrs['features']), attrs['weight'])

    def test_coupling_feature(self):
        g = coupling(self.corpus.features['citations'])

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)
        for s, t, attrs in g.edges(data=True):
            self.assertEqual(len(attrs['features']), attrs['weight'])

    def test_coupling_min_weight(self):
        """
        Limit edges to weight >= 3.
        """

        min_weight = 3
        g = coupling(self.corpus, 'citations')
        g2 = coupling(self.corpus, 'citations', min_weight=min_weight)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g2.nodes()), 0)
        self.assertGreater(len(g.nodes()), len(g2.nodes()))
        self.assertGreater(len(g2.edges()), 0)
        self.assertGreater(len(g.edges()), len(g2.edges()))

        for s, t, attrs in g2.edges(data=True):
            self.assertGreaterEqual(attrs['weight'], min_weight)

    def test_multipartite(self):
        fsets = ['citations', 'authors']
        g = multipartite(self.corpus, fsets)

        # All nodes should be typed.
        types = set()
        self.assertIsInstance(g, nx.Graph)
        for n, attrs in g.nodes(data=True):
            self.assertIn('type', attrs)
            types.add(attrs['type'])
        for t in list(types):
            self.assertIn(t, fsets + ['paper'])
        self.assertEqual(len(types), 3)


class TestBaseNetworkMethodsWithStreaming(unittest.TestCase):
    def setUp(self):
        papers = WoSParser(datapath).parse()
        self.corpus = StreamingCorpus(papers, index_features=['authors', 'citations'])

    def test_coocurrence(self):
        g = cooccurrence(self.corpus, 'authors')

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)

    def test_coocurrence_feature(self):
        g = cooccurrence(self.corpus.features['authors'])

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)

    def test_coupling(self):
        g = coupling(self.corpus, 'citations')

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)
        for s, t, attrs in g.edges(data=True):
            self.assertEqual(len(attrs['features']), attrs['weight'])

    def test_coupling_feature(self):
        g = coupling(self.corpus.features['citations'])

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g.nodes()), 0)
        self.assertGreater(len(g.edges()), 0)
        for s, t, attrs in g.edges(data=True):
            self.assertEqual(len(attrs['features']), attrs['weight'])

    def test_coupling_min_weight(self):
        """
        Limit edges to weight >= 3.
        """

        min_weight = 3
        g = coupling(self.corpus, 'citations')
        g2 = coupling(self.corpus, 'citations', min_weight=min_weight)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(len(g2.nodes()), 0)
        self.assertGreater(len(g.nodes()), len(g2.nodes()))
        self.assertGreater(len(g2.edges()), 0)
        self.assertGreater(len(g.edges()), len(g2.edges()))

        for s, t, attrs in g2.edges(data=True):
            self.assertGreaterEqual(attrs['weight'], min_weight)

    def test_multipartite(self):
        fsets = ['citations', 'authors']
        g = multipartite(self.corpus, fsets)

        # All nodes should be typed.
        types = set()
        self.assertIsInstance(g, nx.Graph)
        for n, attrs in g.nodes(data=True):
            self.assertIn('type', attrs)
            types.add(attrs['type'])
        for t in list(types):
            self.assertIn(t, fsets + ['paper'])
        self.assertEqual(len(types), 3)

#        papers = WoSParser(datapath).parse()
#        for paper in papers:
#            print hasattr(paper, 'authorAddress')


if __name__ == '__main__':
    unittest.main()
