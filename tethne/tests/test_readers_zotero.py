import sys
sys.path.append('../tethne')

import re

import unittest
from tethne.readers.zotero import read, ZoteroParser, _infer_spaces
from tethne import Corpus, Paper, StructuredFeatureSet

datapath = './tethne/tests/data/zotero'
datapath2 = './tethne/tests/data/zotero2'
datapath3 = './tethne/tests/data/zotero_withfiles'


class TestInferSpaces(unittest.TestCase):
    def test_infer(self):
        s = "Thisisastringwithnospaces."
        self.assertEqual(_infer_spaces(s), 'this is a string with no spaces .')


class TestZoteroParserWithFiles(unittest.TestCase):
    """
    When Tethne reads a Zotero collection, it should attempt to extract
    full-text content for the constituent bibliographic records.
    """

    def test_read_pdf(self):
        corpus = read(datapath3)

        self.assertIsInstance(corpus, Corpus)

        self.assertIn('pdf_text', corpus.features,
        """
        If a dataset has full-text content available in PDFs, then
        'structuredfeatures' should contain an element called 'pdf_text'.
        """)

        self.assertIsInstance(corpus.features['pdf_text'],
                              StructuredFeatureSet,
        """
        'pdf_text' should be an instance of StructuredFeatureSet.
        """)

        self.assertEqual(len(corpus.features['pdf_text']), 7,
        """
        There should be seven (7) full-text pdf StructuredFeatures for this
        particular dataset.
        """)


class TestZoteroParser(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath)
        self.assertIsInstance(corpus, Corpus)

    def test_read_files(self):
        # TODO: attempt to read contents of files?
        corpus = read(datapath2, index_by='uri')
        self.assertIsInstance(corpus, Corpus)

    def test_read_nocorpus(self):
        papers = read(datapath, corpus=False)
        self.assertIsInstance(papers, list)
        self.assertIsInstance(papers[0], Paper)

    def test_handle_date(self):
        parser = ZoteroParser(datapath)
        parser.parse()
        date_list = ["January 23, 2015",
                     "2015-9",
                     "2015-9-23",
                     "09/23/2015",
                     "2015-09-23"]

        for each_date in date_list:
            self.assertEqual(2015, parser.handle_date(each_date),
            """
            Date Not properly Formatted.
            """)

    def test_parse(self):
        parser = ZoteroParser(datapath)
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
        self.assertEqual(N, 12, 'Expected 12 entries, found {0}.'.format(N))


if __name__ == '__main__':
    unittest.main()
