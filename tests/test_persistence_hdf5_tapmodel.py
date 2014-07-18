from settings import *

import unittest

from tethne.model.social import tapmodel
from tethne.persistence.hdf5 import HDF5TAPModel

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

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()