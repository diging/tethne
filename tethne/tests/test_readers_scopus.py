import sys
sys.path.append('../tethne')

import unittest

from tethne.readers import scopus
from tethne import Corpus, Paper, Feature, FeatureSet


scopus_datapath = './tethne/tests/data/scopus.csv'



class MyTestCase(unittest.TestCase):
    def test_reader(self):
        corpus = scopus.read(scopus_datapath)
        self.assertIsInstance(corpus, Corpus)


if __name__ == '__main__':
    unittest.main()
