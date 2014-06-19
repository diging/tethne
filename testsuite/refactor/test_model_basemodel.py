import unittest

import sys
sys.path.append('../../')

from tethne.model import BaseModel

class TestModelBad(BaseModel):
    def __init__(self):
        pass

class TestModelGood(BaseModel):
    def __init__(self):
        pass

    def _item_description(self, i, **kwargs):
        return [ (0, 0.5), (1, 0.8) ]

    def _item_relationship(self, i, j, **kwargs):
        return [ (0, 0.2), (1, 0.3) ]

    def _dimension_description(self, d, **kwargs):
        return [ (0, 0.01), (1, 0.02) ]

    def _dimension_relationship(self, d, e, **kwargs):
        return [ (0, 0.03), (1, 0.05) ]

class TestBaseModel(unittest.TestCase):
    def test_direct_instantiation(self):
        self.assertRaises(RuntimeError, BaseModel)

    def test_item_description_not_implemented(self):
        """
        Subclass of BaseModel must implement _item_description(i),
        otherwise a NotImplementedError is raised.
        """
        B = TestModelBad()
        self.assertRaises(NotImplementedError, B.item, 0)

    def test_item_relationship_not_implemented(self):
        """
        Subclass of BaseModel must implement _item_relationship(i,j),
        otherwise a NotImplementedError is raised.
        """
        B = TestModelBad()
        self.assertRaises(NotImplementedError, B.item_relationship, 0, 1 )

    def test_dimension_description_not_implemented(self):
        """
        Subclass of BaseModel must implement _dimension_description(d),
        otherwise a NotImplementedError is raised.
        """
        B = TestModelBad()
        self.assertRaises(NotImplementedError, B.dimension, 0)

    def test_dimension_relationship_not_implemented(self):
        """
        Subclass of BaseModel must implement _dimension_relationship(d,e),
        otherwise a NotImplementedError is raised.
        """
        B = TestModelBad()
        self.assertRaises(NotImplementedError, B.dimension_relationship, 0, 1)

    def test_item_description_passthrough(self):
        B = TestModelGood()
        self.assertIsInstance(B.item(0), list)
        self.assertIsInstance(B.item(0)[0], tuple)
        self.assertIsInstance(B.item(0)[0][0], int)

    def test_item_relationship_passthrough(self):
        B = TestModelGood()
        self.assertIsInstance(B.item_relationship(0,1), list)
        self.assertIsInstance(B.item_relationship(0,1)[0], tuple)
        self.assertIsInstance(B.item_relationship(0,1)[0][0], int)
    
    def test_dimension_description_passthrough(self):
        B = TestModelGood()
        self.assertIsInstance(B.dimension(0), list)
        self.assertIsInstance(B.dimension(0)[0], tuple)
        self.assertIsInstance(B.dimension(0)[0][0], int)

    def test_dimension_relationship_passthrough(self):
        B = TestModelGood()
        self.assertIsInstance(B.dimension_relationship(0,1), list)
        self.assertIsInstance(B.dimension_relationship(0,1)[0], tuple)
        self.assertIsInstance(B.dimension_relationship(0,1)[0][0], int)

if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()