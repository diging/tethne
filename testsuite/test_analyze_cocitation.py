from settings import *

import unittest

from tethne.readers import wos, dfr
from tethne.classes import Corpus, GraphCollection
from tethne.analyze import cocitation
import networkx
import numpy

class TestCocitationAnalysis(unittest.TestCase):
    def setUp(self):
        wosdatapath = '{0}/wos.txt'.format(datapath)
#        papers = wos.read(wosdatapath)
        papers = wos.from_dir('/Users/erickpeirson/Dropbox/Research/Genecology/wos/')

        self.corpus = Corpus(papers, index_by='ayjid')
        self.corpus.slice('date', method='time_period', window_size=1)
        method_kwargs = {   'threshold':2,
                            'topn':200  }
        self.G = GraphCollection().build(self.corpus, 'date', 'papers', 'cocitation', method_kwargs=method_kwargs)

#    def test_sigma(self):
#        graph = cocitation.sigma(self.G, self.corpus)
#        from tethne.writers import collection
##        collection.to_dxgmml(graph, outpath + '/sigma.xgmml')
##        print graph.graphs.values()[-1].nodes(data=True)
##        fig = graph.plot_attr_distribution('sigma', 'node', numpy.mean)

    def test_plot_sigma(self):
        fig = cocitation.plot_sigma(self.G, self.corpus, topn=5, perslice=True)
        fig.savefig(outpath+'/sigma_plot.png')


if __name__ == '__main__':
    unittest.main()