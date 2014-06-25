from settings import *

import unittest

from tethne.persistence import HDF5DataCollection, HDF5Paper

from nltk.corpus import stopwords
from tethne.readers import wos, dfr
import os

import cPickle as pickle
with open('{0}/dfr_DataCollection.pickle'.format(picklepath), 'r') as f:
    D = pickle.load(f)

class TestSaveLoadDataCollection(unittest.TestCase):
    def setUp(self):
        pass

    def test_reload(self):
        HD = D.to_hdf5(datapath=temppath)
        hdpath = HD.path
        self.delpath = hdpath

        HD_ = HDF5DataCollection([], index=False, datapath=hdpath)

        # Papers should be the same.
        self.assertEqual(   len(HD_.papers), len(D.papers)  )
        
        # Citations should be the same.
        self.assertEqual(   len(HD_.citations), len(D.citations)    )
        self.assertEqual(   len(HD_.papers_citing), len(D.papers_citing)   )
        
        # Authors should be the same.
        self.assertEqual(   len(HD_.authors), len(D.authors)    )

        # Features should be the same.
        self.assertEqual(   len(HD_.features['unigrams']['index']),
                            len(D.features['unigrams']['index'])   )
        self.assertEqual(   len(HD_.features['unigrams']['features']),
                            len(D.features['unigrams']['features'])   )
        self.assertEqual(   len(HD_.features['unigrams']['counts']),
                            len(D.features['unigrams']['counts'])   )
        self.assertEqual(   len(HD_.features['unigrams']['documentCounts']),
                            len(D.features['unigrams']['documentCounts']) )

        # Axes should be the same.
        self.assertEqual(   len(HD_.axes), len(D.axes)  )
        self.assertEqual(   len(HD_.axes['date']), len(D.axes['date'])  )

    def tearDown(self):
        os.remove(self.delpath)

class TestDataCollectionDfRHDF5(unittest.TestCase):
    def setUp(self):
        """
        Generate a DataCollection from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')

        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.__init__[dfr].png'
        with Profile(pcgpath):
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
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.__init__[wos].png'
        with Profile(pcgpath):
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

        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.abstract_to_features[wos].png'
        with Profile(pcgpath):
            self.D.abstract_to_features()

        self.assertIn('abstractTerms', self.D.features)
        self.assertNotIn('the', self.D.features['abstractTerms']['index'].values())

        abs_available = len([p for p in self.D.papers.values() if p['abstract'] is not None ])
        abs_tokenized = len(self.D.features['abstractTerms']['features'])
        self.assertEqual(abs_tokenized, abs_available)

    def test_slice(self):
        """
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.slice[wos].png'
        with Profile(pcgpath):
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

        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.__init__[dfr_filter].png'
        with Profile(pcgpath):
            D = HDF5DataCollection(self.papers,
                                        features={'unigrams': self.ngrams},
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
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5DataCollection.filter_features[dfr].png'
        with Profile(pcgpath):
            D.filter_features('unigrams', 'unigrams_lim', filt)
        
        self.assertEqual(len(D.features['unigrams_lim']['index']), 14709)        

if __name__ == '__main__':
    unittest.main()