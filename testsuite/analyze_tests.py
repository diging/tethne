import unittest
import tethne.data as ds
import tethne.analyze.collection as co
import networkx as nx
import numpy as np

class TestCollection(unittest.TestCase):
    """
    Tests methods for tethne.analyze.collection module.
    """
    def setUp(self):
        self.collection = ds.GraphCollection()
        self.N = 100    # Number of nodes
        self.I = 5  # Number of graph indices.
        for graph_index in xrange(self.I):
            d = np.random.random((self.N, self.N))
            g = nx.Graph()
            for i in xrange(self.N):
                for j in xrange(i+1, self.N):
                    if d[i, j] > 0.7:
                        g.add_edge(i, j, index=graph_index)
                g.node[i]['graph_index'] = graph_index
            self.collection.graphs[graph_index] = g
        self.test_graph = nx.Graph()

    def test_algorithm(self):
        """
        Test of tethne.analyze.collection.algorithm method.
        """

        # Properly-formed request, with kwarg.
        results = co.algorithm(self.collection, 'betweenness_centrality', k=None)

        # Correct number of nodes in results.
        self.assertEqual(len(results.keys()), self.N)

        # Correct number of graph indices in result for first node.
        self.assertEqual(len(results.values()[0].keys()), self.I)

        # Poorly-formed request, where no such name exists.
        with self.assertRaises(ValueError):
            co.algorithm(self.collection, 'asdf')

        # Poorly-formed request, where name is not a function.
        with self.assertRaises(ValueError):
            co.algorithm(self.collection, 'connected')

    def test_connected(self):
        """
        Test of tethne.analyze.collection.connected method.
        """

        # Properly-formed request.
        results = co.connected(self.collection, 'is_connected')

        # Correct number of graph indices in result.
        self.assertEqual(len(results.keys()), self.I )

        # Poorly-formed request, where no such name exists.
        with self.assertRaises(ValueError):
            co.connected(self.collection, 'asdf')

    def test_edge_history(self):
        """
        Tests for tethne.analyze.collection.edge_history().
        """

        # Value of edge attribute graph_index should match Graph key.
        graph_indices = co.edge_history(self.collection, 0, 1, 'graph_index')
        self.assertEqual(graph_indices.keys(), graph_indices.values())

    def test_node_history(self):
        """
        Tests for tethne.analyze.collection.node_history().
        """

        # Value of node attribute graph_index should match Graph key.
        graph_indices = co.node_history(self.collection, 0, 'graph_index')
        self.assertEqual(graph_indices.keys(), graph_indices.values())

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
