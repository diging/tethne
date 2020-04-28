import sys
sys.path.append('../tethne')

import re

import unittest
from tethne.readers.wos import WoSParser, read
from tethne import Corpus, Paper, StreamingCorpus

datapath = './tethne/tests/data/wos2.txt'
datapath_v = './tethne/tests/data/valentin.txt'

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


def is_number(value):
    try:
        int(value)
    except ValueError:
        try:
            float(value)
        except ValueError:
            return False
    return True


class TestWoSParserStreaming(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath, streaming=True)
        self.assertIsInstance(corpus, StreamingCorpus)

        derror = "{0} should be {1}, but is {2}"
        dauthorAddressError = "{0} should be {1} or {2}, but is {3}"
        for e in corpus:
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
            if hasattr(e, 'WC'):
                self.assertIsInstance(e.WC, list,
                                      derror.format('WC', 'list',
                                                    type(e.WC)))
            if hasattr(e, 'subject'):
                self.assertIsInstance(e.subject, list,
                                      derror.format('subject', 'list',
                                                    type(e.subject)))
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

            if hasattr(e, 'authorAddress'):
                self.assertTrue((type(e.authorAddress) is list or type(e.authorAddress) is unicode),
                                dauthorAddressError.format('authorAddress', 'unicode',
                                                           'list', type(e.authorAddress)))

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
        dauthorAddressError = "{0} should be {1} or {2}, but is {3}"
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
            if hasattr(e, 'WC'):
                self.assertIsInstance(e.WC, list,
                                      derror.format('WC', 'list',
                                                    type(e.WC)))
            if hasattr(e, 'subject'):
                self.assertIsInstance(e.subject, list,
                                      derror.format('subject', 'list',
                                                    type(e.subject)))
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

            if hasattr(e, 'authorAddress'):
                self.assertTrue((type(e.authorAddress) is list or type(e.authorAddress) is unicode),
                                dauthorAddressError.format('authorAddress', 'unicode',
                                                           'list', type(e.authorAddress)))

        # Check integrity of tag-to-field mapping.
        for tag, attr in parser.tags.items():
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

class TestWithStarCR(unittest.TestCase):
    def setUp(self):
        class TestParser(WoSParser):
            def handle_CR(self, value):
                citation = super(TestParser, self).handle_CR(value)
                # The lastname part of the first author name should match the
                #  CR author name as written, but without the leading *.
                datematch = re.match('([0-9]{4})', value)
                if datematch:
                    date = datematch.group(1)
                    if len(citation.authors) > 0:
                        last = [unicode(v[0]) for v
                                in zip(*zip(*citation.authors)[0])]
                        assert unicode(date) not in last

                if value.startswith('*'):
                    expected = re.match('\*([\w\s]+)\,', value).group(1)
                    assert expected == citation.authors[0][0][0]
                    assert not is_number(citation.authors[0][0][0])

        self.parser = TestParser(datapath_v)

    def test_citedRefs(self):
        try:
            self.parser.parse()
        except AssertionError:
            self.fail('Trouble processing cited references')



if __name__ == '__main__':
    unittest.main()
