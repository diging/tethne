import unittest
import tethne.data as ds
import networkx as nx
import numpy as np
import pickle as pk

class TestPaper(unittest.TestCase):
    """
    Tests for tethne.data.Paper class.
    
    Notes
    -----
    TODO: Implement this.
    """
    
    def setUp(self):
        pass
    
    def test_setitem(self):
        """
        Test of tethne.data.Paper.__setitem__ .
        """    
        pass
    
    def test_getitem(self):
        """
        Test of tethne.data.Paper.__getitem__ .
        """
        pass
    
    def tearDown(self):
        pass

class TestGraphCollection(unittest.TestCase):
    """
    Tests methods for tethne.data.GraphCollection class.
    """
    
    
    def setUp(self):
        self.collection = ds.GraphCollection()
        self.filename = "../testsuite/testout/graphcollections.txt"
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

        pass

    def test_save(self):
        """
        Test of tethne.data.GraphCollection.save .
        """
        # Check for Pickling Error
        with self.assertRaises('PicklingError'):
            self.save1 = self.collection.save(self.filename)
            self.save2 = self.collection.save(self.filename)
            

        # Check for IOError.
        with self.assertRaises(IOError):
            self.save1 = self.collection.save(self.filename)
            self.save2 = self.collection.save(self.filename)
            
    

    def test_load(self):
        """
        Test of tethne.data.GraphCollection.load .
        """
    
        # Check for UnPickling Error.
        with  self.assertRaises('UnPicklingError'):
            self.load  = self.collection.load(self.filename)
       
        # Check for IOError
        with self.assertRaises(IOError):
            self.load  = self.collection.load(self.filename)
           
               
    
                    

    def tearDown(self):
        pass




if __name__ == '__main__':
    unittest.main()
