import sys
sys.path.append('../tethne')

import unittest
from tethne.readers.dfr import read, ngrams
from tethne import Corpus, Paper, FeatureSet

datapath = './tethne/tests/data/dfr'
datapath_float_weights = './tethne/tests/data/dfr_float_weights'

class TestDFRReader(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath)

        self.assertIsInstance(corpus, Corpus)

        for e in corpus.papers:
            if hasattr(e, 'date'):
                self.assertIsInstance(e.date, int)

            uppererr = "Author names should be uppercase"
            if hasattr(e, 'authors_full'):
                self.assertIsInstance(e.authors_full, list)
                for a in e.authors_full:
                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)

            if hasattr(e, 'authors_init'):
                self.assertIsInstance(e.authors_init, list)
                for a in e.authors_init:
                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)

            if hasattr(e, 'journal'):
                self.assertIsInstance(e.journal, str)

            if hasattr(e, 'abstract'):
                self.assertIsInstance(e.abstract, str)

            if hasattr(e, 'authorKeywords'):
                self.assertIsInstance(e.authorKeywords, list)

            if hasattr(e, 'keywordsPlus'):
                self.assertIsInstance(e.keywordsPlus, list)
            if hasattr(e, 'doi'):
                self.assertIsInstance(e.doi, str)
            if hasattr(e, 'volume'):
                self.assertIsInstance(e.volume, str)

            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, str)

        self.assertIn('wordcounts', corpus.features)

        self.assertGreaterEqual(len(corpus),
                                len(corpus.features['wordcounts']))

    def test_transform(self):
        corpus = read(datapath)
        wordcounts = corpus.features['wordcounts']
        def filter(f, v, c, dc):
            if f == 'the':
                return 0
            return v

        # filter() should remove a single token.
        self.assertEqual(len(wordcounts.index) - 1,
                         len(wordcounts.transform(filter).index))


class TestNGrams(unittest.TestCase):
    def test_ngrams(self):
        grams = ngrams(datapath, 'wordcounts')

        self.assertIsInstance(grams, FeatureSet)
        self.assertEqual(len(grams), 398)
        self.assertEqual(len(grams.index), 105156)

    def test_float_weights(self):
        """
        Some DfR features have floating-point weights, rather than ints.
        """
        grams = ngrams(datapath_float_weights, 'keyterms')

        self.assertIsInstance(grams, FeatureSet)
        self.assertEqual(len(grams), 2)
        self.assertEqual(len(grams.index), 43)


class TestCitationFile(unittest.TestCase):
    def test_citations_file(self):
        datapath2 = './tethne/tests/data/dfr2'
        self.assertIsInstance(read(datapath2), Corpus)


if __name__ == '__main__':
    unittest.main()
