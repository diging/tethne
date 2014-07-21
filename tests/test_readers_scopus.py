from settings import *

import unittest

from tethne.readers import scopus
from tethne.classes import Paper, Corpus

class TestScopusReader(unittest.TestCase):
    def setUp(self):
        self.scopus_data = '{0}/scopus/scopus.csv'.format(datapath)
        self.scopus_data_dir = '{0}/scopus'.format(datapath)

    def test_handle_authors(self):
        """
        _handle_authors() should return a tuple containing a aulast and init
        lists.
        """

        authordata = 'Shannonhouse J.L., Fong L.A., Clossen B.L.'
        expected = (['SHANNONHOUSE', 'FONG', 'CLOSSEN'],['JL', 'LA', 'BL'])
        observed = scopus._handle_authors(authordata)
        self.assertEqual(expected, observed)
    
        authordata = 'Aguirre J., Buldu J.M., Stich M., Manrubia S.C., '
        expected = (['AGUIRRE', 'BULDU', 'STICH', 'MANRUBIA'], ['J', 'JM', 'M', 'SC'])
        observed = scopus._handle_authors(authordata)
        self.assertEqual(expected, observed)

    def test_handle_insitutions(self):
        affiliationsdata = 'Shannonhouse, J.L., Texas A andM Institute for Neuroscience, Texas A andM University, College Station, TX 77843, United States; Fong, L.A., Department of Nutrition and Food Science, Texas A andM University, College Station, TX 77843, United States;'
        expected = {
            'SHANNONHOUSE JL': ['TEXAS A ANDM INSTITUTE FOR NEUROSCIENCE, TEXAS A ANDM UNIVERSITY, UNITED STATES'],
             'FONG LA': ['DEPARTMENT OF NUTRITION AND FOOD SCIENCE, TEXAS A ANDM UNIVERSITY, UNITED STATES']
             }
    
        observed = scopus._handle_affiliations(affiliationsdata)
        self.assertEqual(expected, observed)

    def test_read(self):
        papers = scopus.read(self.scopus_data)
        self.assertEqual(len(papers), 20)
        self.assertEqual(len(papers[0]['citations']), 54)
        self.assertGreater(len(papers[0]['accession']), 0)
        self.assertIsInstance(papers[0], Paper)

    def test_from_dir(self):
        papers = scopus.from_dir(self.scopus_data_dir)
        self.assertEqual(len(papers), 20)
        self.assertEqual(len(papers[0]['citations']), 54)
        self.assertGreater(len(papers[0]['accession']), 0)
        self.assertIsInstance(papers[0], Paper)

    def test_read_corpus(self):
        corpus = scopus.read_corpus(self.scopus_data)
        self.assertEqual(len(corpus.all_papers()), 20)
        self.assertIsInstance(corpus, Corpus)

    def test_corpus_from_dir(self):
        corpus = scopus.corpus_from_dir(self.scopus_data_dir)
        self.assertEqual(len(corpus.all_papers()), 20)
        self.assertIsInstance(corpus, Corpus)

    def test_abstract_to_features(self):
        scopus_data = '{0}/scopus/scopus.csv'.format(datapath)
        corpus = scopus.read_corpus(scopus_data)
        corpus.abstract_to_features()
        self.assertGreater(len(corpus.features['abstractTerms']['index']), 0)


if __name__ == '__main__':
    unittest.main()