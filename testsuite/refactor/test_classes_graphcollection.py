# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
cg_path = './callgraphs/'

import unittest

import sys
sys.path.append('../../')

from tethne.readers import wos, dfr
from tethne.classes import DataCollection, GraphCollection

from tethne.networks.authors import coauthors

import logging
logging.basicConfig()
logger = logging.getLogger('tethne.classes.graphcollection')
logger.setLevel('ERROR')
logger = logging.getLogger('tethne.classes.datacollection')
logger.setLevel('ERROR')

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
    datapath = './data'
    unittest.main()