import unittest
import networkx as nx
import os
import os.path
import tethne.writers as wr

class TestNoneGraph(unittest.TestCase):
    """Test case for graphs with no verticies and no edges"""

    def setUp(self):
        #create None graph
        G = nx.Graph()
        D = nx.DiGraph()

    def writers(self):
        #verify files are written
        wr.to_sif(G,"./testout","G_None")
        self.assertTrue(os.path.isFile("./testout/G_None.sif"))

        wr.to_sif(D,"./testout","D_None")
        self.assertTrue(os.path.isFile("./testout/D_None.sif"))

        #and they are empty
        if os.path.isFile("./testout/G_None.sif"):
            G_contents = open("./testout/G_None.sif","r").read()
            self.assertIs(len(G_contents),0)

        if os.path.isFile("./testout/D_None.sif"):
            D_contents = open("./testout/D_None.sif","r").read()
            self.assertIs(len(D_contents),0)

    def tearDown(self):
        #remove output files from writer testing
        print "tomorrow!"

if __name__ == '__main__':
    unittest.main()
