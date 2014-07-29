from settings import *

import unittest

from tethne.model.social import tapmodel
from tethne.persistence.hdf5 import HDF5TAPModel, from_hdf5, to_hdf5

import numpy
import os
import cPickle as pickle

with open(picklepath + '/test_TAPModel.pickle', 'r') as f:
    T_ = pickle.load(f)

class TestH5F5TAPModel(unittest.TestCase):
    def setUp(self):
        self.h5name = 'test_HDF5TAPModel.h5'
        self.h5path = temppath+'/'+self.h5name
        self.T = HDF5TAPModel(T_, self.h5path)
    
#    def test_test(self):
#        for i in T_.theta.keys():
#            self.assertGreater(1e-07, abs(self.T.theta[i][0]-T_.theta[i][0]))
#        for i in T_.a.keys():
#            self.assertGreater(1e-07, abs(self.T.a[i][0][0]-T_.a[i][0][0]))
#        for i in T_.b.keys():
#            self.assertGreater(1e-07, abs(self.T.b[i][0][0]-T_.b[i][0][0]))
#        for i in T_.r.keys():
#            self.assertGreater(1e-07, abs(self.T.r[i][0][0]-T_.r[i][0][0]))
#        for i in T_.g.keys():
#            self.assertGreater(1e-07, abs(self.T.g[i][0][0]-T_.g[i][0][0]))
#
    def test_from_hdf5_object(self):
        tmodel = from_hdf5(self.model)
    
        self.assertIsInstance(tmodel, tapmodel.TAPModel)
        self.assertEqual(tmodel.e_theta, self.model.e_theta)
        self.assertEqual(tmodel.phi, self.model.phi)
        self.assertEqual(tmodel.metadata, self.model.metadata)
        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)
#
#    def test_from_hdf5_datapath(self):
#        tmodel = from_hdf5(self.model.path)
#        self.assertIsInstance(tmodel, dtmmodel.DTMModel)
#        self.assertEqual(tmodel.e_theta.shape, self.model.e_theta.shape)
#        self.assertEqual(tmodel.e_theta[0].all(), self.model.e_theta[0].all())
#        self.assertEqual(tmodel.phi.shape, self.model.phi.shape)
#        self.assertEqual(tmodel.phi[0].all(), self.model.phi[0].all())
#        self.assertEqual(tmodel.metadata, self.model.metadata)
#        self.assertEqual(tmodel.vocabulary, self.model.vocabulary)

    def test_to_hdf5(self):
        hmodel = to_hdf5(T_)

        self.assertIsInstance(hmodel, HDF5TAPModel)
        self.assertEqual(hmodel.a, T_.a)
        self.assertEqual(hmodel.r, T_.r)
        self.assertEqual(hmodel.g, T_.g)
        self.assertEqual(hmodel.b, T_.b)
        self.assertEqual(hmodel.theta, T_.theta)
        self.assertEqual(hmodel.N_d, T_.N_d)

#    def test_from_to_hdf5(self):
#        tmodel = from_hdf5(self.model)
#        hmodel = to_hdf5(tmodel)
#
#        self.assertEqual(tmodel.e_theta[0].all(), hmodel.e_theta[0].all())
#        self.assertEqual(tmodel.phi[0].all(), hmodel.phi[0].all())
#        self.assertEqual(tmodel.metadata, hmodel.metadata)
#        self.assertEqual(tmodel.vocabulary, hmodel.vocabulary)

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()