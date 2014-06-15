import unittest

import sys
sys.path.append('../../')

from tethne.persistence import HDF5DataCollection, HDF5Paper
from nltk.corpus import stopwords
from tethne.readers import wos, dfr

# Set log level to ERROR to avoid debug output.
import logging
logging.basicConfig()
logger = logging.getLogger('tethne.classes.datacollection')
logger.setLevel('ERROR')
logger = logging.getLogger('tethne.persistence.hdf5')
logger.setLevel('ERROR')

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
                                            exclude=set(stopwords.words()))

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

        self.assertEqual(len(self.D.features['unigrams']['index']), 51639)
        self.assertEqual(len(self.D.features['unigrams']['counts']), 51639)
        self.assertEqual(len(self.D.features['unigrams']['documentCounts']), 51639)

class TestDataCollectionWoSHDF5(unittest.TestCase):
    def setUp(self):
        """
        Genereate a DataCollection from some WoS data.
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        papers = wos.read(wosdatapath)
        self.D = HDF5DataCollection(papers, index_by='wosid')
    
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
        
class TestDataCollectionTokenization(unittest.TestCase):
    def setUp(self):
        self.dfrdatapath = '{0}/dfr'.format(datapath)
        self.papers = dfr.read(self.dfrdatapath)
        self.ngrams = dfr.ngrams(self.dfrdatapath, 'uni')
        
    def test_tokenize_filter(self):
        """
        Applying a filter should result in a smaller featureset.
        """
        filt = lambda s: len(s) > 3 # Must have at least four characters.

        D = HDF5DataCollection(self.papers, features={'unigrams': self.ngrams},
                                            index_by='doi',
                                            exclude=set(stopwords.words()),
                                            filt=filt)
        self.assertEqual(len(D.features['unigrams']['index']), 49503)
                
    def test_filter_features(self):
        """
        :func:`DataCollection.filterfeatures` should generate a new, more
        limited featureset.
        """
        
        def filt(s, C, DC):
            """
            Token must occur at least thrice overall, and in at least 2
            documents, and must have more than three characters.
            """

            if C > 2 and DC > 1 and len(s) > 3:
                return True
            return False
            
        D = HDF5DataCollection(self.papers, features={'unigrams': self.ngrams},
                                            index_by='doi',
                                            exclude=set(stopwords.words()))

        D.filter_features('unigrams', 'unigrams_lim', filt)
        self.assertEqual(len(D.features['unigrams_lim']['index']), 14709)        

if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()