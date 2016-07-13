import unittest, tempfile, os, csv, sys, logging
from xml.etree import ElementTree as ET
import networkx as nx

sys.path.append('../tethne')

from tethne.readers.wos import read
from tethne import FeatureSet, tokenize
from tethne.networks import topics

datapath = './tethne/tests/data/wos3.txt'
logger = logging.getLogger('gensim')
logger.setLevel('DEBUG')


class TestLDAModelExistingOutput(unittest.TestCase):
    def setUp(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        self.corpus = read(datapath, index_by='wosid')
        self.corpus.index_feature('abstract', tokenize, structured=True)
        self.old_model = GensimLDAModel(self.corpus, featureset_name='abstract')
        self.old_model.fit(Z=20)

    def test_gensim_to_theta_featureset(self):
        from tethne import gensim_to_theta_featureset
        theta = gensim_to_theta_featureset(self.old_model.model,
                                           self.old_model.gcorpus,
                                           self.old_model.featureset.features.keys())
        self.assertIsInstance(theta, FeatureSet)
        self.assertEqual(len(theta), len(self.corpus.features['abstract'].features))

    def test_gensim_to_phi_featureset(self):
        from tethne import gensim_to_phi_featureset
        phi = gensim_to_phi_featureset(self.old_model.model)
        self.assertIsInstance(phi, FeatureSet)
        self.assertEqual(len(phi), 20)


class TestLDAModelExistingOutput(unittest.TestCase):
    def setUp(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        self.corpus = read(datapath, index_by='wosid')
        self.corpus.index_feature('abstract', tokenize, structured=True)
        self.old_model = GensimLDAModel(self.corpus, featureset_name='abstract')
        self.old_model.fit(Z=20)

    def test_load_existing_data(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        new_model = GensimLDAModel.from_gensim(self.old_model.model,
                                               self.old_model.gcorpus,
                                               self.corpus,
                                               'abstract')

        # For some reason gensim has some slippage at high precision. We should
        #  investigate this further (TODO).
        for o, n in zip(self.old_model.topics_in(u'WOS:000295037200001'),
                         new_model.topics_in(u'WOS:000295037200001')):
            self.assertEqual(o[0], n[0])
            self.assertLess(abs(n[1] - o[1]), 0.001)


class TestLDAModel(unittest.TestCase):
    def setUp(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        corpus = read(datapath, index_by='wosid')
        corpus.index_feature('abstract', tokenize, structured=True)
        self.model = GensimLDAModel(corpus, featureset_name='abstract')
        self.model.fit(Z=20)

    def test_ldamodel(self):
        R = 0.
        for k in xrange(20):
            dates, rep = self.model.corpus.feature_distribution('topics', k)
            R += sum(rep)

        self.assertGreater(R, 0)
        self.assertEqual(len(dates), len(rep))

        self.assertIsInstance(self.model.phi, FeatureSet)
        self.assertIsInstance(self.model.theta, FeatureSet)

        self.assertIsInstance(self.model.list_topics(), list)
        self.assertGreater(len(self.model.list_topics()), 0)
        self.assertIsInstance(self.model.list_topic(0), list)
        self.assertGreater(len(self.model.list_topic(0)), 0)

    def test_networks(self):
        termGraph = topics.terms(self.model)
        self.assertGreater(termGraph.size(), 30)
        self.assertGreater(termGraph.order(), 1)

        topicGraph = topics.cotopics(self.model)
        self.assertGreater(topicGraph.size(), 5)
        self.assertGreater(topicGraph.order(), 0)

        paperGraph = topics.topic_coupling(self.model)
        self.assertGreater(paperGraph.size(), 44)
        self.assertGreater(paperGraph.order(), 1)


class TestLDAModelUnstructured(unittest.TestCase):
    def setUp(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        corpus = read(datapath, index_by='wosid')
        corpus.index_feature('abstract', tokenize)
        self.model = GensimLDAModel(corpus, featureset_name='abstract')
        self.model.fit(Z=20)

    def test_ldamodel(self):
        R = 0.
        for k in xrange(20):
            dates, rep = self.model.corpus.feature_distribution('topics', k)
            R += sum(rep)

        self.assertGreater(R, 0)
        self.assertEqual(len(dates), len(rep))

        self.assertIsInstance(self.model.phi, FeatureSet)
        self.assertIsInstance(self.model.theta, FeatureSet)

        self.assertIsInstance(self.model.list_topics(), list)
        self.assertGreater(len(self.model.list_topics()), 0)
        self.assertIsInstance(self.model.list_topic(0), list)
        self.assertGreater(len(self.model.list_topic(0)), 0)

    def test_networks(self):
        termGraph = topics.terms(self.model)
        self.assertGreater(termGraph.size(), 5)
        self.assertGreater(termGraph.order(), 0)

        topicGraph = topics.cotopics(self.model)
        self.assertGreater(topicGraph.size(), 5)
        self.assertGreater(topicGraph.order(), 0)

        paperGraph = topics.topic_coupling(self.model)
        self.assertGreater(paperGraph.size(), 5)
        self.assertGreater(paperGraph.order(), 0)


class TestLDAModelWithTransformation(unittest.TestCase):
    def setUp(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        corpus = read(datapath, index_by='wosid')
        corpus.index_feature('abstract', tokenize)

        xf = lambda f, c, C, DC: c*3
        corpus.features['xf'] = corpus.features['abstract'].transform(xf)
        self.model = GensimLDAModel(corpus, featureset_name='xf')
        self.model.fit(Z=20)

    def test_ldamodel(self):
        R = 0.
        for k in xrange(20):
            dates, rep = self.model.corpus.feature_distribution('topics', k)
            R += sum(rep)

        self.assertGreater(R, 0)
        self.assertEqual(len(dates), len(rep))

        self.assertIsInstance(self.model.phi, FeatureSet)
        self.assertIsInstance(self.model.theta, FeatureSet)

        self.assertIsInstance(self.model.list_topics(), list)
        self.assertGreater(len(self.model.list_topics()), 0)
        self.assertIsInstance(self.model.list_topic(0), list)
        self.assertGreater(len(self.model.list_topic(0)), 0)

    def test_networks(self):
        termGraph = topics.terms(self.model)
        self.assertGreater(termGraph.size(), 10)
        self.assertGreater(termGraph.order(), 0)

        topicGraph = topics.cotopics(self.model)
        self.assertGreater(topicGraph.size(), 5)
        self.assertGreater(topicGraph.order(), 0)

        paperGraph = topics.topic_coupling(self.model)
        self.assertGreater(paperGraph.size(), 10)
        self.assertGreater(paperGraph.order(), 0)


class TestLDAModelMALLETPath(unittest.TestCase):
    def test_direct_import(self):
        from tethne.model.corpus.gensim_lda import GensimLDAModel
        corpus = read(datapath, index_by='wosid')
        corpus.index_feature('abstract', tokenize, structured=True)
        self.model = GensimLDAModel(corpus, featureset_name='abstract')
        self.model.fit(Z=20)


if __name__ == '__main__':
    unittest.main()
