from settings import *

import unittest

from tethne.model.social import tapmodel
from tethne.persistence.hdf5.tapmodel import HDF5TAPModel, from_hdf5, to_hdf5
from tethne.persistence.hdf5.graphcollection import HDF5Graph

import numpy
import networkx
import os
import cPickle as pickle

with open(picklepath + '/test_TAPModel.pickle', 'r') as f:
    T_ = pickle.load(f)

class TestH5F5TAPModel(unittest.TestCase):
    def setUp(self):
        self.h5name = 'test_HDF5TAPModel.h5'
        self.h5path = temppath+'/'+self.h5name
        self.T = HDF5TAPModel(T_, self.h5path)
    
    def test_test(self):
        for i in T_.theta.keys():
            self.assertGreater(1e-07, abs(self.T.theta[i][0]-T_.theta[i][0]))
        for i in T_.a.keys():
            self.assertGreater(1e-07, abs(self.T.a[i][0][0]-T_.a[i][0][0]))
        for i in T_.b.keys():
            self.assertGreater(1e-07, abs(self.T.b[i][0][0]-T_.b[i][0][0]))
        for i in T_.r.keys():
            self.assertGreater(1e-07, abs(self.T.r[i][0][0]-T_.r[i][0][0]))
        for i in T_.g.keys():
            self.assertGreater(1e-07, abs(self.T.g[i][0][0]-T_.g[i][0][0]))

    def test_from_hdf5_object(self):
        tmodel = from_hdf5(self.T)

        self.assertIsInstance(tmodel, tapmodel.TAPModel)

        for i in xrange(len(tmodel.a)):
            self.assertEqual(tmodel.a[i].all(), self.T.a[i].all())
        for i in xrange(len(tmodel.r)):
            self.assertEqual(tmodel.r[i].all(), self.T.r[i].all())
        for i in xrange(len(tmodel.g)):
            self.assertEqual(tmodel.g[i].all(), self.T.g[i].all())
        for i in xrange(len(tmodel.b)):
            self.assertEqual(tmodel.b[i].all(), self.T.b[i].all())

        for i in xrange(len(tmodel.theta)):
            self.assertEqual(tmodel.theta[i].all(), self.T.theta[i].all())

        self.assertEqual(tmodel.N_d, self.T.N_d)
        self.assertIsInstance(tmodel.G, networkx.Graph)
        self.assertEqual(tmodel.G.nodes(data=True), self.T.G.nodes(data=True))
        self.assertEqual(tmodel.G.edges(data=True), self.T.G.edges(data=True))

    def test_from_hdf5_datapath(self):
        tmodel = from_hdf5(self.h5path)

        self.assertIsInstance(tmodel, tapmodel.TAPModel)

        for i in xrange(len(tmodel.a)):
            self.assertEqual(tmodel.a[i].all(), self.T.a[i].all())
        for i in xrange(len(tmodel.r)):
            self.assertEqual(tmodel.r[i].all(), self.T.r[i].all())
        for i in xrange(len(tmodel.g)):
            self.assertEqual(tmodel.g[i].all(), self.T.g[i].all())
        for i in xrange(len(tmodel.b)):
            self.assertEqual(tmodel.b[i].all(), self.T.b[i].all())

        for i in xrange(len(tmodel.theta)):
            self.assertEqual(tmodel.theta[i].all(), self.T.theta[i].all())

        self.assertEqual(tmodel.N_d, self.T.N_d)
        self.assertIsInstance(tmodel.G, networkx.Graph)
        self.assertEqual(tmodel.G.nodes(data=True), self.T.G.nodes(data=True))
        self.assertEqual(tmodel.G.edges(data=True), self.T.G.edges(data=True))

    def test_to_hdf5(self):
        hmodel = to_hdf5(T_)

        self.assertIsInstance(hmodel, HDF5TAPModel)
        for i in xrange(len(hmodel.a)):
            self.assertEqual(hmodel.a[i].all(), T_.a[i].all())
        for i in xrange(len(hmodel.r)):
            self.assertEqual(hmodel.r[i].all(), T_.r[i].all())
        for i in xrange(len(hmodel.g)):
            self.assertEqual(hmodel.g[i].all(), T_.g[i].all())
        for i in xrange(len(hmodel.b)):
            self.assertEqual(hmodel.b[i].all(), T_.b[i].all())
        for i in xrange(len(hmodel.theta)):
            self.assertEqual(hmodel.theta[i].all(), T_.theta[i].all())
        self.assertEqual(hmodel.N_d, T_.N_d)
        self.assertIsInstance(hmodel.G, HDF5Graph)
        self.assertEqual(hmodel.G.nodes(data=True), T_.G.nodes(data=True))
        self.assertEqual(hmodel.G.edges(data=True), T_.G.edges(data=True))

    def test_from_to_hdf5(self):
        tmodel = from_hdf5(self.T)
        hmodel = to_hdf5(tmodel)

        for i in xrange(len(hmodel.a)):
            self.assertEqual(hmodel.a[i].all(), tmodel.a[i].all())
        for i in xrange(len(hmodel.r)):
            self.assertEqual(hmodel.r[i].all(), tmodel.r[i].all())
        for i in xrange(len(hmodel.g)):
            self.assertEqual(hmodel.g[i].all(), tmodel.g[i].all())
        for i in xrange(len(hmodel.b)):
            self.assertEqual(hmodel.b[i].all(), tmodel.b[i].all())
        for i in xrange(len(hmodel.theta)):
            self.assertEqual(hmodel.theta[i].all(), tmodel.theta[i].all())
        self.assertEqual(hmodel.N_d, tmodel.N_d)
        self.assertIsInstance(hmodel.G, HDF5Graph)
        self.assertEqual(hmodel.G.nodes(data=True), tmodel.G.nodes(data=True))
        self.assertEqual(hmodel.G.edges(data=True), tmodel.G.edges(data=True))

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()