import sys
sys.path.append('../tethne')

import re

import unittest
from tethne.readers.zotero import read, ZoteroParser, _infer_spaces
from tethne import Corpus, Paper, StructuredFeatureSet

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str

datapath = './tethne/tests/data/zotero'
datapath2 = './tethne/tests/data/zotero2'
datapath3 = './tethne/tests/data/zotero_withfiles'
duplicatePath = './tethne/tests/data/Duplicate'


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


class TestZoteroDuplicates(unittest.TestCase):
    def test_duplicate_Papers_length(self):
        """
        Tests for user-warning raised in case of duplicate papers in a Corpus.
        Definition of duplicate papers is : Papers which have the same index_by field value.
        Example :

        Two papers in a Zotero collection, with the same URI, are duplicates
        Two papers from World of Science with the same WOSID are duplicates

        Returns
        -------
        Fails when the attribute duplicate_papers(Dictionary) is not populated.

        duplicate_papers['http://www.jstor.org/stable/2460126'] = 2
        This means there are 2 papers with the URI 'http://www.jstor.org/stable/2460126'

        """
        corpus = read(duplicatePath, corpus=True)
        self.assertGreater(len(corpus.duplicate_papers), 0)
        self.assertEqual(corpus.duplicate_papers['http://www.jstor.org/stable/2460126'], 2)




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



    def test_authors(self):
        """
        Tests for empty author names for each paper in a ZOTERO Corpus

        Returns
        -------
        Fails : When the author-name is empty, it fails

        """
        papers = read(datapath)
        for paper in papers:
            self.assertNotEqual(len(paper.authors), 0, "Author list cannot be empty")


    def test_authors_full(self):
        """
        Tests for empty author_full names for each paper in a ZOTERO Corpus

        Returns
        -------
        Fails : When the author_full names is empty, it fails.

        """
        papers = read(datapath)
        for paper in papers:
            self.assertNotEqual(len(paper.authors_full), 0, "Author_full list cannot be empty")


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
                self.assertIsInstance(e.journal, unicode,
                                      derror.format('journal', 'unicode',
                                                    type(e.journal)))
            if hasattr(e, 'abstract'):
                self.assertIsInstance(e.abstract, unicode,
                                      derror.format('abstract', 'unicode',
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
                self.assertIsInstance(e.doi, unicode,
                                      derror.format('doi', 'unicode',
                                                    type(e.doi)))
            if hasattr(e, 'volume'):
                self.assertIsInstance(e.volume, unicode,
                                      derror.format('volume', 'unicode',
                                                    type(e.volume)))

            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, unicode,
                                      derror.format('title', 'unicode',
                                                    type(e.title)))

        # Check integrity of tag-to-field mapping.
        for tag, attr in parser.tags.items():
            self.assertFalse(hasattr(e, tag),
                             ' '.join(['{0} should map to'.format(tag),
                                       '{0}, but does not.'.format(attr)]))

        # Check number of records.
        N = len(parser.data)
        self.assertEqual(N, 12, 'Expected 12 entries, found {0}.'.format(N))


if __name__ == '__main__':
    unittest.main()
