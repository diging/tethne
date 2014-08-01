from settings import *

import unittest

from tethne.persistence.hdf5.corpus import HDF5Corpus, HDF5Paper
from tethne import Corpus, Paper
from tethne.persistence.hdf5.corpus import from_hdf5, to_hdf5

from nltk.corpus import stopwords
from tethne.readers import wos, dfr
import os

D = dfr.read_corpus(datapath + '/dfr', features=('uni',))
D.slice('date', 'time_period', window_size=1)

#class TestSaveLoadCorpus(unittest.TestCase):
#    def setUp(self):
#        pass
#
#    def test_reload(self):
#        HD = D.to_hdf5(datapath=temppath)
#        hdpath = HD.path
#        delpath = hdpath
#
#        HD_ = HDF5Corpus([], index=False, datapath=hdpath)
#
#        # Papers should be the same.
#        self.assertEqual(   len(HD_.papers), len(D.papers)  )
#        
#        # Citations should be the same.
#        self.assertEqual(   len(HD_.citations), len(D.citations)    )
#        self.assertEqual(   len(HD_.papers_citing), len(D.papers_citing)   )
#        
#        # Authors should be the same.
#        self.assertEqual(   len(HD_.authors), len(D.authors)    )
#
#        # Features should be the same.
#        self.assertEqual(   len(HD_.features['unigrams']['index']),
#                            len(D.features['unigrams']['index'])   )
#        self.assertEqual(   len(HD_.features['unigrams']['features']),
#                            len(D.features['unigrams']['features'])   )
#        self.assertEqual(   len(HD_.features['unigrams']['counts']),
#                            len(D.features['unigrams']['counts'])   )
#        self.assertEqual(   len(HD_.features['unigrams']['documentCounts']),
#                            len(D.features['unigrams']['documentCounts']) )
#
#        # Axes should be the same.
#        self.assertEqual(   len(HD_.axes), len(D.axes)  )
#        self.assertEqual(   len(HD_.axes['date']), len(D.axes['date'])  )
#        os.remove(delpath)
#
#class TestCorpusDfRHDF5(unittest.TestCase):
#    def setUp(self):
#        """
#        Generate a :class:`.Corpus` from some DfR data with unigrams.
#        """
#        
#        dfrdatapath = '{0}/dfr'.format(datapath)
#    
#        papers = dfr.read(dfrdatapath)
#        ngrams = dfr.ngrams(dfrdatapath, 'uni')
#
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.__init__[dfr].png'
#        with Profile(pcgpath):
#            self.D = HDF5Corpus(papers, features={'unigrams': ngrams},
#                                                index_by='doi',
#                                                exclude=set(stopwords.words()))
#
#    def test_indexing(self):
#        """
#        index_papers: Should be N_p number of papers.
#        index_papers_by_author: N_a authors
#        index_citations: no citations
#        """
#
#        # papers
#        self.assertEqual(self.D.N_p, 241)
#        self.assertEqual(len(self.D.papers), self.D.N_p)
#    
#        # papers by author
#        self.assertEqual(self.D.N_a, 193)
#        self.assertEqual(len(self.D.authors), self.D.N_a)
#
#        # citations
#        self.assertEqual(self.D.N_c, 0)
#        self.assertEqual(len(self.D.citations), self.D.N_c)
#
#    def test_tokenize_features(self):
#        """
#        Should be N_f features in the appropriate features dict.
#        """
#
#        self.assertIn('unigrams', self.D.features)
#        self.assertIn('features', self.D.features['unigrams'])
#        self.assertIn('index', self.D.features['unigrams'])
#        self.assertIn('counts', self.D.features['unigrams'])
#        self.assertIn('documentCounts', self.D.features['unigrams'])
#        self.assertEqual(len(self.D.features), 2)
#
#        self.assertEqual(len(self.D.features['unigrams']['index']), 51639)
#        self.assertEqual(len(self.D.features['unigrams']['counts']), 51639)
#        self.assertEqual(len(self.D.features['unigrams']['documentCounts']), 51639)
#
#class TestCorpusWoSHDF5(unittest.TestCase):
#    def setUp(self):
#        """
#        Genereate a :class:`.Corpus` from some WoS data.
#        """
#    
#        wosdatapath = '{0}/wos.txt'.format(datapath)
#
#        papers = wos.read(wosdatapath)
#        
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.__init__[wos].png'
#        with Profile(pcgpath):
#            self.D = HDF5Corpus(papers, index_by='wosid')
#
#    def test_indexing(self):
#        """
#        index_papers: Should be N_p number of papers.
#        index_papers_by_authors: N_a authors
#        index_citations: N_c citations
#        """
#        
#        # papers
#        self.assertEqual(self.D.N_p, 10)
#        self.assertEqual(len(self.D.papers), self.D.N_p)
#    
#        # authors
#        self.assertEqual(self.D.N_a, 51)
#        self.assertEqual(len(self.D.authors), self.D.N_a)
#    
#        # citations
#        self.assertEqual(self.D.N_c, 531)
#        self.assertEqual(len(self.D.citations), self.D.N_c)
#
#    def test_abstract_to_features(self):
#        """
#        Should generate features from available abstracts.
#        """
#
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.abstract_to_features[wos].png'
#        with Profile(pcgpath):
#            self.D.abstract_to_features()
#
#        self.assertIn('abstractTerms', self.D.features)
#        self.assertNotIn('the', self.D.features['abstractTerms']['index'].values())
#
#        abs_available = len([p for p in self.D.papers.values() if p['abstract'] is not None ])
#        abs_tokenized = len(self.D.features['abstractTerms']['features'])
#        self.assertEqual(abs_tokenized, abs_available)
#
#    def test_slice(self):
#        """
#        """
#
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.slice[wos].png'
#        with Profile(pcgpath):
#            self.D.slice('date')
#
#        self.assertIn('date', self.D.axes)
#        self.assertIn(2012, self.D.axes['date'])
#        self.assertIn(2013, self.D.axes['date'])
#        self.assertEqual(len(self.D.axes['date'][2012]), 5)
#        
#class TestCorpusTokenization(unittest.TestCase):
#    def setUp(self):
#
#        self.dfrdatapath = '{0}/dfr'.format(datapath)
#        self.papers = dfr.read(self.dfrdatapath)
#        self.ngrams = dfr.ngrams(self.dfrdatapath, 'uni')
#        
#    def test_tokenize_filter(self):
#        """
#        Applying a filter should result in a smaller featureset.
#        """
#        filt = lambda s: len(s) > 3 # Must have at least four characters.
#
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.__init__[dfr_filter].png'
#        with Profile(pcgpath):
#            D = HDF5Corpus(self.papers,
#                                        features={'unigrams': self.ngrams},
#                                        index_by='doi',
#                                        exclude=set(stopwords.words()),
#                                        filt=filt)
#        
#                
#        self.assertEqual(len(D.features['unigrams']['index']), 49503)
#                
#    def test_filter_features(self):
#        """
#        :func:`Corpus.filterfeatures` should generate a new, more
#        limited featureset.
#        """
#        
#        def filt(s, C, DC):
#            """
#            Token must occur at least thrice overall, and in at least 2
#            documents, and must have more than three characters.
#            """
#
#            if C > 2 and DC > 1 and len(s) > 3:
#                return True
#            return False
#        
#        D = HDF5Corpus(self.papers, features={'unigrams': self.ngrams},
#                                            index_by='doi',
#                                            exclude=set(stopwords.words()))
#        
#        pcgpath = cg_path + 'persistence.hdf5.HDF5Corpus.filter_features[dfr].png'
#        with Profile(pcgpath):
#            D.filter_features('unigrams', 'unigrams_lim', filt)
#        
#        self.assertEqual(len(D.features['unigrams_lim']['index']), 14709)        


