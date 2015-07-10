import sys
sys.path.append('../tethne')

import unittest
from tethne.readers.dfr import read, ngrams
from tethne import Corpus, Paper, FeatureSet

datapath = './tethne/tests/data/dfr'


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
        
class TestNGrams(unittest.TestCase):
    def test_ngrams(self):
        grams = ngrams(datapath, 'wordcounts')
        
        self.assertIsInstance(grams, FeatureSet)
        self.assertEqual(len(grams), 398)
        


if __name__ == '__main__':
    unittest.main()
