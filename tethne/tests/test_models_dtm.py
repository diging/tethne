import sys
sys.path.append('../tethne')

import unittest
import tempfile
import os
from xml.etree import ElementTree as ET
import networkx as nx
import csv


from tethne.readers.wos import read
from tethne import FeatureSet, tokenize
from tethne.networks import topics
from tethne.model.corpus.dtm import DTMModel
from nltk.tokenize import word_tokenize

datapath = './tethne/tests/data/wos3.txt'
sandbox = './tethne/tests/sandbox'

import logging
logger = logging.getLogger('dtm')
logger.setLevel('DEBUG')


from tethne.model.corpus.dtm import _to_dtm_input


class TestToDTMInput(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.basepath = os.path.join(sandbox, 'dtm_test')
        self.corpus.index_feature('abstract', word_tokenize)
        for fname in ['meta', 'mult', 'seq', 'vocab']:
            try:
                os.remove(self.basepath + '-%s.dat' % fname)
            except OSError:
                pass

    def test_to_dtm_input(self):
        _to_dtm_input(self.corpus, self.basepath, 'abstract')

        for fname in ['meta', 'mult', 'seq', 'vocab']:
            self.assertTrue(os.path.exists(self.basepath + '-%s.dat' % fname))

    def tearDown(self):
        for fname in ['meta', 'mult', 'seq', 'vocab']:
            os.remove(self.basepath + '-%s.dat' % fname)


class TestDTMModel(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.basepath = os.path.join(sandbox, 'dtm_test')
        self.corpus.index_feature('abstract', word_tokenize)
        for fname in ['meta', 'mult', 'seq', 'vocab']:
            try:
                os.remove(self.basepath + '-%s.dat' % fname)
            except OSError:
                pass

    def test_init(self):
        self.model = DTMModel(self.corpus, featureset_name='abstract')

    def test_fit(self):
        self.model = DTMModel(self.corpus, featureset_name='abstract')
        self.model.fit(Z=20)

# class TestLDAModel(unittest.TestCase):
#     def setUp(self):
#         from tethne.model.corpus.dtm import DTMModel
#         corpus = read(datapath, index_by='wosid')
#         corpus.index_feature('abstract', tokenize, structured=True)
#         self.model = LDAModel(corpus, featureset_name='abstract')
#         self.model.fit(Z=20, max_iter=500)
#
#     def test_ldamodel(self):
#         dates, rep = self.model.topic_over_time(1)
#         self.assertGreater(sum(rep), 0)
#         self.assertEqual(len(dates), len(rep))
#
#         self.assertIsInstance(self.model.phi, FeatureSet)
#         self.assertIsInstance(self.model.theta, FeatureSet)
#
#         self.assertIsInstance(self.model.list_topics(), list)
#         self.assertGreater(len(self.model.list_topics()), 0)
#         self.assertIsInstance(self.model.list_topic(0), list)
#         self.assertGreater(len(self.model.list_topic(0)), 0)


if __name__ == '__main__':
    unittest.main()