class TestCorpusDfR(unittest.TestCase):
    def setUp(self):
        """
        Generate a Corpus from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
        self.h5name = 'test_HDF5Corpus.h5'
        self.h5path = temppath+'/'+self.h5name
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')

        pcgpath = cg_path + 'classes.Corpus.__init__[dfr].png'
        with Profile(pcgpath):
            self.D = Corpus(papers, features={'unigrams': ngrams},
                                                index_by='doi',
                                                exclude=set(stopwords.words()))


    def test_to_hdf5(self):
        """
        Create a new :class:`.HDF5Corpus` with identical attributes.
        """

        self.D.slice('date', method='time_period', window_size=5)
        HD = to_hdf5(self.D, datapath=self.h5path)
        self.assertIsInstance(HD, HDF5Corpus)

        # Papers should be the same.
        self.assertEqual(   len(HD.papers), len(self.D.papers)  )
        
        # Citations should be the same.
        self.assertEqual(   len(HD.citations), len(self.D.citations)    )
        self.assertEqual(   len(HD.papers_citing), len(self.D.papers_citing)   )
        self.assertEqual(   set(HD.papers_citing.keys()),
                            set(self.D.papers_citing.keys())    )
        
        # Authors should be the same.
        self.assertEqual(   len(HD.authors), len(self.D.authors)    )
        self.assertEqual(set(HD.authors.keys()), set(self.D.authors.keys()))
        for k in self.D.authors.keys():
            self.assertTrue(k in HD.authors)

        # Features should be the same.
        self.assertEqual(   len(HD.features['unigrams']['index']),
                            len(self.D.features['unigrams']['index'])   )
        self.assertEqual(   len(HD.features['unigrams']['features']),
                            len(self.D.features['unigrams']['features'])   )
        self.assertEqual(   len(HD.features['unigrams']['counts']),
                            len(self.D.features['unigrams']['counts'])   )
        self.assertEqual(   len(HD.features['unigrams']['documentCounts']),
                            len(self.D.features['unigrams']['documentCounts']) )
        self.assertEqual(   len(HD.features['unigrams']['papers']),
                            len(self.D.features['unigrams']['papers']) )

        # Axes should be the same.
        self.assertEqual(   len(HD.axes), len(self.D.axes)  )
        self.assertEqual(   len(HD.axes['date']), len(self.D.axes['date'])  )

        print HD.authors

    def test_from_hdf5(self):
        self.D.slice('date', method='time_period', window_size=5)
        HD = to_hdf5(self.D, datapath=self.h5path)

        D_ = from_hdf5(HD)

        self.assertIsInstance(D_, Corpus)

        # Papers should be the same.
        self.assertEqual(   len(HD.papers), len(D_.papers)  )
        
        # Citations should be the same.
        self.assertEqual(   len(HD.citations), len(D_.citations)    )
        self.assertEqual(   len(HD.papers_citing), len(D_.papers_citing)   )
        self.assertEqual(   set(HD.papers_citing.keys()),
                            set(D_.papers_citing.keys())    )
        
        # Authors should be the same.
        self.assertEqual(   len(HD.authors), len(D_.authors)    )
        self.assertEqual(set(HD.authors.keys()), set(D_.authors.keys()))
        for k in D_.authors.keys():
            self.assertTrue(k in HD.authors)

        # Features should be the same.
        self.assertEqual(   len(HD.features['unigrams']['index']),
                            len(D_.features['unigrams']['index'])   )
        self.assertEqual(   len(HD.features['unigrams']['features']),
                            len(D_.features['unigrams']['features'])   )
        self.assertEqual(   len(HD.features['unigrams']['counts']),
                            len(D_.features['unigrams']['counts'])   )
        self.assertEqual(   len(HD.features['unigrams']['documentCounts']),
                            len(D_.features['unigrams']['documentCounts']) )

        # Axes should be the same.
        self.assertEqual(   len(HD.axes), len(D_.axes)  )
        self.assertEqual(   len(HD.axes['date']), len(D_.axes['date'])  )

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()