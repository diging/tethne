from settings import *

import unittest

from tethne.readers import wos, dfr
from tethne.classes import Corpus, GraphCollection
from tethne.analyze.corpus import plot_sigma, sigma
import networkx
import numpy

wosdatapath = '{0}/wos.txt'.format(datapath)
papers = wos.from_dir('/Users/erickpeirson/tethne/tests/data/wos_large')

corpus = Corpus(papers, index_by='ayjid')
corpus.slice('date', method='time_period', window_size=2)
method_kwargs = {   'threshold':2,
                    'topn':100  }
G = GraphCollection().build(corpus, 'date', 'papers', 'cocitation',
                                    method_kwargs=method_kwargs)

class TestCocitationAnalysis(unittest.TestCase):
    def setUp(self):
        self.G = G
        self.corpus = corpus

    def test_sigma(self):
        G_ = sigma(self.G, self.corpus, 'citations')
        self.assertIsInstance(G_, GraphCollection)
        
        node = G.graphs.values()[-1].nodes(data=True)[0]
        self.assertIn('sigma', node[1].keys())

    def test_plot_sigma(self):
        import matplotlib
        fig, G_ = plot_sigma( self.G, self.corpus, 'citations',
                                         topn=2, perslice=True   )
        self.assertIsInstance(fig, matplotlib.figure.Figure)
        self.assertIsInstance(G_, GraphCollection)
        
        node = G_.graphs.values()[-1].nodes(data=True)[0]
        self.assertIn('sigma', node[1].keys())        



if __name__ == '__main__':
    unittest.main()