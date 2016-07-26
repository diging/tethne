import unittest, mock, sys
sys.path.append('../tethne')

from tethne.classes.streamingfeature import StreamingFeatureSet



class TestStreamingFeature(unittest.TestCase):
    def test_init(self):
        """
        No IO should occur in the constructor.
        """
        mock_feature_iter = mock.MagicMock()
        mock_feature_iter.__iter__.return_value = enumerate(xrange(10))

        mock_parser = mock.Mock(return_value=[('mock', mock_feature_iter)])

        featureset = StreamingFeatureSet('/path/to/nowhere', mock_parser)

        self.assertEqual(mock_parser.call_count, 0)
        self.assertEqual(mock_feature_iter.call_count, 0)

    def test_generate_counts(self):
        """
        :meth:`StreamingFeatureSet._generate_counts` should make a single pass
        over the parser and each feature iterator, updating :prop:`.counts` and
        :prop:`.documentCounts`\.
        """
        mock_feature_iter = mock.MagicMock()
        mock_feature_iter.__iter__.return_value = enumerate(xrange(10))

        mock_parser = mock.Mock(return_value=[('mock', mock_feature_iter)])

        featureset = StreamingFeatureSet('/path/to/nowhere', mock_parser)
        featureset._generate_counts()

        self.assertEqual(mock_parser.call_count, 1)
        self.assertEqual(mock_feature_iter.__iter__.call_count, 1)

        # Zero is falsey, so it won't survive.
        self.assertEqual(len(featureset.counts), 9)
        self.assertEqual(len(featureset.documentCounts), 9)

    def test_getitem(self):
        """
        :meth:`StreamingFeatureSet.__getitem__` should return an iterator. No
        IO occurs until iteration.
        """

        mock_feature_iter = mock.MagicMock()
        mock_feature_iter.__iter__.return_value = enumerate(xrange(10))

        def _stop(*args):
            raise StopIteration()
        mock_feature_iter.next.side_effect = _stop

        mock_parser = mock.Mock(return_value=mock_feature_iter)

        featureset = StreamingFeatureSet('/path/to/nowhere', mock_parser)
        self.assertTrue(hasattr(featureset[0], '__iter__'))

        self.assertEqual(mock_parser.call_count, 0)
        self.assertEqual(mock_feature_iter.__iter__.call_count, 0)

        for i, v in featureset[0]:
            pass

        self.assertEqual(mock_parser.call_count, 1)
        self.assertEqual(mock_feature_iter.next.call_count, 1)

    def test_transform(self):
        """
        :meth:`StreamingFeatureSet.transform` generates a new
        :class:`StreamingFeatureSet`\, but without IO of any kind.
        """

        mock_feature_iter = mock.MagicMock()
        mock_feature_iter.__iter__.return_value = enumerate(xrange(10))

        mock_parser = mock.Mock(return_value=[('mock', mock_feature_iter)])

        featureset = StreamingFeatureSet('/path/to/nowhere', mock_parser)

        new_featureset = featureset.transform(lambda *a: a[1])
        self.assertNotEqual(featureset, new_featureset)
        self.assertIsInstance(new_featureset, StreamingFeatureSet)

        self.assertEqual(mock_feature_iter.call_count, 0)
        self.assertEqual(mock_parser.call_count, 0)

    def test_normalize(self):
        """
        :meth:`StreamingFeatureSet.normalize` generates a new
        :class:`StreamingFeatureSet`\, but without IO of any kind.
        """

        mock_feature_iter = mock.MagicMock()
        mock_feature_iter.__iter__.return_value = enumerate(xrange(10))

        mock_parser = mock.Mock(return_value=[('mock', mock_feature_iter)])

        featureset = StreamingFeatureSet('/path/to/nowhere', mock_parser)

        new_featureset = featureset.normalize(lambda *a: a)
        self.assertNotEqual(featureset, new_featureset)
        self.assertIsInstance(new_featureset, StreamingFeatureSet)

        self.assertEqual(mock_feature_iter.call_count, 0)
        self.assertEqual(mock_parser.call_count, 0)

    def test_with_parser(self):
        from tethne.readers.dfr import StreamingParser
        datapath = 'tethne/tests/data/dfr'
        featureset = StreamingFeatureSet(datapath, StreamingParser().parse)

        featureset._generate_counts()
        self.assertEqual(len(featureset.counts), 105216)
        self.assertEqual(len(featureset.documentCounts), 105216)

class TestWorkflows(unittest.TestCase):
    def test_lda_mallet(self):
        from tethne.readers.dfr import read
        datapath = 'tethne/tests/data/dfr'
        corpus = read(datapath, streaming=True)
        from tethne import LDAModel
        model = LDAModel(corpus, featureset_name='wordcounts')
        model.Z = 20
        model.max_iter = 200
        model.fit()
        self.assertGreater(len(model.phi.features), 0)
        self.assertGreater(len(model.theta.features), 0)

    def test_lda_gensim(self):
        from tethne.readers.dfr import read
        datapath = 'tethne/tests/data/dfr'
        corpus = read(datapath, streaming=True)
        from tethne import GensimLDAModel
        model = GensimLDAModel(corpus, featureset_name='wordcounts')
        model.Z = 20
        model.max_iter = 200
        model.fit()
        self.assertGreater(len(model.phi.features), 0)
        self.assertGreater(len(model.theta.features), 0)

    def test_with_parser(self):
        from tethne.readers.dfr import read
        datapath = '/Users/erickpeirson/Dropbox (ASU)/xml'
        corpus = read(datapath, streaming=True)

        from tethne import LDAModel
        model = LDAModel(corpus, featureset_name='wordcounts')
        model.Z = 20
        model.max_iter = 200
        model.fit()
        print model.list_topics()


if __name__ == '__main__':
    unittest.main()
