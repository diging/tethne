from settings import *

import unittest

from nltk.corpus import stopwords
import numpy
import os
from networkx import DiGraph

from tethne import Corpus, GraphCollection, HDF5Corpus
from tethne.readers import dfr
from tethne.model.managers import TAPModelManager, MALLETModelManager
from tethne.model import TAPModel
from tethne.networks.authors import coauthors

import cPickle as pickle
picklepath = '{0}/pickles'.format(datapath)

dfrdatapath = '{0}/dfr'.format(datapath)
corpus = dfr.read_corpus(dfrdatapath, ['uni'])
print corpus.features.keys()
corpus.slice('date', 'time_period', window_size=1)
G = GraphCollection().build(corpus, 'date', 'authors', 'coauthors')
L = MALLETModelManager(    corpus, feature='unigrams',
                               outpath=outpath,
                               temppath=temppath,
                               mallet_path=mallet_path  )
L._load_model()

class TestTAPModelManager(unittest.TestCase):
    def setUp(self):
        pcgpath = cg_path + 'model.manager.TAPModelManager.__init__.png'
        with Profile(pcgpath):
            self.M = TAPModelManager(corpus, G, L.model,
                                                outpath=outpath,
                                                temppath=temppath,
                                                mallet_path=mallet_path)

    def test_author_theta(self):
        """
        Should generate an ``a_theta`` matrix for slice ``0`` with shape (3,20).
        """

        s = corpus.get_slices('date').keys()[1]
        papers = corpus.get_slice('date', s, papers=True)
        authors_list = list(set([ a for p in papers for a in p.authors() ]))
        authors = { authors_list[i]:i for i in xrange(len(authors_list)) }
        
        pcgpath = cg_path + 'model.manager.TAPModelManager.author_theta.png'
        with Profile(pcgpath):
            atheta = self.M.author_theta(papers, authors)

        self.assertEqual(len(atheta), 4)
        self.assertIsInstance(atheta, dict)
        self.assertEqual(atheta[0].shape, (20,))

    def test_build_and_graph_collection(self):
        """
        :func:`.build` should generate a set of :class:`.TAPModel` instances.
        """

        pcgpath = cg_path + 'model.manager.TAPModelManager.build.png'
        with Profile(pcgpath):
            self.M.build(axis='date')

        self.assertIsInstance(self.M.SM.values()[0], TAPModel)
        self.assertIsInstance(self.M.SM.values()[0].MU[0], DiGraph)

        pcgpath = cg_path + 'model.manager.TAPModelManager.graph_collection.png'
        with Profile(pcgpath):
            GC = self.M.graph_collection(0)

        testnodes = GC.graphs.values()[0].nodes(data=True)
        
        self.assertIsInstance(GC, GraphCollection)
        self.assertIsInstance(testnodes[0][1]['label'], str)
#
#        with open(picklepath + '/test_TAPModel.pickle', 'w') as f:
#            pickle.dump(self.M.SM.values()[-1], f)

if __name__ == '__main__':
    unittest.main()