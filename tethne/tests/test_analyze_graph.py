import sys
sys.path.append('./')

import unittest
from tethne import coauthors
from tethne.readers.wos import read
from tethne.analyze.graph import global_closeness_centrality

datapath = './tethne/tests/data/wos2.txt'


class TestGlobalCloseness(unittest.TestCase):
    def test_global_closeness(self):
        corpus = read(datapath)
        graph = coauthors(corpus)
        C = global_closeness_centrality(graph)

        self.assertIsInstance(C, dict)
        for n in graph.nodes():
            self.assertIn(n, C)


    def test_global_closeness_node(self):
        corpus = read(datapath)
        graph = coauthors(corpus)
        C = global_closeness_centrality(graph, node=('SEDA', 'B C'))

        self.assertIsInstance(C, float)
        self.assertGreater(C, 0)


if __name__ == '__main__':
    unittest.main()