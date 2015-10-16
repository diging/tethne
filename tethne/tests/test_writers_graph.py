import sys
sys.path.append('../tethne')

import unittest
import tempfile
import os
from xml.etree import ElementTree as ET
import networkx as nx
import csv

from tethne import write_graphml, write_csv
from tethne.readers.wos import read
from tethne.networks.authors import coauthors

datapath = './tethne/tests/data/wos2.txt'

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



if __name__ == '__main__':
    unittest.main()
