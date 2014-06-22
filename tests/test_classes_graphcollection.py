from settings import *

# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

import unittest

from tethne.readers import wos, dfr
from tethne.classes import DataCollection, GraphCollection
from tethne.networks.authors import coauthors

class TestGraphCollection(unittest.TestCase):
    def setUp(self):
        wosdatapath = '{0}/wos.txt'.format(datapath)
        
        papers = wos.read(wosdatapath)
        self.D = DataCollection(papers)
        self.G = GraphCollection()
        self.D.slice('date')

        for k,v in self.D.get_slices('date', include_papers=True).iteritems():
            self.G[k] = coauthors(v)

    def test_nodes(self):
        """
        should return a list of integers
        """
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'classes.GraphCollection.nodes.png')):
            nodes = self.G.nodes()

        self.assertIsInstance(nodes, list)
        self.assertIsInstance(nodes[0], int)

    def test_index_graph(self):
        """
        index should be as large as set of unique nodes in all graphs
        """

        unodes = set([ n for g in self.G.graphs.values() for n in g.nodes() ])
        self.assertEqual(len(self.G.node_index), len(unodes))

if __name__ == '__main__':
    unittest.main()