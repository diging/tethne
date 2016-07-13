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

DTM_PATH = os.environ.get('DTM_PATH', None)


from tethne.model.corpus.dtm import _to_dtm_input


def _cleanUp(basepath):
    for fname in ['meta', 'mult', 'seq', 'vocab']:
        try:
            os.remove(basepath + '-%s.dat' % fname)
        except OSError:
            pass


class TestToDTMInput(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.basepath = os.path.join(sandbox, 'dtm_test')
        self.corpus.index_feature('abstract', word_tokenize)
        _cleanUp(self.basepath)

    def test_to_dtm_input(self):
        _to_dtm_input(self.corpus, self.basepath, 'abstract')

        for fname in ['meta', 'mult', 'seq', 'vocab']:
            self.assertTrue(os.path.exists(self.basepath + '-%s.dat' % fname))

    def tearDown(self):
        _cleanUp(self.basepath)


class TestDTMModel(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.basepath = os.path.join(sandbox, 'dtm_test')
        self.corpus.index_feature('abstract', word_tokenize)
        _cleanUp(self.basepath)

    def test_init(self):
        # We have to depend on the user compiling DTM themselves at this point,
        #  so until we add a DTM build step to Travis this should only run if
        #  the path to DTM binary is set.
        if not DTM_PATH:
            return
        self.model = DTMModel(self.corpus,
                              featureset_name='abstract',
                              dtm_path=DTM_PATH)

    def test_fit(self):
        # We have to depend on the user compiling DTM themselves at this point,
        #  so until we add a DTM build step to Travis this should only run if
        #  the path to DTM binary is set.
        if not DTM_PATH:
            return

        self.model = DTMModel(self.corpus,
                              featureset_name='abstract',
                              dtm_path=DTM_PATH)
        self.model.fit(Z=5)

        self.assertEqual(self.model.e_theta.shape, (5, 220))
        self.assertEqual(self.model.phi.shape, (5, 7429, 12))

        keys, values =  self.model.topic_evolution(0)
        self.assertEqual(keys, self.corpus.indices['date'].keys())

        self.model.list_topic(3, 0)
        self.model.list_topic_diachronic(3)
        self.model.list_topics(3)

    def tearDown(self):
        _cleanUp(self.basepath)



if __name__ == '__main__':
    unittest.main()
