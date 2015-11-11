import sys
sys.path.append('./')

import unittest
from tethne.readers.wos import read
from tethne import Corpus, Paper, GraphCollection
from tethne.networks import coauthors
from tethne.utilities import _iterable
from tethne.writers.collection import to_dxgmml

import tempfile
import os


datapath = './tethne/tests/data/wos.txt'


class TestToDXGMML(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)
        self.G = GraphCollection(self.corpus, coauthors)
        f, self.temp = tempfile.mkstemp(suffix='.xgmml')

    def test_write_dxgmml(self):
        try:
            to_dxgmml(self.G, self.temp)
        except Exception as E:
            self.fail(E.message)




if __name__ == '__main__':
    unittest.main()
