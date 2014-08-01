from settings import *

import unittest

import warnings

from tethne.readers import wos, dfr
from tethne.classes import Corpus, GraphCollection
from tethne.networks.authors import coauthors
from tethne.persistence.hdf5.util import get_h5file, get_or_create_group
from tethne.persistence.hdf5.graphcollection import HDF5GraphCollection, HDF5Graph
from tethne.persistence.hdf5.ldamodel import HDF5LDAModel
from tethne.persistence.hdf5.tapmodel import HDF5TAPModel
from tethne.persistence.hdf5.dtmmodel import HDF5DTMModel
from tethne.persistence.hdf5.corpus import HDF5Corpus

from tethne.model.corpus import ldamodel, dtmmodel
from tethne.model.social import tapmodel

from tethne import hdf5

import os

import networkx
from scipy.sparse import coo_matrix
import cPickle as pickle
from nltk.corpus import stopwords


dfrdatapath = '{0}/dfr'.format(datapath)
papers = dfr.read(dfrdatapath)

D = Corpus(papers, index_by='doi')
D.slice('date', method='time_period', window_size=1)

with open(picklepath + '/test_TAPModel.pickle', 'r') as f:
    T_ = pickle.load(f)

#class TestGraphCollectionToFromHDF5(unittest.TestCase):
#    def setUp(self):
#        self.h5name = 'HDF5_test.h5'
#        self.h5path = temppath + '/' + self.h5name
#        self.h5file,a,b = get_h5file('GraphCollection', self.h5path)
#
#        self.G_ = GraphCollection()
#
#        for k,v in D.get_slices('date', papers=True).iteritems():
#            self.G_[k] = coauthors(v)
#
#    def test_to_hdf5(self):
#        HG = hdf5.to_hdf5(self.G_, datapath=self.h5path)
#        self.assertIsInstance(HG, HDF5GraphCollection)
#
#        self.assertEqual(HG.graphs.keys(), self.G_.graphs.keys())
#        for key, graph in HG.graphs.iteritems():
#            self.assertEqual(   set(graph.nodes()),
#                                set(self.G_[key].nodes())   )
#            self.assertEqual(   set(graph.edges()),
#                                set(self.G_[key].edges())   )
#
#    def test_from_hdf5_path(self):
#        HG = hdf5.to_hdf5(self.G_, datapath=self.h5path)
#        G = hdf5.from_hdf5(self.h5path)
#    
#        self.assertIsInstance(G, GraphCollection)
#
#        self.assertEqual(HG.graphs.keys(), G.graphs.keys())
#        for key, graph in HG.graphs.iteritems():
#            self.assertEqual(   set(graph.nodes()),
#                                set(G[key].nodes())   )
#            self.assertEqual(   set(graph.edges()),
#                                set(G[key].edges())   )
#
#    def test_from_hdf5_obj(self):
#        HG = hdf5.to_hdf5(self.G_, datapath=self.h5path)
#        G = hdf5.from_hdf5(HG)
#    
#        self.assertIsInstance(G, GraphCollection)
#
#        self.assertEqual(HG.graphs.keys(), G.graphs.keys())
#        for key, graph in HG.graphs.iteritems():
#            self.assertEqual(   set(graph.nodes()),
#                                set(G[key].nodes())   )
#            self.assertEqual(   set(graph.edges()),
#                                set(G[key].edges())   )
#
#    def tearDown(self):
#        os.remove(self.h5path)
#
#class TestLDAModelToFromHDF5(unittest.TestCase):
#    def setUp(self):
#        self.dt_path = '{0}/mallet/dt.dat'.format(datapath)
#        self.wt_path = '{0}/mallet/wt.dat'.format(datapath)
#        self.meta_path = '{0}/mallet/tethne_meta.csv'.format(datapath)
#        self.lmodel = ldamodel.from_mallet(  self.dt_path,
#                                             self.wt_path,
#                                             self.meta_path  )
#    
#        self.h5name = 'test_HDF5LDAModel.h5'
#        self.h5path = temppath+'/'+self.h5name
#        pcgpath = cg_path + 'persistence.hdf5.HDF5LDAModel.__init__.png'
#        with Profile(pcgpath):
#            self.model = HDF5LDAModel(self.lmodel.theta, self.lmodel.phi,
#                                      self.lmodel.metadata,
#                                      self.lmodel.vocabulary,
#                                      datapath=self.h5path)
#                
#        self.assertIn(self.h5name, os.listdir(temppath))
#
#    def test_from_hdf5_object(self):
#        tmodel = hdf5.from_hdf5(self.model)
#    
#        self.assertIsInstance(tmodel, ldamodel.LDAModel)
#        self.assertEqual(tmodel.theta, self.model.theta)
#        self.assertEqual(tmodel.phi, self.model.phi)
#        self.assertEqual(tmodel.metadata, self.model.metadata)
#        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)
#
#    def test_from_hdf5_datapath(self):
#        tmodel = hdf5.from_hdf5(self.model.path)
#        
#        self.assertIsInstance(tmodel, ldamodel.LDAModel)
#        self.assertEqual(tmodel.theta.shape, self.model.theta.shape)
#        self.assertEqual(tmodel.theta[0].all(), self.model.theta[0].all())
#        self.assertEqual(tmodel.phi.shape, self.model.phi.shape)
#        self.assertEqual(tmodel.phi[0].all(), self.model.phi[0].all())
#        self.assertEqual(tmodel.metadata, self.model.metadata)
#        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)
#
#    def test_to_hdf5(self):
#        hmodel = hdf5.to_hdf5(self.lmodel)
#
#        self.assertIsInstance(hmodel, HDF5LDAModel)
#        self.assertEqual(self.lmodel.theta[0].all(), hmodel.theta[0].all())
#        self.assertEqual(self.lmodel.phi[0].all(), hmodel.phi[0].all())
#        self.assertEqual(self.lmodel.metadata, hmodel.metadata)
#        self.assertEqual(self.lmodel.vocabulary, hmodel.vocabulary)
#
#    def tearDown(self):
#        os.remove(self.h5path)
#
#class TestTAPModelToFromHDF5(unittest.TestCase):
#    def setUp(self):
#        self.h5name = 'test_HDF5TAPModel.h5'
#        self.h5path = temppath+'/'+self.h5name
#        self.T = HDF5TAPModel(T_, self.h5path)
#
#    def test_from_hdf5_object(self):
#        tmodel = hdf5.from_hdf5(self.T)
#
#        self.assertIsInstance(tmodel, tapmodel.TAPModel)
#
#        for i in tmodel.a.keys():
#            self.assertEqual(tmodel.a[i].all(), self.T.a[i].all())
#        for i in tmodel.r.keys():
#            self.assertEqual(tmodel.r[i].all(), self.T.r[i].all())
#        for i in tmodel.g.keys():
#            self.assertEqual(tmodel.g[i].all(), self.T.g[i].all())
#        for i in tmodel.b.keys():
#            self.assertEqual(tmodel.b[i].all(), self.T.b[i].all())
#
#        for i in tmodel.theta.keys():
#            self.assertEqual(tmodel.theta[i].all(), self.T.theta[i].all())
#
#        self.assertEqual(tmodel.N_d, self.T.N_d)
#        self.assertIsInstance(tmodel.G, networkx.Graph)
#        self.assertEqual(tmodel.G.nodes(data=True), self.T.G.nodes(data=True))
#        self.assertEqual(tmodel.G.edges(data=True), self.T.G.edges(data=True))
#
#    def test_from_hdf5_datapath(self):
#        tmodel = hdf5.from_hdf5(self.h5path)
#
#        self.assertIsInstance(tmodel, tapmodel.TAPModel)
#
#        for i in tmodel.a.keys():
#            self.assertEqual(tmodel.a[i].all(), self.T.a[i].all())
#        for i in tmodel.r.keys():
#            self.assertEqual(tmodel.r[i].all(), self.T.r[i].all())
#        for i in tmodel.g.keys():
#            self.assertEqual(tmodel.g[i].all(), self.T.g[i].all())
#        for i in tmodel.b.keys():
#            self.assertEqual(tmodel.b[i].all(), self.T.b[i].all())
#        for i in tmodel.theta.keys():
#            self.assertEqual(tmodel.theta[i].all(), self.T.theta[i].all())
#
#        self.assertEqual(tmodel.N_d, self.T.N_d)
#        self.assertIsInstance(tmodel.G, networkx.Graph)
#        self.assertEqual(tmodel.G.nodes(data=True), self.T.G.nodes(data=True))
#        self.assertEqual(tmodel.G.edges(data=True), self.T.G.edges(data=True))
#
#    def test_to_hdf5(self):
#        hmodel = hdf5.to_hdf5(T_)
#
#        self.assertIsInstance(hmodel, HDF5TAPModel)
#        for i in hmodel.a.keys():
#            self.assertEqual(hmodel.a[i].all(), T_.a[i].all())
#        for i in hmodel.r.keys():
#            self.assertEqual(hmodel.r[i].all(), T_.r[i].all())
#        for i in hmodel.g.keys():
#            self.assertEqual(hmodel.g[i].all(), T_.g[i].all())
#        for i in hmodel.b.keys():
#            self.assertEqual(hmodel.b[i].all(), T_.b[i].all())
#        for i in hmodel.theta.keys():
#            self.assertEqual(hmodel.theta[i].all(), T_.theta[i].all())
#        self.assertEqual(hmodel.N_d, T_.N_d)
#        self.assertIsInstance(hmodel.G, HDF5Graph)
#        self.assertEqual(hmodel.G.nodes(data=True), T_.G.nodes(data=True))
#        self.assertEqual(hmodel.G.edges(data=True), T_.G.edges(data=True))
#
#    def test_from_to_hdf5(self):
#        tmodel = hdf5.from_hdf5(self.T)
#        hmodel = hdf5.to_hdf5(tmodel)
#
#        for i in hmodel.a.keys():
#            self.assertEqual(hmodel.a[i].all(), tmodel.a[i].all())
#        for i in hmodel.r.keys():
#            self.assertEqual(hmodel.r[i].all(), tmodel.r[i].all())
#        for i in hmodel.g.keys():
#            self.assertEqual(hmodel.g[i].all(), tmodel.g[i].all())
#        for i in hmodel.b.keys():
#            self.assertEqual(hmodel.b[i].all(), tmodel.b[i].all())
#        for i in hmodel.theta.keys():
#            self.assertEqual(hmodel.theta[i].all(), tmodel.theta[i].all())
#        self.assertEqual(hmodel.N_d, tmodel.N_d)
#        self.assertIsInstance(hmodel.G, HDF5Graph)
#        self.assertEqual(hmodel.G.nodes(data=True), tmodel.G.nodes(data=True))
#        self.assertEqual(hmodel.G.edges(data=True), tmodel.G.edges(data=True))
#
#    def tearDown(self):
#        os.remove(self.h5path)
#
#class TestDTMModelToFromHDF5(unittest.TestCase):
#    def setUp(self):
#        self.meta_path = '{0}/dtm/tethne-meta.dat'.format(datapath)
#        self.vocab_path = '{0}/dtm/tethne-vocab.dat'.format(datapath)
#        self.target_path = '{0}/dtm/model_run'.format(datapath)
#        self.lmodel = dtmmodel.from_gerrish(  self.target_path,
#                                             self.meta_path,
#                                             self.vocab_path )
#    
#        self.h5name = 'test_HDF5DTMModel.h5'
#        self.h5path = temppath+'/'+self.h5name
#        
#        pcgpath = cg_path + 'persistence.hdf5.HDF5DTMModel.__init__.png'
#        with Profile(pcgpath):
#            self.model = HDF5DTMModel(  self.lmodel.e_theta, self.lmodel.phi,
#                                        self.lmodel.metadata,
#                                        self.lmodel.vocabulary,
#                                        datapath=self.h5path  )
#    
#
#
#    def test_from_hdf5_object(self):
#        tmodel = hdf5.from_hdf5(self.model)
#    
#        self.assertIsInstance(tmodel, dtmmodel.DTMModel)
#        self.assertEqual(tmodel.e_theta.all(), self.model.e_theta[0].all())
#        self.assertEqual(tmodel.phi.all(), self.model.phi[0].all())
#        self.assertEqual(tmodel.metadata, self.model.metadata)
#        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)
#
#    def test_from_hdf5_datapath(self):
#        tmodel = hdf5.from_hdf5(self.model.path)
#        
#        self.assertIsInstance(tmodel, dtmmodel.DTMModel)
#        self.assertEqual(tmodel.e_theta.shape, self.model.e_theta.shape)
#        self.assertEqual(tmodel.e_theta[0].all(), self.model.e_theta[0].all())
#        self.assertEqual(tmodel.phi.shape, self.model.phi.shape)
#        self.assertEqual(tmodel.phi[0].all(), self.model.phi[0].all())
#        self.assertEqual(tmodel.metadata, self.model.metadata)
#        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)
#
#    def test_to_hdf5(self):
#        hmodel = hdf5.to_hdf5(self.lmodel)
#
#        self.assertIsInstance(hmodel, HDF5DTMModel)
#        self.assertEqual(self.lmodel.e_theta[0].all(), hmodel.e_theta[0].all())
#        self.assertEqual(self.lmodel.phi[0].all(), hmodel.phi[0].all())
#        self.assertEqual(self.lmodel.metadata, hmodel.metadata)
#        self.assertEqual(self.lmodel.vocabulary, hmodel.vocabulary)
#
#    def test_from_to_hdf5(self):
#        tmodel = hdf5.from_hdf5(self.model)
#        hmodel = hdf5.to_hdf5(tmodel)
#
#        self.assertEqual(tmodel.e_theta[0].all(), hmodel.e_theta[0].all())
#        self.assertEqual(tmodel.phi[0].all(), hmodel.phi[0].all())
#        self.assertEqual(tmodel.metadata, hmodel.metadata)
#        self.assertEqual(tmodel.vocabulary, hmodel.vocabulary)
#
#    def tearDown(self):
#        os.remove(self.h5path)

