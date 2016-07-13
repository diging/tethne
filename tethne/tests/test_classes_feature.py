import sys
sys.path.append('./')

import unittest

from tethne.classes.feature import Feature, FeatureSet

import logging
logger = logging.getLogger('feature')
logger.setLevel('ERROR')


class TestFeature(unittest.TestCase):
    def test_init_datum(self):
        """
        Initialize with a single token.
        """
        feature = Feature('bob')

        self.assertEqual(len(feature), 1)
        self.assertEqual(feature[0], ('bob', 1))

    def test_init_list(self):
        """
        Initialize with a list of tokens.
        """
        feature = Feature(['bob', 'joe', 'bob', 'bobert', 'bob'])

        self.assertEqual(len(feature), 3)
        self.assertEqual(dict(feature)['bob'], 3)
        self.assertEqual(dict(feature)['joe'], 1)

    def test_init_counts(self):
        """
        Initialize with a list of 2-tuple token values.
        """
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])

        self.assertEqual(len(feature), 3)
        self.assertEqual(dict(feature)['bob'], 3)
        self.assertEqual(dict(feature)['joe'], 1)

    def test_init_tuples(self):
        feature = Feature([('bob', 'dole'), ('roy', 'snaydon')])

        self.assertEqual(len(feature), 2)
        self.assertEqual(dict(feature)[('bob', 'dole')], 1)

    def test_norm(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        T = sum(list(zip(*feature))[1])
        for n, r in zip(list(zip(*feature.norm))[1], list(zip(*feature))[1]):
            self.assertEqual(n, float(r)/T)

    def test_extend(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])

        feature.extend([('bob', 1)])
        self.assertEqual(feature.value('bob'), 4)

        feature.extend(['bob'])
        self.assertEqual(feature.value('bob'), 5)

        feature.extend('bob')
        self.assertEqual(feature.value('bob'), 6)


    def test_iadd(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])

        feature += [('bob', 1)]
        self.assertEqual(feature.value('bob'), 4)

        feature += ['bob']
        self.assertEqual(feature.value('bob'), 5)

        feature += 'bob'
        self.assertEqual(feature.value('bob'), 6)

    def test_isub(self):
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])

        feature -= [('bob', 1)]
        self.assertEqual(feature.value('bob'), 2)

        feature -= ['bob']
        self.assertEqual(feature.value('bob'), 1)

        feature -= 'bob'
        self.assertEqual(feature.value('bob'), 0)


