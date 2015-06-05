import sys
sys.path.append('./')

import unittest
from tethne.readers.wos import read
from tethne import Corpus, Paper
from tethne.utilities import _iterable

datapath = './tethne/tests/data/wos.txt'


class TestCorpus(unittest.TestCase):
    def setUp(self):
        self.papers = read(datapath, corpus=False)

    def test_init(self):
        """
        Check for clean initialization.
        """

        try:
            corpus = Corpus(self.papers, index_by='wosid')
            corpus.__init__(self.papers, index_by='wosid')
        except Exception as E:
            failure_msg = ' '.join(['Initialization failed with exception',
                                    '{0}: {1}'.format(E.__class__.__name__,
                                                      E.message)])
            self.fail(failure_msg)

    def test_indexing(self):
        """
        Check for successful indexing.
        """

        index_fields = ['date', 'journal', 'authors']
        corpus = Corpus(self.papers, index_by='wosid')

        for field in index_fields:
            corpus.index(field)
            self.assertIn(field, corpus.indices,
                          '{0} not indexed.'.format(field))

            expected = len(set([o for p in corpus.papers
                                for o in _iterable(getattr(p, field))]))
            self.assertEqual(len(corpus.indices[field]), expected,
                             'Index for {0} is the wrong size.'.format(field))

    def test_slice(self):
        corpus = Corpus(self.papers, index_by='wosid')
        for papers in corpus.slice():
            self.assertIsInstance(papers, list)
            self.assertIsInstance(papers[0], Paper)

    def test_slice_sliding(self):
        corpus = Corpus(self.papers, index_by='wosid')
        allpapers = [papers for papers in corpus.slice(window_size=2)]

        self.assertEqual(len(allpapers[0]), 10)

    def test_slice_larger(self):
        corpus = Corpus(self.papers, index_by='wosid')
        allpapers = [papers for papers in corpus.slice(window_size=2,
                                                       step_size=2)]

        self.assertEqual(len(allpapers[0]), 10)

    def test_distribution(self):
        corpus = Corpus(self.papers, index_by='wosid')
        values = corpus.distribution()

        self.assertListEqual(values, [5, 5])

    def test_feature_distribution(self):
        corpus = Corpus(self.papers, index_by='wosid')
        values = corpus.feature_distribution('authors', ('ZENG', 'EDDY Y'))

        self.assertListEqual(values, [0, 1])


if __name__ == '__main__':
    unittest.main()
