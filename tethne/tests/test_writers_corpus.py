import sys
sys.path.append('../tethne')

import unittest
import tempfile
import os
from xml.etree import ElementTree as ET
import networkx as nx
import csv

from tethne import write_documents, write_documents_dtm
from tethne.readers.wos import read

datapath = './tethne/tests/data/wos3.txt'


class WriteDocumentsTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.target = os.path.join(self.temp, 'test')
        self.corpus = read(datapath, index_by='wosid', index_features=['citations', 'authors'])

        self.dpath = self.target + '_docs.txt'
        self.mpath = self.target + '_meta.csv'

    def test_write_documents(self):
        write_documents(self.corpus, self.target, 'citations')

        self.assertTrue(os.path.exists(self.dpath))
        self.assertTrue(os.path.exists(self.mpath))
        self.assertGreater(os.path.getsize(self.dpath), 0)
        self.assertGreater(os.path.getsize(self.mpath), 0)

    def tearDown(self):
        os.remove(self.dpath)
        os.remove(self.mpath)
        os.rmdir(self.temp)


class WriteDocumentsDTMTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.mkdtemp()
        self.target = os.path.join(self.temp, 'test')
        self.corpus = read(datapath, index_by='wosid', index_features=['citations', 'authors'])

        self.multpath = self.target + '-mult.dat'
        self.metapath = self.target + '-meta.dat'
        self.seqpath = self.target + '-seq.dat'
        self.vpath = self.target + '-vocab.dat'

    def test_write_documents_dtm(self):
        write_documents_dtm(self.corpus, self.target, 'citations')

        self.assertTrue(os.path.exists(self.multpath))
        self.assertTrue(os.path.exists(self.metapath))
        self.assertTrue(os.path.exists(self.seqpath))
        self.assertTrue(os.path.exists(self.vpath))
        self.assertGreater(os.path.getsize(self.multpath), 0)
        self.assertGreater(os.path.getsize(self.metapath), 0)
        self.assertGreater(os.path.getsize(self.seqpath), 0)
        self.assertGreater(os.path.getsize(self.vpath), 0)


    def tearDown(self):
        os.remove(self.multpath)
        os.remove(self.metapath)
        os.remove(self.seqpath)
        os.remove(self.vpath)
        os.rmdir(self.temp)


if __name__ == '__main__':
    unittest.main()
