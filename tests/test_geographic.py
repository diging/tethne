from settings import *

import unittest
from tethne.readers import wos
from tethne.networks import authors

import os
import networkx

class TestCoauthorsGeo(unittest.TestCase):
    def setUp(self):
        self.path = datapath + '/wos.txt'
        self.corpus = wos.read_corpus(self.path)
    
    def test_coauthors_geo(self):
        graph = authors.coauthors(
                    self.corpus.all_papers(), threshold=1, geocode=True )
        nodes = graph.nodes(data=True)
        self.assertGreater(len(nodes), 0)
        self.assertIn('longitude', nodes[0][1])
        self.assertIn('latitude', nodes[0][1])
        self.assertIn('precision', nodes[0][1])
        self.assertIsInstance(nodes[0][1]['latitude'], float)
        self.assertIsInstance(nodes[0][1]['longitude'], float)
        self.assertIsInstance(nodes[0][1]['precision'], str)


if __name__ == '__main__':
    unittest.main()