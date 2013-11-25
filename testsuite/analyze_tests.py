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
                        g.add_edge(i, j)
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

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
