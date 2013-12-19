import tethne.writers as wr
import unittest
import networkx as nx
import os

class TestNoneGraph(unittest.TestCase):
    """Test case for graphs with no verticies and no edges"""

    def setUp(self):
        #create None graph
        self.G = nx.Graph()
        self.path = "./testout/G_None"

    def test_sif(self):
        #verify files are written
        wr.graph.to_sif(self.G, self.path)
        self.assertTrue(os.path.isfile(self.path + ".sif"))

        #and they are empty
        if os.path.isfile(self.path + ".sif"):
            G_contents = open(self.path + ".sif",
                              "r").read().splitlines()
            self.assertIs(len(G_contents),0)

    def tearDown(self):
        #remove output files from writer testing
        try:
            os.remove("./testout/G_None.sif")
        except OSError:
            pass

class TestEmptyGraph(unittest.TestCase):
    """Test case for graphs with verticies but no edges"""

    def setUp(self):
        #create Empty graph on n verticies
        self.path = "./testout/G_Empty"
        self.n = 5
        node_list = range(self.n)
        self.G = nx.Graph()
        self.G.add_nodes_from(node_list)

    def test_sif(self):
        #verify files are written
        wr.graph.to_sif(self.G, self.path)
        self.assertTrue(os.path.isfile(self.path + ".sif"))

        #and has a line for each node
        if os.path.isfile(self.path + ".sif"):
            G_contents = open(self.path + ".sif",
                              "r").read().splitlines()
            self.assertIs(len(G_contents), self.n)

    def tearDown(self):
        #remove output files from writer testing
        try:
            os.remove(self.path + ".sif")
        except OSError:
            pass


class TestNAttribEmptyGraph(unittest.TestCase):
    """
    Test case for graphs with verticies with attributes but no edges
    """

    def setUp(self):
        #create Empty graph with node attributes on n verticies
        self.path = "./testout/G_NAttribEmpty"
        self.n = 5
        self.attrib_dict = {'test_att1':1, 'test_att2':2}

        node_list = []
        for i in xrange(self.n):
            node_list.append((i, self.attrib_dict))

        self.G = nx.Graph()
        self.G.add_nodes_from(node_list)


    def test_sif(self):
        #verify files are written
        wr.graph.to_sif(self.G, self.path)
        self.assertTrue(os.path.isfile(self.path + ".sif"))
        for key in self.attrib_dict.iterkeys():
            self.assertTrue(os.path.isfile(self.path + "_" + key + 
                                           ".noa"))

        #and have appropriate contents
        if os.path.isfile(self.path + ".sif"):
            G_contents = open(self.path + ".sif", 
                              "r").read().splitlines()
            self.assertIs(len(G_contents), self.n)

        for key in self.attrib_dict.iterkeys():
            if os.path.isfile(self.path + key + ".noa"):
                noa_contents = open(self.path + "_" + key + ".noa",
                                "r").read().splitlines()
                self.assertIs(len(noa_contents), self.n)

    def tearDown(self):
        #remove output files from writer testing
        try:
            os.remove(self.path + ".sif")
            for key in self.attrib_dict.iterkeys():
                os.remove(self.path + "_" +  key + ".noa")
        except OSError:
            pass

if __name__ == '__main__':
    unittest.main()
