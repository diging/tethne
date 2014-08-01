from settings import *

import unittest
import warnings
import tables
import os
import numpy

from tethne.persistence.hdf5.util import *

class TestStore(unittest.TestCase):
    def setUp(self):
        self.h5name = 'HDF5_test.h5'
        self.h5path = temppath + '/' + self.h5name
        self.h5file,a,b = get_h5file('Test', self.h5path)
        self.group = get_or_create_group(self.h5file, 'testgroup')

        self.stratom = tables.StringAtom(100)
        self.intatom = tables.Int32Atom()
        self.floatatom = tables.Float32Atom()

    def test_create_vlarray_dict_intkey(self):
        """
        keys are integers, values are integers
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.intatom,
                            self.intatom    )
        keys = range(0,10)
        values = numpy.random.randint(1, 10, size=(10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        # Values are the right shape
        vd_ = h5file.getNode(group, 'test')
        self.assertEqual(vd_.shape[0], len(keys) + 1)     # 0-padded

        # Index is the right shape
        vd_index = h5file.getNode(group, 'test_keys')
        self.assertEqual(vd_index.shape[0], len(keys) + 1)
        self.assertEqual(vd_index[i+1], keys[i])

        # Same values and keys
        for i in xrange(len(keys)):
            self.assertEqual(vd_[i+1].all(), values[i].all())
            self.assertEqual(vd_index[i+1], keys[i])

    def test_create_vlarray_dict_intstr(self):
        """
        keys are strings, values are integers
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.intatom,
                            self.stratom    )
        keys = ['a','b','c','d','e','f','g','h','i','j']
        values = numpy.random.randint(1, 10, size=(10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        # Values are the right shape
        vd_ = h5file.getNode(group, 'test')
        self.assertEqual(vd_.shape[0], len(keys) + 1)     # 0-padded

        # Index is the right shape
        vd_index = h5file.getNode(group, 'test_keys')
        self.assertEqual(vd_index.shape[0], len(keys) + 1)

        # Same values and keys
        for i in xrange(len(keys)):
            self.assertEqual(vd_[i+1].all(), values[i].all())
            self.assertEqual(vd_index[i+1], keys[i])

    def test_create_vlarray_dict_strstr(self):
        """
        keys are strings, values are strings
        """

        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.stratom,
                            self.stratom    )
        keys = ['a','b','c','d','e','f','g','h','i','j']
        values = []
        for i in xrange(len(keys)):
            values.append( numpy.array(['argh'] + [ keys[x] for x in xrange(i) ] ))

        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        # Values are the right shape
        vd_ = h5file.getNode(group, 'test')
        self.assertEqual(vd_.shape[0], len(keys) + 1)     # 0-padded

        # Index is the right shape
        vd_index = h5file.getNode(group, 'test_keys')
        self.assertEqual(vd_index.shape[0], len(keys) + 1)

        # Same values and keys
        for i in xrange(len(keys)):
            for x in xrange(len(values[i])):
                self.assertEqual(vd_[i+1][x], values[i][x])
            self.assertEqual(vd_index[i+1], keys[i])

    def test_create_vlarray_dict_strint(self):
        """
        keys are integers, values are strings
        """

        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.stratom,
                            self.intatom    )
        keys = range(0,10)
        lets = ['a','b','c','d','e','f','g','h','i','j']
        values = []
        for i in xrange(len(keys)):
            values.append( numpy.array(['argh'] + [ lets[x] for x in xrange(i) ] ))

        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        # Values are the right shape
        vd_ = h5file.getNode(group, 'test')
        self.assertEqual(vd_.shape[0], len(keys) + 1)     # 0-padded

        # Index is the right shape
        vd_index = h5file.getNode(group, 'test_keys')
        self.assertEqual(vd_index.shape[0], len(keys) + 1)

        # Same values and keys
        for i in xrange(len(keys)):
            for x in xrange(len(values[i])):
                self.assertEqual(vd_[i+1][x], values[i][x])
            self.assertEqual(vd_index[i+1], keys[i])

    def test_create_vlarray_dict_floatint(self):
        """
        keys are integers, values are floats
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.floatatom,
                            self.intatom    )
        keys = range(0,10)
        values = numpy.random.random((10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        # Values are the right shape
        vd_ = h5file.getNode(group, 'test')
        self.assertEqual(vd_.shape[0], len(keys) + 1)     # 0-padded

        # Index is the right shape
        vd_index = h5file.getNode(group, 'test_keys')
        self.assertEqual(vd_index.shape[0], len(keys) + 1)
        self.assertEqual(vd_index[i+1], keys[i])

        # Same values
        for i in xrange(len(keys)):
            self.assertEqual(vd_[i+1].all(), values[i].all())
            self.assertEqual(vd_index[i+1], keys[i])

    def tearDown(self):
        os.remove(self.h5path)

class TestRetrieve(unittest.TestCase):
    def setUp(self):
        self.h5name = 'HDF5_test.h5'
        self.h5path = temppath + '/' + self.h5name
        self.h5file,a,b = get_h5file('Test', self.h5path)
        self.group = get_or_create_group(self.h5file, 'testgroup')

        self.stratom = tables.StringAtom(100)
        self.intatom = tables.Int32Atom()
        self.floatatom = tables.Float32Atom()

    def test_create_vlarray_dict_intkey(self):
        """
        keys are integers, values are integers
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.intatom,
                            self.intatom    )
        keys = range(0,10)
        values = numpy.random.randint(1, 10, size=(10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        vd_ = vlarray_dict( h5file,
                            group,
                            'test',
                            self.intatom,
                            self.intatom    )

        # Right length
        self.assertEqual(len(vd_), len(keys))

        # Right keys
        self.assertEqual(set(vd_.keys()), set(keys))

        # Right values
        for i in xrange(len(keys)):
            self.assertEqual(vd_[keys[i]].all(), values[i].all())

    def tearDown(self):
        os.remove(self.h5path)

    def test_create_vlarray_dict_intstr(self):
        """
        keys are strings, values are integers
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.intatom,
                            self.stratom    )
        keys = ['a','b','c','d','e','f','g','h','i','j']
        values = numpy.random.randint(1, 10, size=(10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        vd_ = vlarray_dict( h5file,
                            group,
                            'test',
                            self.intatom,
                            self.stratom    )

        # Right length
        self.assertEqual(len(vd_), len(keys))

        # Right keys
        self.assertEqual(set(vd_.keys()), set(keys))

        # Right values
        for i in xrange(len(keys)):
            self.assertEqual(vd_[keys[i]].all(), values[i].all())

    def test_create_vlarray_dict_strstr(self):
        """
        keys are strings, values are strings
        """

        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.stratom,
                            self.stratom    )
        keys = ['a','b','c','d','e','f','g','h','i','j']
        values = []
        for i in xrange(len(keys)):
            values.append( numpy.array(['argh'] + [ keys[x] for x in xrange(i) ] ))

        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        vd_ = vlarray_dict( h5file,
                            group,
                            'test',
                            self.stratom,
                            self.stratom    )

        # Right length
        self.assertEqual(len(vd_), len(keys))

        # Right keys
        self.assertEqual(set(vd_.keys()), set(keys))

        # Right values
        for i in xrange(len(keys)):
            for x in xrange(len(values[i])):
                self.assertEqual(vd_[keys[i]][x], values[i][x])

    def test_create_vlarray_dict_strint(self):
        """
        keys are integers, values are strings
        """

        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.stratom,
                            self.intatom    )
        keys = range(0,10)
        lets = ['a','b','c','d','e','f','g','h','i','j']
        values = []
        for i in xrange(len(keys)):
            values.append( numpy.array(['argh'] + [ lets[x] for x in xrange(i) ] ))

        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        vd_ = vlarray_dict( h5file,
                            group,
                            'test',
                            self.stratom,
                            self.intatom    )

        # Right length
        self.assertEqual(len(vd_), len(keys))

        # Right keys
        self.assertEqual(set(vd_.keys()), set(keys))

        # Right values
        for i in xrange(len(keys)):
            for x in xrange(len(values[i])):
                self.assertEqual(vd_[keys[i]][x], values[i][x])

    def test_create_vlarray_dict_floatint(self):
        """
        keys are integers, values are floats
        """
        vd = vlarray_dict(  self.h5file,
                            self.group,
                            'test',
                            self.floatatom,
                            self.intatom    )
        keys = range(0,10)
        values = numpy.random.random((10, 100))
        for i in xrange(len(keys)):
            vd[keys[i]] = values[i]
            self.assertEqual(len(vd), i+1)

        self.h5file.close()

        ### Load data directly, and inspect ###

        h5file,a,b = get_h5file('Test', self.h5path)
        group = get_or_create_group(h5file, 'testgroup')
        self.assertIn('test', group)

        vd_ = vlarray_dict( h5file,
                            group,
                            'test',
                            self.floatatom,
                            self.intatom    )

        # Right length
        self.assertEqual(len(vd_), len(keys))

        # Right keys
        self.assertEqual(set(vd_.keys()), set(keys))

        # Right values
        for i in xrange(len(keys)):
            self.assertEqual(vd_[keys[i]].all(), values[i].all())

    def tearDown(self):
        os.remove(self.h5path)

if __name__ == '__main__':
    unittest.main()
