# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput
cg_path = './callgraphs/'

import unittest

import sys
sys.path.append('../../')

from nltk.corpus import stopwords
import numpy
import os
from networkx import DiGraph

from tethne import DataCollection, GraphCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import TAPModelManager, MALLETModelManager
from tethne.model import TAPModel
from tethne.networks.authors import coauthors

import logging
logging.basicConfig()
#logger = logging.getLogger('tethne.classes.datacollection')
#logger.setLevel('ERROR')

class TestTAPModelManager(unittest.TestCase):
    def setUp(self):
        dfrdatapath = '{0}/dfr'.format(datapath)
        
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')
        self.D = DataCollection(papers, features={'unigrams': ngrams},
                                        index_by='doi',
                                        exclude=set(stopwords.words()))
        self.D.slice('date', 'time_period', window_size=10)
        
        # Coauthor graph.
        self.G = GraphCollection()
        for k,v in self.D.get_slices('date', include_papers=True).iteritems():
            self.G[k] = coauthors(v)
        
        # LDAModel
        self.L = MALLETModelManager(self.D, outpath=outpath,
                                            temppath=temppath,
                                            mallet_path=mallet_path)
        self.L._load_model()
        
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.TAPModelManager.__init__.png')):
            self.M = TAPModelManager(self.D, self.G, self.L.model, outpath=outpath,
                                                                    temppath=temppath,
                                                                    mallet_path=mallet_path)

    def test_author_theta(self):
        """
        Should generate an ``a_theta`` matrix for slice ``0`` with shape (3,20).
        """

        s = self.D.get_slices('date').keys()[0]
        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.TAPModelManager.author_theta.png')):
            atheta = self.M.author_theta(
                        self.D.get_slice('date', s, include_papers=True))

        self.assertEqual(atheta.shape, (3,20))

    def test_build_and_graph_collection(self):
        """
        :func:`.build` should generate a set of :class:`.TAPModel` instances.
        :func:`.graph_collection` should generate a :class:`.GraphCollection`\.
        """

        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.TAPModelManager.build.png')):
            self.M.build(axis='date')

        self.assertIsInstance(self.M.SM.values()[0], TAPModel)
        self.assertIsInstance(self.M.SM.values()[0].MU[0], DiGraph)

        with PyCallGraph(output=GraphvizOutput(
                output_file=cg_path + 'model.manager.TAPModelManager.graph_collection.png')):

            GC = self.M.graph_collection(0)

        self.assertIsInstance(GC, GraphCollection)

if __name__ == '__main__':
    datapath = './data'
    temppath = './sandbox/temp'
    outpath = './sandbox/out'
    mallet_path = '/Applications/mallet-2.0.7'
    unittest.main()