class TestFeatureSet(unittest.TestCase):
    def test_end_to_end_raw(self):
        """
        Runs the Gensim LDA workflow
        (https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation).
        """
        from tethne.readers.wos import read
        corpus = read('./tethne/tests/data/wos3.txt')
        from nltk.tokenize import word_tokenize
        corpus.index_feature('abstract', word_tokenize)

        gensim_corpus, _ = corpus.features['abstract'].to_gensim_corpus(raw=True)
        from gensim import corpora, models

        dictionary = corpora.Dictionary(gensim_corpus)
        corpus = [dictionary.doc2bow(text) for text in gensim_corpus]
        model = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
                                         num_topics=5, update_every=1,
                                         chunksize=100, passes=1)
        model.print_topics()

    def test_end_to_end(self):
        """
        Runs the Gensim LDA workflow
        (https://radimrehurek.com/gensim/wiki.html#latent-dirichlet-allocation).
        """
        from tethne.readers.wos import read
        corpus = read('./tethne/tests/data/wos3.txt')
        from nltk.tokenize import word_tokenize
        corpus.index_feature('abstract', word_tokenize)

        gensim_corpus, id2word = corpus.features['abstract'].to_gensim_corpus()
        from gensim import models

        model = models.ldamodel.LdaModel(corpus=gensim_corpus, id2word=id2word,
                                         num_topics=5, update_every=1,
                                         chunksize=100, passes=1)
        model.print_topics()

    def test_init_empty(self):
        """
        Initialize with no Features.
        """

        logger.debug('FeatureSet should have 0 Features')
        try:
            featureset = FeatureSet()
            featureset.__init__()
        except:
            self.fail()

    def test_empty_feature(self):
        feature1 = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([])
        try:
            featureset = FeatureSet({'p1': feature1, 'p2': feature2})
        except Exception as E:
            self.fail(E.message)

    def test_init_features(self):
        """
        Initialize with multiple features.
        """

        logger.debug('FeatureSet should have 2 Features')
        feature1 = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('bob', 3), ('jane', 1), ('fido', 1)])
        featureset = FeatureSet({'p1': feature1, 'p2': feature2})

        self.assertEqual(len(featureset.features), 2)

        expected = len(feature1.unique | feature2.unique)

        self.assertEqual(len(featureset.index), expected)
        self.assertEqual(len(featureset.lookup), expected)
        self.assertEqual(len(featureset.counts), expected)
        self.assertEqual(len(featureset.documentCounts), expected)
        self.assertEqual(len(featureset.unique), expected)

        self.assertEqual(featureset.documentCount('bob'), 2)

        self.assertEqual(featureset.count('bob'), 6)

        self.assertIn('p1', featureset.papers_containing('bob'))
        self.assertIn('p2', featureset.papers_containing('bob'))

    def test_transform(self):
        """

        """

        feature1 = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('bob', 3), ('jane', 1), ('fido', 1)])
        featureset = FeatureSet({'p1': feature1, 'p2': feature2})

        featureset_transformed = featureset.transform(lambda f, c, C, DC: c*3)

        self.assertEqual(len(featureset_transformed.features), 2)

        expected = len(featureset_transformed.unique | feature2.unique)

        self.assertEqual(len(featureset_transformed.index), expected)
        self.assertEqual(len(featureset_transformed.lookup), expected)
        self.assertEqual(len(featureset_transformed.counts), expected)
        self.assertEqual(len(featureset_transformed.documentCounts), expected)
        self.assertEqual(len(featureset_transformed.unique), expected)

        self.assertEqual(featureset_transformed.documentCount('bob'), 2)

        self.assertEqual(featureset_transformed.count('bob'), 18)

        self.assertIn('p1', featureset_transformed.papers_containing('bob'))
        self.assertIn('p2', featureset_transformed.papers_containing('bob'))

    def test_add_feature(self):
        """
        Initialize empty, then add a feature.
        """

        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        featureset.add('p1', feature)

        self.assertEqual(len(featureset.features), 1)

        expected = len(feature.unique)

        self.assertEqual(len(featureset.index), expected)
        self.assertEqual(len(featureset.lookup), expected)
        self.assertEqual(len(featureset.counts), expected)
        self.assertEqual(len(featureset.documentCounts), expected)
        self.assertEqual(len(featureset.unique), expected)

        self.assertIn('p1', featureset.papers_containing('bob'))

        self.assertEqual(featureset.documentCount('bob'), 1)
        self.assertEqual(featureset.count('bob'), 3)

        # Do it again! There was some weirdness with the FeatureSet constructor.
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        featureset.add('p1', feature)

        self.assertEqual(len(featureset.features), 1)

        expected = len(feature.unique)

        self.assertEqual(len(featureset.index), expected)
        self.assertEqual(len(featureset.lookup), expected)
        self.assertEqual(len(featureset.counts), expected)
        self.assertEqual(len(featureset.documentCounts), expected)
        self.assertEqual(len(featureset.unique), expected)

        self.assertIn('p1', featureset.papers_containing('bob'))

        self.assertEqual(featureset.documentCount('bob'), 1)
        self.assertEqual(featureset.count('bob'), 3)

    def test_top(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        N = 3
        top = featureset.top(N)
        self.assertIsInstance(top, list)
        self.assertIsInstance(top[0], tuple)
        self.assertEqual(len(top), N)
        self.assertSetEqual(set(list(zip(*top))[0]), set(['blob', 'bob', 'joe']))

        top = featureset.top(N, by='documentCounts')
        self.assertIsInstance(top, list)
        self.assertIsInstance(top[0], tuple)
        self.assertEqual(len(top), N)
        self.assertSetEqual(set(list(zip(*top))[0]), set(['blob', 'brobert', 'joe']))

    def test_as_matrix(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        M = featureset.as_matrix()
        self.assertEqual(len(M), len(featureset))
        self.assertEqual(len(M[0]), len(featureset.unique))

    def test_as_vector(self):
        featureset = FeatureSet()
        feature = Feature([('bob', 3), ('joe', 1), ('bobert', 1)])
        feature2 = Feature([('blob', 3), ('joe', 1), ('brobert', 1)])
        feature3 = Feature([('blob', 1), ('joe', 1), ('brobert', 1)])
        featureset.add('p1', feature)
        featureset.add('p2', feature2)
        featureset.add('p3', feature3)

        v = featureset.as_vector('p1')
        v_norm = featureset.as_vector('p1', norm=True)

        self.assertIsInstance(v, list)
        self.assertIsInstance(v_norm, list)
        self.assertEqual(len(v), len(v_norm))
        self.assertEqual(len(v), len(featureset.unique))
        self.assertGreater(sum(v), 0)
        self.assertGreater(sum(v_norm), 0)
        self.assertEqual(sum(v_norm), 1.0)


if __name__ == '__main__':
    unittest.main()
