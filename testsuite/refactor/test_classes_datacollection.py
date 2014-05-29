import unittest

import sys
sys.path.append('../../')

from tethne.readers import wos, dfr
from tethne.classes import DataCollection, HDF5DataCollection

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
    
    def test_indexing(self):
        """
        index_papers: Should be N_p number of papers.
        index_papers_by_authors: N_a authors
        index_citations: N_c citations
        """
        # papers
        self.assertEqual(self.D.N_p, 10)
        self.assertEqual(len(self.D.papers), self.D.N_p)
    
        # authors
        self.assertEqual(self.D.N_a, 51)
        self.assertEqual(len(self.D.authors), self.D.N_a)
    
        # citations
        self.assertEqual(self.D.N_c, 531)
        self.assertEqual(len(self.D.citations), self.D.N_c)
    
    def test_abstract_to_features(self):
        """
        Should generate features from available abstracts.
        """

        self.D.abstract_to_features()
        self.assertIn('abstractTerms', self.D.features)
        self.assertNotIn('the', self.D.features['abstractTerms']['index'].values())

        abs_available = len([p for p in self.D.papers.values() if p['abstract'] is not None ])
        abs_tokenized = len(self.D.features['abstractTerms']['features'])
        self.assertEqual(abs_tokenized, abs_available)

    def test_slice(self):
        """
        """

        self.D.slice('date')
        self.assertIn('date', self.D.axes)
        self.assertIn(2012, self.D.axes['date'])
        self.assertIn(2013, self.D.axes['date'])
        self.assertEqual(len(self.D.axes['date'][2012]), 5)

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

    def test_indexing(self):
        """
        index_papers: Should be N_p number of papers.
        index_papers_by_author: N_a authors
        index_citations: no citations
        """
        # papers
        self.assertEqual(self.D.N_p, 241)
        self.assertEqual(len(self.D.papers), self.D.N_p)
    
        # papers by author
        self.assertEqual(self.D.N_a, 193)
        self.assertEqual(len(self.D.authors), self.D.N_a)

        # citations
        self.assertEqual(self.D.N_c, 0)
        self.assertEqual(len(self.D.citations), self.D.N_c)

    def test_tokenize_features(self):
        """
        Should be N_f features in the appropriate features dict.
        """
        self.assertIn('unigrams', self.D.features)
        self.assertIn('features', self.D.features['unigrams'])
        self.assertIn('index', self.D.features['unigrams'])
        self.assertIn('counts', self.D.features['unigrams'])
        self.assertIn('documentCounts', self.D.features['unigrams'])
        self.assertEqual(len(self.D.features), 2)
        self.assertEqual(len(self.D.features['unigrams']['index']), 51658)

        self.assertEqual(len(self.D.features['unigrams']['counts']), 51658)
        self.assertEqual(len(self.D.features['unigrams']['documentCounts']), 51658)

class TestDataCollectionDfRHDF5(unittest.TestCase):
    def setUp(self):
        """
        Generate a DataCollection from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')
        self.D = HDF5DataCollection(papers, features={'unigrams': ngrams},
                                            index_by='doi',
                                            exclude_features=set(stopwords.words()))

    def test_indexing(self):
        """
        index_papers: Should be N_p number of papers.
        index_papers_by_author: N_a authors
        index_citations: no citations
        """
        # papers
        self.assertEqual(self.D.N_p, 241)
        self.assertEqual(len(self.D.papers), self.D.N_p)
    
        # papers by author
        self.assertEqual(self.D.N_a, 193)
        self.assertEqual(len(self.D.authors), self.D.N_a)

        # citations
        self.assertEqual(self.D.N_c, 0)
        self.assertEqual(len(self.D.citations), self.D.N_c)


    def test_tokenize_features(self):
        """
        Should be N_f features in the appropriate features dict.
        """
        self.assertIn('unigrams', self.D.features)
        self.assertIn('features', self.D.features['unigrams'])
        self.assertIn('index', self.D.features['unigrams'])
        self.assertIn('counts', self.D.features['unigrams'])
        self.assertIn('documentCounts', self.D.features['unigrams'])
        self.assertEqual(len(self.D.features), 2)
        self.assertEqual(len(self.D.features['unigrams']['index']), 51658)

        self.assertEqual(len(self.D.features['unigrams']['counts']), 51658)
        self.assertEqual(len(self.D.features['unigrams']['documentCounts']), 51658)

class TestDataCollectionWoSHDF5(unittest.TestCase):
    def setUp(self):
        """
        Genereate a DataCollection from some WoS data.
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        papers = wos.read(wosdatapath)
        self.D = HDF5DataCollection(papers)
    
    def test_indexing(self):
        """
        index_papers: Should be N_p number of papers.
        index_papers_by_authors: N_a authors
        index_citations: N_c citations
        """
        # papers
        self.assertEqual(self.D.N_p, 10)
        self.assertEqual(len(self.D.papers), self.D.N_p)
    
        # authors
        self.assertEqual(self.D.N_a, 51)
        self.assertEqual(len(self.D.authors), self.D.N_a)
    
        # citations
        self.assertEqual(self.D.N_c, 531)
        self.assertEqual(len(self.D.citations), self.D.N_c)
    
    def test_abstract_to_features(self):
        """
        Should generate features from available abstracts.
        """

        self.D.abstract_to_features()
        self.assertIn('abstractTerms', self.D.features)
        self.assertNotIn('the', self.D.features['abstractTerms']['index'].values())

        abs_available = len([p for p in self.D.papers.values() if p['abstract'] is not None ])
        abs_tokenized = len(self.D.features['abstractTerms']['features'])
        self.assertEqual(abs_tokenized, abs_available)

    def test_slice(self):
        """
        """

        self.D.slice('date')
        self.assertIn('date', self.D.axes)
        self.assertIn(2012, self.D.axes['date'])
        self.assertIn(2013, self.D.axes['date'])
        self.assertEqual(len(self.D.axes['date'][2012]), 5)


if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()