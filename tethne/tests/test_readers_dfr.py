import sys
sys.path.append('../tethne')

import unittest
from tethne.readers import merge
from tethne.readers.dfr import read, ngrams, _handle_author,_dfr2paper_map,_create_ayjid,_handle_pagerange,tokenize,_handle_authors,_handle_paper
from tethne import Corpus, Paper, FeatureSet
import xml.etree.ElementTree as ET

datapath = './tethne/tests/data/dfr'
datapath_float_weights = './tethne/tests/data/dfr_float_weights'
sample_datapath = './tethne/tests/data/test_citations_sample.xml'


class TestDFRReaderStreaming(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath, streaming=True)

        self.assertIsInstance(corpus, Corpus)

        for e in corpus:
            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, unicode)

            if hasattr(e, 'date'):
                self.assertIsInstance(e.date, int)

            if hasattr(e, 'authors_init'):
                self.assertIsInstance(e.authors_init, list)
                for a in e.authors_init:

                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)

            if hasattr(e, 'journal'):
                self.assertIsInstance(e.journal, unicode)

            if hasattr(e, 'abstract'):
                self.assertIsInstance(e.abstract, unicode)

            if hasattr(e, 'authorKeywords'):
                self.assertIsInstance(e.authorKeywords, list)

            if hasattr(e, 'keywordsPlus'):
                self.assertIsInstance(e.keywordsPlus, list)
            if hasattr(e, 'doi'):
                self.assertIsInstance(e.doi, unicode)
            if hasattr(e, 'volume'):
                self.assertIsInstance(e.volume, unicode)

            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, unicode)




class TestDFRReader(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath)

        self.assertIsInstance(corpus, Corpus)

        for e in corpus.papers:
            if hasattr(e, 'date'):
                self.assertIsInstance(e.date, int)

            if hasattr(e, 'authors_init'):
                self.assertIsInstance(e.authors_init, list)
                for a in e.authors_init:

                    self.assertTrue(a[0].isupper(), uppererr)
                    self.assertTrue(a[1].isupper(), uppererr)

            if hasattr(e, 'journal'):
                self.assertIsInstance(e.journal, unicode)

            if hasattr(e, 'abstract'):
                self.assertIsInstance(e.abstract, unicode)

            if hasattr(e, 'authorKeywords'):
                self.assertIsInstance(e.authorKeywords, list)

            if hasattr(e, 'keywordsPlus'):
                self.assertIsInstance(e.keywordsPlus, list)
            if hasattr(e, 'doi'):
                self.assertIsInstance(e.doi, unicode)
            if hasattr(e, 'volume'):
                self.assertIsInstance(e.volume, unicode)

            if hasattr(e, 'title'):
                self.assertIsInstance(e.title, unicode)

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
        self.assertEqual(len(grams.index), 105216)

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


class TestHandleAuthor(unittest.TestCase):

    def test_handle_author_NOJR(self):
        self.assertEqual(('TERRELL', 'E'),_handle_author("Edward E. Terrell"))

    def test_handle_author_JR(self):
        self.assertEqual(('STEBBINS, JR', 'G'),_handle_author("G. Ledyard Stebbins, Jr."))

class TestDfr2PaperMap(unittest.TestCase):

    def test_dfr2paper(self):
        local_dict = { 'doi': 'doi','title': 'atitle','journaltitle': 'jtitle','volume': 'volume','issue': 'issue'    }
        self.assertEqual(local_dict, _dfr2paper_map())

class TestCreateAyijid(unittest.TestCase):

    def test_no_aulast(self):
        self.assertEqual(' R  ',_create_ayjid(None,['R'],None,None))
    def test_no_auinit(self):
        self.assertEqual('NIXON   ',_create_ayjid(['NIXON'],None,None,None))
    def test_all_None_args(self):
        self.assertEqual('UNKNOWN PAPER',_create_ayjid(None,None,None,None))

class TestHandlePageRange(unittest.TestCase):

    def test_handle_pagerange_noNumbers(self):
        input_pagerange = 'pp.efcadd'
        req_pagerange = (u'0',u'0')
        self.assertEqual(req_pagerange,_handle_pagerange(input_pagerange))

    def test_handle_pagerange(self):
        input_pagerange = 'pp. 111-999'
        req_pagerange = (u'111',u'999')
        self.assertEqual(req_pagerange,_handle_pagerange(input_pagerange))

class TestHandleAuthors(unittest.TestCase):

    """testing the functionality when the input parameter is list"""
    def test_handle_authors_list(self):

        exp_aulast = ['STROMNAES', 'GARBER']
        exp_auinit = ['C', 'E']

        self.assertEqual(exp_aulast,_handle_authors(['Cistein Stromnaes', 'E. D. Garber'])[0])
        self.assertEqual(exp_auinit,_handle_authors(['Cistein Stromnaes', 'E. D. Garber'])[1])

    """testing the functionality when the input parameter is String"""
    def test_handle_authors_String(self):

        exp_aulast = ['YARNELL']
        exp_auinit = ['S']

        self.assertEqual(exp_aulast,_handle_authors('S. H. Yarnell')[0])
        self.assertEqual(exp_auinit,_handle_authors('S. H. Yarnell')[1])

class TestHandlePaper(unittest.TestCase):

    def test_handle_Paper(self):
       with open(sample_datapath, 'r') as f:
            root = ET.fromstring(f.read())
            pattern = './/{elem}'.format(elem='article')
            elements = root.findall(pattern)
            presentPaper = _handle_paper(elements[0])

            self.assertIsInstance(presentPaper,Paper)
            self.assertEqual(1954,presentPaper.__getitem__('date'))


if __name__ == '__main__':
    unittest.main()
