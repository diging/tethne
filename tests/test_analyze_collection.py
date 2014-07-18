from settings import *

import unittest

from tethne.readers import wos, dfr
from tethne.classes import Corpus
from tethne.analyze.corpus import feature_burstness, _top_features, burstness, \
                                  plot_burstness

class TestBurstness(unittest.TestCase):
    def setUp(self):
        wosdatapath = '{0}/wos.txt'.format(datapath)
        papers = wos.read(wosdatapath)

        self.corpus = Corpus(papers, index_by='ayjid')
        self.corpus.slice('date', method='time_period', window_size=1)
        self.corpus.abstract_to_features()

    def test_top_citations(self):
        result = _top_features(self.corpus, 'citations')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 20)

    def test_top_words(self):
        result = _top_features(self.corpus, 'abstractTerms')
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 20)

    def test_feature_burstness(self):
        result = feature_burstness(self.corpus, 'abstractTerms', 44)
        self.assertIsInstance(result, tuple)
        self.assertIsInstance(result[0], list)
        self.assertGreater(sum(result[1]), 0.)

    def test_burstness(self):
        result = burstness(self.corpus, 'abstractTerms')
        self.assertIsInstance(result, dict)
        self.assertIsInstance(result.values()[0], tuple)
        self.assertIsInstance(result.values()[0][0], list)
        self.assertIsInstance(result.keys()[0], str)

    def test_burstness_flist(self):
        flist = ['process', 'method']
        result = burstness( self.corpus, 'abstractTerms',
                            flist=flist )
        self.assertIsInstance(result, dict)
        self.assertEqual(flist, result.keys())
        self.assertGreater(len(result), 0)

    def test_plot_burstness(self):
        import matplotlib
        result = plot_burstness(self.corpus, 'citations', topn=2, perslice=True)
        self.assertIsInstance(result, matplotlib.figure.Figure)


if __name__ == '__main__':
    unittest.main()