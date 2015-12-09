import unittest
import networkx as nx

import sys
sys.path.append('../tethne')


datapath = './tethne/tests/data/wos2.txt'

from tethne.networks import helpers
from tethne.readers.wos import read
from collections import Counter



class MyTestCase(unittest.TestCase):


    def test_simplify_multigraph(self):
        """
        PURPOSE :To Test the simplify_Multigraph functionality.

        DESCRIPTION : simplify_graph takes as input a multigraph i.e
        a graph having parallel edges in between 2 vertices/nodes
        and converts it to a simple graph i.e. with only one edge
        in between two nodes. And the weight of the new edge is equal
        to the number of edges that were collapsed.

        TESTED FOR : 1) Collapsed edges between vertices.
                     2) Weight of the new edges

        TEST DATA : any Multigraph.
        """
        test_graph = nx.MultiGraph()
        test_graph.add_weighted_edges_from([(1,2,8.0), (1,2,100.0), (2,3,97.0),(1,2,98.0),(3,4,67.0)])
        simplified_graph = helpers.simplify_multigraph(test_graph)
        self.assertIsInstance(simplified_graph, nx.Graph)
        self.assertEqual(simplified_graph.number_of_nodes(), 4)
        self.assertEqual(simplified_graph.number_of_edges(), 3)
        self.assertEqual(simplified_graph[1][2]['weight'], 3)

if __name__ == '__main__':
    unittest.main()