class TestCorpusToFromHDF5(unittest.TestCase):
    def setUp(self):
        """
        Generate a Corpus from some DfR data with unigrams.
        """
        
        dfrdatapath = '{0}/dfr'.format(datapath)
        self.h5name = 'test_HDF5Corpus.h5'
        self.h5path = temppath+'/'+self.h5name
    
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')

        pcgpath = cg_path + 'classes.Corpus.__init__[dfr].png'
        with Profile(pcgpath):
            self.D = Corpus(papers, features={'unigrams': ngrams},
                                                index_by='doi',
                                                exclude=set(stopwords.words()))

    def test_to_hdf5(self):
        """
        Create a new :class:`.HDF5Corpus` with identical attributes.
        """

        self.D.slice('date', method='time_period', window_size=5)
        HD = hdf5.to_hdf5(self.D, datapath=self.h5path)
        self.assertIsInstance(HD, HDF5Corpus)

        # Papers should be the same.
        self.assertEqual(   len(HD.papers), len(self.D.papers)  )
        
        # Citations should be the same.
        self.assertEqual(   len(HD.citations), len(self.D.citations)    )
        self.assertEqual(   len(HD.papers_citing), len(self.D.papers_citing)   )
        self.assertEqual(   set(HD.papers_citing.keys()),
                            set(self.D.papers_citing.keys())    )
        
        # Authors should be the same.
        self.assertEqual(   len(HD.authors), len(self.D.authors)    )
        self.assertEqual(set(HD.authors.keys()), set(self.D.authors.keys()))
        for k in self.D.authors.keys():
            self.assertTrue(k in HD.authors)

        # Features should be the same.
        self.assertEqual(   len(HD.features['unigrams']['index']),
                            len(self.D.features['unigrams']['index'])   )
        self.assertEqual(   len(HD.features['unigrams']['features']),
                            len(self.D.features['unigrams']['features'])   )
        self.assertEqual(   len(HD.features['unigrams']['counts']),
                            len(self.D.features['unigrams']['counts'])   )
        self.assertEqual(   len(HD.features['unigrams']['documentCounts']),
                            len(self.D.features['unigrams']['documentCounts']) )
        self.assertEqual(   len(HD.features['unigrams']['papers']),
                            len(self.D.features['unigrams']['papers']) )

        # Axes should be the same.
        self.assertEqual(   len(HD.axes), len(self.D.axes)  )
        self.assertEqual(   len(HD.axes['date']), len(self.D.axes['date'])  )

