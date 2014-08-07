from settings import *
import unittest

import numpy
from tethne.analyze.features import kl_divergence, cosine_distance, cosine_similarity, distance
from tethne.readers import wos, dfr

methods = [
    'braycurtis',
    'canberra',
    'chebyshev',
    'cityblock',
    'correlation',
    'cosine',
    'dice',
    'euclidean',
    'hamming',
    'jaccard',
    'kulsinski',
    'matching',
    'rogerstanimoto',
    'russellrao',
    'sokalmichener',
    'sokalsneath',
    'sqeuclidean',
    'yule'  ]

class TestDistance(unittest.TestCase):
    def test_random_data(self):
        for i in xrange(20):    # Do this a few times to catch oddities.
            a = zip(range(20), numpy.random.randint(0,10,(20)))
            b = zip(range(20), numpy.random.randint(0,10,(20)))
            
            for m in methods:
                result = distance(a, b, m)
                self.assertNotEqual(result, 0.)

                result = distance(a, b, m, smooth=True)
                self.assertNotEqual(result, 0.)

    def test_wos_data(self):
        """
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        corpus = wos.read_corpus(wosdatapath)
        corpus.abstract_to_features()

        p1 = 'WOS:000313867300011'
        p2 = 'WOS:000316281300006'

        vect1 = corpus.features['abstractTerms']['features'][p1]
        vect2 = corpus.features['abstractTerms']['features'][p2]

        for m in methods:
            result = distance(vect1, vect2, m)
            self.assertIsInstance(result, float)

            result = distance(vect1, vect2, m, smooth=True)
            self.assertIsInstance(result, float)

        vect1 = corpus.features['citations']['features'][p1]
        vect2 = corpus.features['citations']['features'][p2]

        for m in methods:
            result = distance(vect1, vect2, m)
            self.assertIsInstance(result, float)

            result = distance(vect1, vect2, m, smooth=True)
            self.assertIsInstance(result, float)

    def test_dfr_data(self):
        from nltk.corpus import stopwords
        
        dfrdatapath = '{0}/dfr'.format(datapath)

        corpus = dfr.read_corpus(dfrdatapath, features=['uni',])
        corpus.filter_features('unigrams', 'u_filt')
        corpus.apply_stoplist('u_filt', 'u_stop', stopwords.words())

        p1 = corpus.papers.keys()[0]
        p2 = corpus.papers.keys()[1]

        vect1 = corpus.features['u_stop']['features'][p1]
        vect2 = corpus.features['u_stop']['features'][p2]

        for m in methods:
            result = distance(vect1, vect2, m)
            self.assertIsInstance(result, float)

            result = distance(vect1, vect2, m, smooth=True)
            self.assertIsInstance(result, float)

class TestKLDivergence(unittest.TestCase):
    def test_random_data(self):
        for i in xrange(20):    # Do this a few times to catch oddities.
            a = zip(range(20), numpy.random.randint(0,10,(20)))
            b = zip(range(20), numpy.random.randint(0,10,(20)))
            
            self.assertIsInstance(kl_divergence(a, b), float)

    def test_wos_data(self):
        """
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        corpus = wos.read_corpus(wosdatapath)
        corpus.abstract_to_features()

        p1 = 'WOS:000313867300011'
        p2 = 'WOS:000316281300006'

        vect1 = corpus.features['abstractTerms']['features'][p1]
        vect2 = corpus.features['abstractTerms']['features'][p2]

        result = kl_divergence(vect1, vect2)
        self.assertEqual(round(result, 3), 7.186)

        vect1 = corpus.features['citations']['features'][p1]
        vect2 = corpus.features['citations']['features'][p2]
        result = kl_divergence(vect1, vect2)
        self.assertEqual(round(result, 1), 6.9)

    def test_dfr_data(self):
        from nltk.corpus import stopwords
        
        dfrdatapath = '{0}/dfr'.format(datapath)

        corpus = dfr.read_corpus(dfrdatapath, features=['uni',])
        corpus.filter_features('unigrams', 'u_filt')
        corpus.apply_stoplist('u_filt', 'u_stop', stopwords.words())

        p1 = corpus.papers.keys()[0]
        p2 = corpus.papers.keys()[1]

        vect1 = corpus.features['u_stop']['features'][p1]
        vect2 = corpus.features['u_stop']['features'][p2]

        result = kl_divergence(vect1, vect2)
        self.assertEqual(round(result, 3), 5.948)


