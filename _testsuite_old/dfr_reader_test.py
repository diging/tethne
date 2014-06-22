import sys
sys.path.append("../")
import tethne.readers as rd
import tethne.data as dt
import tethne.writers as wr
import unittest

class TestNGrams(unittest.TestCase):

    def setUp(self):
        filepath = "./testin/2013.5.3.cHrmED8A"
        self.unigrams = rd.dfr.ngrams(filepath, N='uni')
        self.papers = rd.dfr.read(filepath)

        self.D = dt.DataCollection(self.papers)
        self.D.slice('date')
        
        self.t_unigrams, self.voc, self.counts = rd.dfr.tokenize(self.unigrams)

    def test_read(self):
        self.assertEqual(len(self.unigrams), 398)

    def test_write_corpus(self):
        """will fail if non-ascii characters aren't stripped."""
        ret = wr.corpora.to_documents('./testout/mycorpus', self.unigrams)
        self.assertEqual(ret, None)

    def test_write_corpus_papers(self):
        ret = wr.corpora.to_documents('./testout/mycorpus', self.unigrams,
                                                             papers=self.papers)
        self.assertEqual(ret, None)

    def test_write_dtm(self):
        ret = wr.corpora.to_dtm_input('./testout/mydtm', self.D, self.unigrams,
                                      self.voc)


class TestRead(unittest.TestCase):

    def setUp(self):
        filepath = "./testin/dfr"
        self.papers = rd.dfr.read(filepath)

    def test_number(self):
        """
        Each article should be converted.
        """

        self.assertEqual(len(self.papers), 4)

    def test_type(self):
        """
        Should produce a list of :class:`.Paper`
        """

        self.assertIs(type(self.papers[0]), dt.Paper)

    def test_handle_authors(self):
        """
        _handle_authors should generate lists of author surnames (aulast) and
        author first-initialis (auinit) of the same length.
        """

        aulast = self.papers[0]['aulast']
        expected = ['MADGWICK', 'SATOO']
        self.assertListEqual(aulast, expected )

        auinit = self.papers[0]['auinit']
        expected = ['H', 'T']
        self.assertListEqual(auinit, expected )

        self.assertEqual(len(aulast), len(auinit))

    def test_handle_authors_raises(self):
        """
        If parameter is not a list or a string, should raise a ValueError.
        """

        with self.assertRaises(ValueError):
            rd.dfr._handle_authors(1234)

    def test_handle_pubdate(self):
        """
        _handle_pubdate should yield a four-digit integer from a DfR pubdate
        string.
        """

        pubdate = self.papers[0]['date']
        self.assertIs(type(pubdate), int)   # Integer

        self.assertEqual(len(str(pubdate)), 4) # Four-digit

    def test_handle_pagerange(self):
        """
        _handle_pagerange should yield start and end pages, as strings.
        """

        start = self.papers[0]['spage']
        end = self.papers[0]['epage']

        self.assertIs(type(start), str) # Strings
        self.assertIs(type(end), str)

    def teardown(self):
        pass

if __name__ == '__main__':
    unittest.main()