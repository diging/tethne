from settings import *

import unittest

from tethne.readers import wos, dfr
from tethne.classes import Corpus
from tethne.classes.corpus import from_hdf5
from tethne.persistence import HDF5Corpus

import numpy

from nltk.corpus import stopwords

class TestPaper(unittest.TestCase):
    pass

class TestAddFeatures(unittest.TestCase):
    def setUp(self):
        """
        Generate a Corpus from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
        self.ngrams = dfr.ngrams(dfrdatapath, 'uni')
        papers = dfr.read(dfrdatapath)

        self.D = Corpus(papers, index_by='doi')

    def test_add_features(self):
        pcgpath = cg_path+ 'classes.Corpus.add_features.png'
        with Profile(pcgpath):
            self.D.add_features('wordcounts', self.ngrams,
                                              exclude=stopwords.words())

        self.assertEqual(len(self.D.features['wordcounts']['index']), 51639)
#
class TestCorpusWoS(unittest.TestCase):
    def setUp(self):
        """
        Genereate a Corpus from some WoS data.
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)
        papers = wos.read(wosdatapath)

        pcgpath = cg_path + 'classes.Corpus.__init__[wos].png'
        with Profile(pcgpath):
            self.D = Corpus(papers, index_by='wosid')

    def test_feature_counts(self):
        filt = lambda s: len(s) > 3
        self.D.slice('date', method='time_period', window_size=1)
        
        # Counts
        result = self.D.feature_counts('citations', 2012, 'date')
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)

        # Document Counts
        result = self.D.feature_counts('citations', 2012, 'date',
                                        documentCounts=True)
        self.assertIsInstance(result, dict)
        self.assertGreater(len(result), 0)


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
        
        pcgpath = cg_path+'classes.Corpus.abstract_to_features[wos].png'
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

        pcgpath = cg_path + 'classes.Corpus.slice[wos].png'
        with Profile(pcgpath):
            self.D.slice('date')

        self.assertIn('date', self.D.axes)
        self.assertIn(2012, self.D.axes['date'])
        self.assertIn(2013, self.D.axes['date'])
        self.assertEqual(len(self.D.axes['date'][2012]), 5)

class TestCorpusDfR(unittest.TestCase):
    def setUp(self):
        """
        Generate a Corpus from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')

        pcgpath = cg_path + 'classes.Corpus.__init__[dfr].png'
        with Profile(pcgpath):
            self.D = Corpus(papers, features={'unigrams': ngrams},
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

class TestCorpusTokenization(unittest.TestCase):

    def setUp(self):
        self.dfrdatapath = '{0}/dfr'.format(datapath)
        self.papers = dfr.read(self.dfrdatapath)
        self.ngrams = dfr.ngrams(self.dfrdatapath, 'uni')


    def test_feature_distribution(self):
        filt = lambda s: len(s) > 3
        D = Corpus(self.papers, features={'unigrams': self.ngrams},
                                        index_by='doi',
                                        exclude=set(stopwords.words()),
                                        filt=filt)

        D.slice('date', 'time_period', window_size=5)
        D.slice('jtitle')
        
        dateshape = len(D.axes['date'].keys())
        jtitleshape = len(D.axes['jtitle'].keys())

        values = D.feature_distribution('unigrams', 'four', 'date',
                                        mode='counts', normed=True)
        self.assertEqual(values.shape, (dateshape,1))
        self.assertGreater(numpy.sum(values), 0)
        
        values = D.feature_distribution('unigrams', 'four', 'date',
                                        mode='counts', normed=False)
        self.assertEqual(values.shape, (dateshape,1))
        self.assertGreater(numpy.sum(values), 0)
        
        values = D.feature_distribution('unigrams', 'four', 'date',
                                        mode='documentCounts', normed=True)
        self.assertEqual(values.shape, (dateshape,1))
        self.assertGreater(numpy.sum(values), 0)
        
        values = D.feature_distribution('unigrams', 'four', 'date',
                                        mode='documentCounts', normed=False)
        self.assertEqual(values.shape, (dateshape,1))
        self.assertGreater(numpy.sum(values), 0)
        
        values = D.feature_distribution('unigrams', 'four', 'date', 'jtitle',
                                        mode='counts', normed=True)
        self.assertEqual(values.shape, (dateshape,jtitleshape))
        self.assertGreater(numpy.sum(values), 0)

        fkwargs = {
            'featureset': 'unigrams',
            'feature': 'four',
            'mode': 'counts',
            'normed': True,
            }

        import matplotlib.pyplot as plt
        fig = D.plot_distribution('date', 'jtitle', mode='features',
                                    fkwargs=fkwargs, interpolation='none')


    def test_tokenize_filter(self):
        """
        Applying a filter should result in a smaller featureset.
        """
        filt = lambda s: len(s) > 3
        
        pcgpath = cg_path+ 'classes.Corpus.__init__[dfr_filter].png'
        with Profile(pcgpath):
            D = Corpus(self.papers, features={'unigrams': self.ngrams},
                                            index_by='doi',
                                            exclude=set(stopwords.words()),
                                            filt=filt)

        self.assertEqual(len(D.features['unigrams']['index']), 49503)

    def test_filter_features(self):
        """
        :func:`Corpus.filterfeatures` should generate a new, more
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
        
        D = Corpus(self.papers, features={'unigrams': self.ngrams},
                                        index_by='doi',
                                        exclude=set(stopwords.words()))
                                        
        k = D.papers.keys()[0]  # Get some paper's key.
        before = [ D.features['unigrams']['index'][g[0]]
                    for g in D.features['unigrams']['features'][k] ]
        
        pcgpath = cg_path + 'classes.Corpus.filter_features[dfr].png'
        with Profile(pcgpath):
            D.filter_features('unigrams', 'unigrams_lim', filt)

        after =  [ D.features['unigrams_lim']['index'][g[0]]
                    for g in D.features['unigrams_lim']['features'][k] ]

        self.assertEqual(len(D.features['unigrams_lim']['index']), 14709)
        self.assertEqual(len(set(after) - set(before)), 0)

if __name__ == '__main__':
    unittest.main()