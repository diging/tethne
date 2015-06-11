import sys
sys.path.append('./')

import unittest
from tethne.classes.feature import Feature, FeatureSet
from tethne.readers.wos import read
from tethne.analyze.features import *

datapath = './tethne/tests/data/wos3.txt'


class TestCosineSimilarity(unittest.TestCase):
    def test_cosine_similarity(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 2), ('brobert', 1)])

        c = cosine_similarity(feature3, feature2)

        self.assertIsInstance(c, float)
        self.assertGreater(c, 0.)

    def test_cosine_similarity_citations(self):
        corpus = read(datapath, index_by='wosid')

        top = corpus.top_features('citations', 1)[0][0]

        P = corpus.features['citations'].papers_containing(top)
        F_a = corpus.features['citations'].features[P[0]]
        F_b = corpus.features['citations'].features[P[1]]

        c = cosine_similarity(F_a, F_b)
        self.assertIsInstance(c, float)
        self.assertGreater(c, 0.)


class TestAngularSimilarity(unittest.TestCase):
    def test_angular_similarity(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 2), ('brobert', 1)])

        c = angular_similarity(feature3, feature2)

        self.assertIsInstance(c, float)
        self.assertGreater(c, 0.)

    def test_angular_similarity_citations(self):
        corpus = read(datapath, index_by='wosid')

        top = corpus.top_features('citations', 1)[0][0]

        P = corpus.features['citations'].papers_containing(top)
        F_a = corpus.features['citations'].features[P[0]]
        F_b = corpus.features['citations'].features[P[1]]

        c = angular_similarity(F_a, F_b)

        self.assertIsInstance(c, float)
        self.assertGreater(c, 0.)


class TestKLDivergence(unittest.TestCase):
    def test_kl_divergence(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 2), ('brobert', 1)])
        featureset = FeatureSet()
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        V_a = featureset.as_vector('p2')
        V_b = featureset.as_vector('p3')
        k = kl_divergence(V_a, V_b)

        self.assertIsInstance(k, float)
        self.assertGreater(k, 0.)

    def test_kl_divergence_citations(self):
        corpus = read(datapath, index_by='wosid')

        top = corpus.top_features('citations', 1)[0][0]

        P = corpus.features['citations'].papers_containing(top)
        V_a = corpus.features['citations'].as_vector(P[0])
        V_b = corpus.features['citations'].as_vector(P[1])

        k = kl_divergence(V_a, V_b)

        self.assertIsInstance(k, float)
        self.assertGreater(k, 0.)


class TestEuclidean(unittest.TestCase):
    def test_euclidean(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 2), ('brobert', 1)])
        featureset = FeatureSet()
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        V_a = featureset.as_vector('p2')
        V_b = featureset.as_vector('p3')
        k = distance(V_a, V_b, 'euclidean')

        self.assertIsInstance(k, float)
        self.assertGreater(k, 0.)

    def test_euclidean_citations(self):
        corpus = read(datapath, index_by='wosid')

        top = corpus.top_features('citations', 1)[0][0]

        P = corpus.features['citations'].papers_containing(top)
        V_a = corpus.features['citations'].as_vector(P[0])
        V_b = corpus.features['citations'].as_vector(P[1])

        k = distance(V_a, V_b, 'euclidean')

        self.assertIsInstance(k, float)
        self.assertGreater(k, 0.)


if __name__ == '__main__':
    unittest.main()