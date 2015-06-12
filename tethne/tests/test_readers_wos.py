import sys
sys.path.append('../tethne')

import unittest
from tethne.readers.wos import WoSParser, read
from tethne import Corpus, Paper

datapath = './tethne/tests/data/wos2.txt'


class TestWoSParser(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath)
        self.assertIsInstance(corpus, Corpus)

    def test_read_nocorpus(self):
        papers = read(datapath, corpus=False)
        self.assertIsInstance(papers, list)
        self.assertIsInstance(papers[0], Paper)

    def test_parse(self):
        parser = WoSParser(datapath)
        parser.parse()

        # Check data types for the most common fields.
        derror = "{0} should be {1}, but is {2}"
        for e in parser.data:
            if hasattr(e, 'date'):
                self.assertIsInstance(e.date, int,
                                      derror.format('date', 'int',
                                                    type(e.date)))
            uppererr = "Author names should be uppercase"
            if hasattr(e, 'authors_full'):
                self.assertIsInstance(e.authors_full, list,
                                      derror.format('authors_full', 'list',
                                                    type(e.authors_full)))
                for a in e.authors_full:
                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)
            if hasattr(e, 'authors_init'):
                self.assertIsInstance(e.authors_init, list,
                                      derror.format('authors_init', 'list',
                                                    type(e.authors_init)))
                for a in e.authors_init:
                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)
            if hasattr(e, 'journal'):
                self.assertIsInstance(e.journal, str,
                                      derror.format('journal', 'str',
                                                    type(e.journal)))
            if hasattr(e, 'abstract'):
                self.assertIsInstance(e.abstract, str,
                                      derror.format('abstract', 'str',
                                                    type(e.abstract)))
            if hasattr(e, 'authorKeywords'):
                self.assertIsInstance(e.authorKeywords, list,
                                      derror.format('authorKeywords', 'list',
                                                    type(e.authorKeywords)))
            if hasattr(e, 'keywordsPlus'):
                self.assertIsInstance(e.keywordsPlus, list,
                                      derror.format('keywordsPlus', 'list',
                                                    type(e.keywordsPlus)))
            if hasattr(e, 'doi'):
                self.assertIsInstance(e.doi, str,
                                      derror.format('doi', 'str',
                                                    type(e.doi)))
            if hasattr(e, 'volume'):
                self.assertIsInstance(e.volume, str,
                                      derror.format('volume', 'str',
                                                    type(e.volume)))

            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, str,
                                      derror.format('title', 'str',
                                                    type(e.title)))

        # Check integrity of tag-to-field mapping.
        for tag, attr in parser.tags.iteritems():
            self.assertFalse(hasattr(e, tag),
                             ' '.join(['{0} should map to'.format(tag),
                                       '{0}, but does not.'.format(attr)]))

        # Check number of records.
        N = len(parser.data)
        self.assertEqual(N, 100, 'Expected 100 entries, found {0}.'.format(N))

        self.assertTrue(hasattr(parser.data[0], 'citedReferences'))
        for cr in parser.data[0].citedReferences:
            self.assertTrue(hasattr(cr, 'date'))
            if cr.date:
                self.assertIsInstance(cr.date, int)
            self.assertTrue(hasattr(cr, 'journal'))


if __name__ == '__main__':
    unittest.main()
