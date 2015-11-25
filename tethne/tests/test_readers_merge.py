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

    def test_merge_both_empty(self):
        """
        Testing the functionality of merge when both lists passed are empty
        """

        wos_papers = []
        wos_corpus = Corpus(wos_papers)
        dfr_papers = []
        dfr_corpus = Corpus(dfr_papers)
        expected_len = 0

        self.assertEqual(expected_len,len(merge(wos_corpus,dfr_corpus)))

    def test_merge_one_empty(self):
        """
        Testing the functionality of merge when one of the lists passed is empty
        """

        wos_papers = []
        wos_corpus = Corpus(wos_papers)
        dfr_papers = []
        dfr_paper = Paper()
        dfr_paper['date'] = 1965
        dfr_papers.append(dfr_paper)
        dfr_corpus = Corpus(dfr_papers)
        dfr_papers.append(dfr_paper)
        expected_len = 1

        self.assertEqual(expected_len,len(merge(dfr_corpus,wos_corpus)))
        self.assertEqual(expected_len,len(merge(wos_corpus,dfr_corpus)))


    def test_merge_not_equal(self):
        """
        Testing the functionality of merge by passing two lists with 1 field each and field's values in both are not equal
        """

        wos_papers = []
        wos_paper = Paper()
        wos_paper['date'] = 1999
        wos_papers.append(wos_paper)
        wos_corpus = Corpus(wos_papers)
        dfr_papers = []
        dfr_paper = Paper()
        dfr_paper['date'] = 1965
        dfr_papers.append(dfr_paper)
        dfr_corpus = Corpus(dfr_papers)
        result = merge(dfr_corpus,wos_corpus,['date'])
        expected_len = 2

        self.assertEqual(expected_len,len(result))


    def test_merge_equal(self):
        """
        Testing the functionality of merge by passing two lists with 1 field each and field's values in both are equal
        """
        wos_papers = []
        wos_paper = Paper()
        wos_paper['date'] = 1999

        wos_papers.append(wos_paper)
        wos_corpus = Corpus(wos_papers)
        dfr_papers = []
        dfr_paper = Paper()
        dfr_paper['date'] = 1999
        dfr_papers.append(dfr_paper)
        dfr_corpus = Corpus(dfr_papers)
        result = merge(dfr_corpus,wos_corpus,['date'])
        expected_len = 1

        self.assertEqual(1999,result[0].__getitem__('date'))



if __name__ == '__main__':
    unittest.main()
