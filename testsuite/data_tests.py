import unittest
import tethne.data as ds
import networkx as nx
import numpy as np
import pickle as pk
import tethne.networks as nt
import tethne.readers as rd

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
        self.correct_filename = "../testsuite/testout/graphcollections1.txt"
        self.wrong_filename = "../testsuite/asdad123e2e1aphcollections.txt"
        self.save_edges = []
        self.save_nodes = []
        self.load_edges = []
        self.load_nodes = []
        
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
        
        C = ds.GraphCollection()
        C[0] = nx.Graph()
        C[0].add_edge(0,1)
        C[0].add_edge(2,1)
        C[0].add_edge(2,0)
        C.save(self.correct_filename)

        self.assertIsInstance(C,type(C), msg="yes it is a object")
        
        self.g1 = ds.GraphCollection()
        self.g2 = ds.GraphCollection()
       

        filepath = "../testsuite/testin/coauthors.txt"
        wos_list = rd.wos.parse(filepath)
        meta_list= rd.wos.convert(wos_list)


        coauthors = nt.authors.coauthors(meta_list, 'date','jtitle','ayjid')
        author_coup = nt.papers.author_coupling(meta_list, 1, 'ayjid', 'atitle')


        self.g1.__setitem__('ayjid',coauthors)
        self.g2.__setitem__('ayjid',author_coup)


        self.save_nodes = self.g1.nodes()
        self.save_edges = self.g1.edges()

        self.g1.save\
            ("../testsuite/testout/graphcollections.txt")

        obtained = set(self.g1.nodes())
        expected = set (['TUERHONG G', 'CHEN T', 'BARRENECHEA E', 'KANG P', \
                         'GALAR M', 'ZHANG B', 'CHO S', 'CHEN F', 'YE G', \
                         'MAALEJ W', 'FERNANDEZ A', 'HUANG J', 'PAGANO D', \
                         'HERMAN G', 'KIM S', 'VATALIS K', 'WANG Y', \
                         'HERRERA F', 'MODIS K'])
                
        self.assertSetEqual(obtained, expected, "nodes not as expected")
    

    
    

    def test_load(self):
        """
        Test of tethne.data.GraphCollection.load .
        """
        self.g3 = ds.GraphCollection()
       
        # Check for IOError.
        
#        with self.assertRaises('IOError',self.collection.load(self.wrong_filename)):
#            D = dt.GraphCollection()
#            D.load(self.filename)

        self.g3.load("../testsuite/testout/graphcollections.txt")
        
        self.load_nodes = set(self.g3.nodes())
        self.load_edges = self.g3.edges()
        
        obtained = set(self.g3.nodes())
        expected = set (['TUERHONG G', 'CHEN T', 'BARRENECHEA E', 'KANG P', \
                         'GALAR M', 'ZHANG B', 'CHO S', 'CHEN F', 'YE G', \
                         'MAALEJ W', 'FERNANDEZ A', 'HUANG J', 'PAGANO D', \
                         'HERMAN G', 'KIM S', 'VATALIS K', 'WANG Y', \
                         'HERRERA F', 'MODIS K'])
    
        self.assertSetEqual \
            (obtained, self.load_nodes, "nodes not as expected")
            
            
    
    def tearDown(self):
        pass




if __name__ == '__main__':
    unittest.main()
