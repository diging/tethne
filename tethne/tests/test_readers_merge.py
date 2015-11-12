import sys
sys.path.append('../tethne')

import unittest
from tethne.readers import dfr, wos, merge
from tethne import Corpus, Paper, FeatureSet

dfr_datapath = './tethne/tests/data/dfr'
wos_datapath = './tethne/tests/data/wos2.txt'


class TestMerge(unittest.TestCase):
    def setUp(self):
        self.dfr_corpus = dfr.read(dfr_datapath)
        self.wos_corpus = wos.read(wos_datapath)

    def test_merge(self):
        combined = merge(self.dfr_corpus, self.wos_corpus)
        self.assertEqual(len(combined), 472)

        old_features = list(set(self.dfr_corpus.features.keys()) | \
                            set(self.wos_corpus.features.keys()))
        self.assertListEqual(combined.features.keys(), old_features)

    def test_merge_comparator(self):
        """
        Instead of passing a list of fields to compare, we can pass a callable
        object that returns bool.
        """

        comparator = lambda p1, p2: p1.ayjid == p2.ayjid
        combined = merge(self.dfr_corpus, self.wos_corpus, match_by=comparator)
        self.assertEqual(len(combined), 472)


if __name__ == '__main__':
    unittest.main()
