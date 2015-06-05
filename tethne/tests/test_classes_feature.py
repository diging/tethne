import sys
sys.path.append('./')

import unittest

from tethne.classes.feature import Feature, FeatureSet


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


class TestFeatureSest(unittest.TestCase):
    def test_init_empty(self):
        """
        Initialize with no Features.
        """

        try:
            featureset = FeatureSet()
            featureset.__init__()
        except:
            self.fail()

    def test_init_features(self):
        """
        Initialize with multiple features.
        """
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


if __name__ == '__main__':
    unittest.main()
