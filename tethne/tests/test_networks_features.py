import sys
sys.path.append('../tethne')

import unittest

import networkx as nx

from tethne.readers.wos import read
from tethne.networks.features import *

datapath = './tethne/tests/data/wos2.txt'


class TestAuthorPapers(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)

    def test_feature_cooccurrence(self):
        g = feature_cooccurrence(self.corpus, 'citations')

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

        for n, attrs in g.nodes(data=True):
            self.assertIn('count', attrs)
            self.assertIn('documentCount', attrs)

    def test_mutual_information(self):
        g = mutual_information(self.corpus, 'citations')

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)

    def test_keyword_cooccurrence(self):
        g = keyword_cooccurrence(self.corpus, min_weight=2)

        self.assertIsInstance(g, nx.Graph)
        self.assertGreater(g.order(), 0)
        self.assertGreater(g.size(), 0)


if __name__ == '__main__':
    unittest.main()