#    def test_from_hdf5(self):
#        self.D.slice('date', method='time_period', window_size=5)
#        HD = hdf5.to_hdf5(self.D, datapath=self.h5path)
#
#        D_ = hdf5.from_hdf5(HD)
#
#        self.assertIsInstance(D_, Corpus)
#
#        # Papers should be the same.
#        self.assertEqual(   len(HD.papers), len(D_.papers)  )
#        
#        # Citations should be the same.
#        self.assertEqual(   len(HD.citations), len(D_.citations)    )
#        self.assertEqual(   len(HD.papers_citing), len(D_.papers_citing)   )
#        self.assertEqual(   set(HD.papers_citing.keys()),
#                            set(D_.papers_citing.keys())    )
#        
#        # Authors should be the same.
#        self.assertEqual(   len(HD.authors), len(D_.authors)    )
#        self.assertEqual(set(HD.authors.keys()), set(D_.authors.keys()))
#        for k in D_.authors.keys():
#            self.assertTrue(k in HD.authors)
#
#        # Features should be the same.
#        self.assertEqual(   len(HD.features['unigrams']['index']),
#                            len(D_.features['unigrams']['index'])   )
#        self.assertEqual(   len(HD.features['unigrams']['features']),
#                            len(D_.features['unigrams']['features'])   )
#        self.assertEqual(   len(HD.features['unigrams']['counts']),
#                            len(D_.features['unigrams']['counts'])   )
#        self.assertEqual(   len(HD.features['unigrams']['documentCounts']),
#                            len(D_.features['unigrams']['documentCounts']) )
#
#        # Axes should be the same.
#        self.assertEqual(   len(HD.axes), len(D_.axes)  )
#        self.assertEqual(   len(HD.axes['date']), len(D_.axes['date'])  )
#
#    def tearDown(self):
#        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()
