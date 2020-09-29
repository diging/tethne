import sys
sys.path.append('./')

import unittest
from tethne import GraphCollection
from tethne.readers.wos import read
from tethne.analyze.corpus import feature_burstness, burstness, sigma

datapath = './tethne/tests/data/wos3.txt'


class TestFeatureBurstness(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.corpus.index('date')
        self.feature_name = self.corpus.top_features('citations', topn=1)[0][0]

    def test_feature_burstness(self):

        B = feature_burstness(self.corpus, 'citations', self.feature_name)

        self.assertIsInstance(B, tuple)
        self.assertEqual(len(B[0]), len(B[1]))

        # Should cover a period no larger than that of the corpus.
        dates = set(B[0]) - set(self.corpus.indices['date'].keys())
        self.assertEqual(len(dates), 0)

        self.assertIsInstance(B[1][0], float)

    def test_feature_burstness_nonorm(self):
        B = feature_burstness(self.corpus, 'citations', self.feature_name,
                              normalize=False)

        self.assertIsInstance(B, tuple)
        self.assertEqual(len(B[0]), len(B[1]))

        # Should cover a period no larger than that of the corpus.
        dates = set(B[0]) - set(self.corpus.indices['date'].keys())
        self.assertEqual(len(dates), 0)

        self.assertIsInstance(B[1][0], float)


class TestBurstness(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.corpus.index('date')

    def test_feature_burstness_(self):
        B = feature_burstness(self.corpus, 'citations', 'BOSSDORF O 2005 OECOLOGIA')


    def test_burstness(self):

        B = burstness(self.corpus, 'citations')

        self.assertEqual(len(B), 20)

        for k, B_ in B.items():
            self.assertIsInstance(B_, tuple)
            self.assertEqual(len(B_[0]), len(B_[1]))
            self.assertGreater(len(B_[0]), 0)


class TestSigma(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath, index_by='wosid')
        self.corpus.index('date')
        self.G = GraphCollection(self.corpus, 'cocitation',
                                 method_kwargs={'min_weight':4})

    def test_sigma(self):
        Sigma = sigma(self.G, self.corpus, 'citations')

        # Updates to the GraphCollection.
        for node, attrs in self.G.nodes(data=True):
            self.assertIn('sigma', attrs)
            for value in attrs['sigma'].values():
                self.assertIsInstance(value, float)

            self.assertIn(node, Sigma)




if __name__ == '__main__':
    unittest.main()