class TestCosineDistance(unittest.TestCase):
    def test_random_data(self):
        for i in xrange(20):    # Do this a few times to catch oddities.
            a = zip(range(20), numpy.random.randint(0,10,(20)))
            b = zip(range(20), numpy.random.randint(0,10,(20)))

            result = cosine_distance(a,b)
            
            self.assertIsInstance(result, float)
            self.assertGreater(result, -0.1)
            self.assertGreater(2.1, result)

    def test_wos_data(self):
        """
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        corpus = wos.read_corpus(wosdatapath)
        corpus.abstract_to_features()

        p1 = 'WOS:000313867300011'
        p2 = 'WOS:000316281300006'

        vect1 = corpus.features['abstractTerms']['features'][p1]
        vect2 = corpus.features['abstractTerms']['features'][p2]

        result = cosine_distance(vect1, vect2)

        self.assertEqual(round(result, 3), 0.993)

        vect1 = corpus.features['citations']['features'][p1]
        vect2 = corpus.features['citations']['features'][p2]
        result = cosine_distance(vect1, vect2)
        self.assertEqual(round(result, 1), 1.0)

    def test_dfr_data(self):
        from nltk.corpus import stopwords
        
        dfrdatapath = '{0}/dfr'.format(datapath)

        corpus = dfr.read_corpus(dfrdatapath, features=['uni',])
        corpus.filter_features('unigrams', 'u_filt')
        corpus.apply_stoplist('u_filt', 'u_stop', stopwords.words())

        p1 = corpus.papers.keys()[0]
        p2 = corpus.papers.keys()[1]

        vect1 = corpus.features['u_stop']['features'][p1]
        vect2 = corpus.features['u_stop']['features'][p2]
        result = cosine_distance(vect1, vect2)
        self.assertEqual(round(result, 3), 0.658)

class TestCosineSimilarity(unittest.TestCase):
    def test_random_data(self):
        for i in xrange(20):    # Do this a few times to catch oddities.
            a = zip(range(20), numpy.random.randint(0,10,(20)))
            b = zip(range(20), numpy.random.randint(0,10,(20)))

            result = cosine_similarity(a,b)
            
            self.assertIsInstance(result, float)
            self.assertGreater(result, -1.1)
            self.assertGreater(1.1, result)

    def test_wos_data(self):
        """
        """
    
        wosdatapath = '{0}/wos.txt'.format(datapath)

        corpus = wos.read_corpus(wosdatapath)
        corpus.abstract_to_features()

        p1 = 'WOS:000313867300011'
        p2 = 'WOS:000316281300006'

        vect1 = corpus.features['abstractTerms']['features'][p1]
        vect2 = corpus.features['abstractTerms']['features'][p2]

        result = cosine_similarity(vect1, vect2)
        self.assertEqual(round(result, 4), 0.0066)

        vect1 = corpus.features['citations']['features'][p1]
        vect2 = corpus.features['citations']['features'][p2]
        result = cosine_similarity(vect1, vect2)
        self.assertEqual(round(result, 1), -0.0)

    def test_dfr_data(self):
        from nltk.corpus import stopwords
        
        dfrdatapath = '{0}/dfr'.format(datapath)

        corpus = dfr.read_corpus(dfrdatapath, features=['uni',])
        corpus.filter_features('unigrams', 'u_filt')
        corpus.apply_stoplist('u_filt', 'u_stop', stopwords.words())

        p1 = corpus.papers.keys()[0]
        p2 = corpus.papers.keys()[1]

        vect1 = corpus.features['u_stop']['features'][p1]
        vect2 = corpus.features['u_stop']['features'][p2]
        result = cosine_similarity(vect1, vect2)
        self.assertEqual(round(result, 2), 0.34)

#        import matplotlib.pyplot as plt
#        
#        kld_cit = []
#        kld_abs = []
#        for i in xrange(10):
#            p_i = corpus.papers.keys()[i]
#
#            cit_vect_i = corpus.features['citations']['features'][p_i]
#            abs_vect_i = corpus.features['abstractTerms']['features'][p_i]
#            
#            for j in xrange(i+1,10):
#                p_j = corpus.papers.keys()[j]
#                
#                cit_vect_j = corpus.features['citations']['features'][p_j]
#                abs_vect_j = corpus.features['abstractTerms']['features'][p_j]
#
#                c = numpy.mean( (   kl_divergence(cit_vect_j, cit_vect_i),
#                                    kl_divergence(cit_vect_i, cit_vect_j)   ) )
#                a = numpy.mean( (   kl_divergence(abs_vect_j, abs_vect_i),
#                                    kl_divergence(abs_vect_i, abs_vect_j)   ) )
#                kld_cit.append(c)
#                kld_abs.append(a)
#
#        fig = plt.figure(figsize=(10,10))
#        plt.plot(kld_cit, kld_abs, 'ro')
#        plt.savefig('/Users/erickpeirson/Desktop/test.png')


if __name__ == '__main__':
    unittest.main()

