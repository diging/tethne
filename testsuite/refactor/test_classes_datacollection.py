import unittest

import sys
sys.path.append('../../')

from tethne.readers import wos, dfr
from tethne.classes import DataCollection

from nltk.corpus import stopwords

import logging
logging.basicConfig()
logger = logging.getLogger('tethne.classes.datacollection')
logger.setLevel('ERROR')

class TestPaper(unittest.TestCase):
    pass

class TestDataCollectionWoS(unittest.TestCase):
    def setUp(self):
        """
        Genereate a DataCollection from some WoS data.
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        papers = wos.read(wosdatapath)
        self.D = DataCollection(papers)
    
    def test_index_papers(self):
        """
        Should be N_p number of papers.
        """
        self.assertEqual(self.D.N_p, 10)
        self.assertEqual(len(self.D.papers), self.D.N_p)

    def test_index_papers_by_author(self):
        """
        Should be N_a number of authors.
        """
        self.assertEqual(self.D.N_a, 51)
        self.assertEqual(len(self.D.authors), self.D.N_a)

    def test_index_citations(self):
        """
        Should be N_c number of citations.
        """
        self.assertEqual(self.D.N_c, 531)
        self.assertEqual(len(self.D.citations), self.D.N_c)

    def test_tokenize_features(self):
        """
        Should be no features.
        """
        self.assertEqual(self.D.features, None)

    def test_abstract_to_features(self):
        """
        Should generate features from available abstracts.
        """
        pass

    def test_slice(self):
        """
        """

        self.D.slice('date')
        self.assertIn('date', self.D.axes)
        self.assertIn(2012, self.D.axes['date'])
        self.assertIn(2013, self.D.axes['date'])
        self.assertEqual(len(self.D.axes['date'][2012]), 5)

    def test_get_slice(self):
        pass

    def test_get_slices(self):
        pass

class TestDataCollectionDfR(unittest.TestCase):
    def setUp(self):
        """
        Generate a DataCollection from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')
        self.D = DataCollection(papers, features={'unigrams': ngrams},
                                        index_by='doi',
                                        exclude_features=set(stopwords.words()))

    def test_index_papers(self):
        """
        Should be N_p number of papers.
        """
        self.assertEqual(self.D.N_p, 241)
        self.assertEqual(len(self.D.papers), self.D.N_p)

    def test_index_papers_by_author(self):
        """
        Should be N_a number of authors.
        """
        self.assertEqual(self.D.N_a, 196)
        self.assertEqual(len(self.D.authors), self.D.N_a)

    def test_index_citations(self):
        """
        Should be no citations.
        """
        self.assertEqual(self.D.N_c, 0)
        self.assertEqual(len(self.D.citations), self.D.N_c)

    def test_tokenize_features(self):
        """
        Should be N_f features in the appropriate features dict.
        """
        self.assertIn('unigrams', self.D.features)
        self.assertEqual(len(self.D.features), 1)
        self.assertEqual(len(self.D.features['unigrams']['index']), 51641)

if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()