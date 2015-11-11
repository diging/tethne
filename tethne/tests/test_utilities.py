import sys
sys.path.append('./')


import unittest

from tethne.utilities import subdict
from tethne.utilities import concat_list
from tethne.utilities import overlap
from tethne.utilities import _strip_punctuation
from tethne.utilities import strip_punctuation
from tethne.utilities import Dictionary

from tethne.utilities import strip_non_ascii

#testing method "_strip_punctuation"
class TestStripPunctuation(unittest.TestCase):
    def test_str(self):
        self.assertEqual('asdf', _strip_punctuation('a.s,d;f?'))

    def test_unicode(self):
        self.assertEqual(u'asdf', _strip_punctuation(u'a.s,d;f?'))

class TestOverlap(unittest.TestCase):

    def test_empty_listA(self):
        self.assertEqual([],overlap([1,2,3,4],None))

    def test_empty_listB(self):
        self.assertEqual([],overlap(None,[1,2,3,4]))

    def test_both_not_empty(self):
        self.assertEqual([2,4],overlap([1,2,3,4],[2,4]))

class TestSubDict(unittest.TestCase):

    def test_NonEmpty(self):
        superdict = { 1:10, 2:20, 3:30, 4:40}
        keys = {2,4}
        test_subdict = {2:20, 4:40}
        self.assertEqual(test_subdict,subdict(superdict,keys))

class TestConcatList(unittest.TestCase):

    def test_EqualSize_Default(self):
        listA = ['a','c','e']
        listB = ['b','f','h']
        self.assertEqual(['a b','c f','e h'],concat_list(listA,listB))

    def test_EqualSize(self):
        listA = ['a','c','e']
        listB = ['b','f','h']
        delim = ','
        self.assertEqual(['a,b','c,f','e,h'],concat_list(listA,listB,delim))

#testing method "strip_punctuation"
class TestStripPunctual2(unittest.TestCase):

    def test_string(self):
        self.assertEqual('abcd',strip_punctuation('a$b%c@d'))

    def test_empty_string(self):
        self.assertEqual('', strip_punctuation(''))

class TestSetItem(unittest.TestCase):

    def test_key_str(self):
        dict_obj = Dictionary()
        dict_str = {}
        dict_int = {}
        dict_str['string'] = 4
        dict_int[4] = 'string'
        Dictionary.__setitem__(dict_obj,'string',4)

        self.assertEqual(dict_str,dict_obj.by_str)
        self.assertEqual(dict_int,dict_obj.by_int)

    def test_key_int(self):
        dict_obj = Dictionary()
        dict_str = {}
        dict_int = {}
        dict_int[8] = 'str'
        dict_str['str'] = 8
        Dictionary.__setitem__(dict_obj,8,'str')

        self.assertEqual(dict_int,dict_obj.by_int)
        self.assertEqual(dict_str,dict_obj.by_str)

class TestGetItem(unittest.TestCase):

    def test_key_str(self):
        dict_obj = Dictionary()

        Dictionary.__setitem__(dict_obj,6,'string')
        self.assertEqual('string',Dictionary.__getitem__(dict_obj,6))

    def test_key_int(self):
        dict_obj = Dictionary()

        Dictionary.__setitem__(dict_obj,'str',8)
        self.assertEqual(8,Dictionary.__getitem__(dict_obj,'str'))

if __name__ == '__main__':
    unittest.main()
