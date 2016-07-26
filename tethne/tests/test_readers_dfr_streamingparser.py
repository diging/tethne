import unittest, mock, sys
sys.path.append('../tethne')

from tethne.readers import dfr

datapath = 'tethne/tests/data/dfr'

class TestStreamingParser(unittest.TestCase):
    def test_parse(self):
        parser = dfr.StreamingParser()
        iterator = parser.parse(datapath)
        self.assertTrue(hasattr(iterator, '__iter__'))

    def test_iterate(self):
        parser = dfr.StreamingParser()
        iterator = parser.parse(datapath)
        i = 0
        for identifier, feature_iter in iterator:
            self.assertIsInstance(identifier, str)
            self.assertTrue(hasattr(feature_iter, '__iter__'))
            i += 1
        self.assertEqual(i, 398)

    def test_inner_iterate(self):
        parser = dfr.StreamingParser()
        iterator = parser.parse(datapath)
        i = 0
        for identifier, feature_iter in iterator:
            self.assertIsInstance(identifier, str)
            self.assertTrue(hasattr(feature_iter, '__iter__'))

            for feature, value in feature_iter:
                self.assertIsInstance(feature, unicode)
                self.assertIsInstance(value, float)
                i += 1

        self.assertEqual(i, 536079)


if __name__ == '__main__':
    unittest.main()
