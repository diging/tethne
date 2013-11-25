import unittest
import tethne.data as dt
import networkx as nx
import os
import os.path
import numpy as np

class testGraphCollection(unittest.TestCase):
    """
    Tests methods for tethne.data.GraphCollection class.
    """
    def setUp(self):
        self.collection = dt.GraphCollection()
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

    def test_analyze(self):
        """
        Test of tethne.data.GraphCollection.analyze method.
        """
        
        # Properly-formed request, with kwarg.
        results = self.collection.analyze('betweenness_centrality', k=None)

        # Correct number of nodes in results.
        self.assertEqual(len(results.keys()), self.N)
        
        # Correct number of graph indices in result for first node.
        self.assertEqual(len(results.values()[0].keys()), self.I)
        
        # Poorly-formed request, where no such name exists.
        with self.assertRaises(ValueError):
            self.collection.analyze('asdf')
        
        # Poorly-formed request, where name is not a function.
        with self.assertRaises(ValueError):
            self.collection.analyze('connected')

    def test_connected(self):
        """
        Test of tethne.data.GraphCollection.connected method.
        """
    
        # Properly-formed request.
        results = self.collection.connected('is_connected')
    
        # Correct number of graph indices in result.
        self.assertEqual(len(results.keys()), self.I )

        # Poorly-formed request, where no such name exists.
        with self.assertRaises(ValueError):
            self.collection.connected('asdf')

    def test_setitem(self):
        """
        Test of tethne.data.GraphCollection.__setitem__ .
        """
        
        # If value is not a tuple, then it must be a Graph.
        with self.assertRaises(ValueError):
            self.collection[6] = 'asdf'
    
        # If value is a tuple, then value[0] must be a Graph.
        with self.assertRaises(ValueError):
            self.collection[6] = ('asdf', 'asdf')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
