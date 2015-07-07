import sys
sys.path.append('../tethne')

import unittest
import tempfile
import os
from xml.etree import ElementTree as ET
import networkx as nx
import csv

from tethne.model.corpus.mallet import LDAModel
from tethne.readers.wos import read
from tethne import FeatureSet

datapath = './tethne/tests/data/wos3.txt'

class TestLDAModel(unittest.TestCase):
    def test_ldamodel(self):
        corpus = read(datapath, index_by='wosid')
        model = LDAModel(corpus, featureset_name='citations')
        model.fit(Z=20, max_iter=500)

        dates, rep = model.topic_over_time(1)
        self.assertGreater(sum(rep), 0)
        self.assertEqual(len(dates), len(rep))
        
        self.assertIsInstance(model.phi, FeatureSet)
        self.assertIsInstance(model.theta, FeatureSet)        


if __name__ == '__main__':
    unittest.main()