import sys
sys.path.append('../tethne')

import unittest
import tempfile
import os
from xml.etree import ElementTree as ET
import networkx as nx
import csv

from tethne import write_graphml, write_csv
from tethne.writers.graph import to_sif
from tethne.readers.wos import read
from tethne.networks.authors import coauthors

datapath = './tethne/tests/data/wos2.txt'
testdatapath = '/Users/diging_yogi/tethne/tethne/tests/data/wos2.txt'



class GraphMLTest(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)
        self.graph = coauthors(self.corpus)
        f, self.temp = tempfile.mkstemp(suffix='.graphml')

    def test_write_graphml(self):
        write_graphml(self.graph, self.temp)
        self.assertGreater(os.path.getsize(self.temp), 0)

        try:    # Should be well-formed XML.
            ET.parse(self.temp)
        except Exception as E:
            self.fail(E.message)

        # Can read with networkx GraphML reader.
        try:
            rgraph = nx.read_graphml(self.temp)
        except Exception as E:
            self.fail(E.message)
        self.assertTrue(nx.is_isomorphic(self.graph, rgraph))

    def tearDown(self):
        try:
            os.remove(self.temp)
        except WindowsError:
            pass

class CSVTest(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)
        self.graph = coauthors(self.corpus)
        self.temp = tempfile.mkdtemp()
        self.prefix = os.path.join(self.temp, 'textprefix')

    def test_write_csv(self):
        write_csv(self.graph, self.prefix)

        self.assertGreater(os.path.getsize(self.prefix + '_nodes.csv'), 0)
        self.assertGreater(os.path.getsize(self.prefix + '_edges.csv'), 0)

        try:
            with open(self.prefix + '_nodes.csv', 'r') as f:
                reader = csv.reader(f)
                [ line for line in reader ]
        except Exception as E:
            self.fail(E.message)

        try:
            with open(self.prefix + '_edges.csv', 'r') as f:
                reader = csv.reader(f)
                [ line for line in reader ]
        except Exception as E:
            self.fail(E.message)

    def tearDown(self):
        try:
            os.remove(self.prefix + '_nodes.csv')
            os.remove(self.prefix + '_edges.csv')
            os.rmdir(self.temp)
        except WindowsError:
            pass


class TestToSif(unittest.TestCase):

    #testing the functionality of to_sif method
    def testBasic(self):
        self.corpus = read(datapath)
        self.graph = coauthors(self.corpus)
        #self.temp = tempfile.mkstemp()
        #self.prefix = os.path.join(self.temp,'.toSif')
        f, self.temp = tempfile.mkstemp(suffix='.toSif')


        to_sif(self.graph,self.temp)

        self.assertEqual(os.path.getsize(self.temp), 0)

    #testing the functionality when the graph is multigraph
    def testMultiGraph(self):
        testGraphMulti = nx.MultiGraph()
        testGraphMulti.add_edges_from([(1,2),(2,1),(1,3),(2,4,{'color':'blue'}),(3,5)])
        f, self.temp = tempfile.mkstemp(suffix='.toSif')

        to_sif(testGraphMulti,self.temp)
        self.assertEqual(os.path.getsize(self.temp),0)

    def testGraphZeroEdges(self):
        testGraphNoEdges = nx.Graph()
        testGraphNoEdges.add_nodes_from([1,3,5,7])
        f, self.temp = tempfile.mkstemp(suffix='.toSif')

        to_sif(testGraphNoEdges,self.temp)
        self.assertEqual(os.path.getsize(self.temp),0)







if __name__ == '__main__':
    unittest.main()
