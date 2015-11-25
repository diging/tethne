import sys
sys.path.append('../tethne')
datapath = './tethne/tests/data/test_citations_sample.xml'

import unittest

from tethne.utilities import subdict
from tethne.utilities import concat_list
from tethne.utilities import overlap
from tethne.utilities import _strip_punctuation
from tethne.utilities import strip_punctuation
from tethne.utilities import Dictionary
from tethne.utilities import attribs_to_string
from tethne.utilities import argmax
from tethne.utilities import contains
from tethne.utilities import dict_from_node
import xml.etree.ElementTree as ET
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

#method not changing anything much
class TestAttribsToString(unittest.TestCase):

    def test_attribs(self):
        present_dict = { 1:[2,4,6,8], 2:(7,14), 3:{10:20}, 4:100, 5:300, 6:400}

        self.assertEqual(present_dict,attribs_to_string(present_dict,None))

class TestArgMax(unittest.TestCase):

    def test_arg_max_str(self):
        iterable = ['efgh','abcd','jklm','poqr']
        self.assertEqual(3,argmax(iterable))

    def test_arg_max_num(self):
        iterable = [30,10,40,20]
        self.assertEqual(2,argmax(iterable))

class TestContains(unittest.TestCase):

    def test_contains_true(self):
        l = [2,4,1,6]
        f = lambda x: x %2 == 1

        self.assertEqual(True,contains(l,f))

    def test_contains_false(self):
        l = [0,2,4,8]
        f = lambda x: x%2 == 1

        self.assertEqual(False,contains(l,f))

class TestDictFromNode(unittest.TestCase):

    """
    Testing the functionality when there are more than one node of the same type and the resultants values are in propertly obtained in the list
    and also when there is only node of a type, the resultant is a String
    """
    def test_dict_from_node(self):
        with open(datapath, 'r') as f:
            root = ET.fromstring(f.read())
            pattern = './/{elem}'.format(elem='article')
            elements = root.findall(pattern)
            present_dict = dict_from_node(elements[0])

        expectedList = ['Askell Dove','Doris Love']
        expectedString = 'American Midland Naturalist'
        self.assertEqual(11,len(present_dict))
        self.assertEqual(expectedList,present_dict.get('author'))
        self.assertEqual(expectedString,present_dict.get('journaltitle'))

    """
    Testing the functionality when one of the nodes have children and recursive value is false
    """
    def test_dict_from_node_rec_false(self):

        with open(datapath, 'r') as f:
            root = ET.fromstring(f.read())
            pattern = './/{elem}'.format(elem='article')
            elements = root.findall(pattern)
            present_dict = dict_from_node(elements[1])

        expectedListSize = 2

        self.assertEqual(expectedListSize,present_dict.get('authors'))

    """
    Testing the functionality when one of the nodes have children and recursive value is true
    """
    def test_dict_from_node_rec_True(self):
        with open(datapath, 'r') as f:
            root = ET.fromstring(f.read())
            pattern = './/{elem}'.format(elem='article')
            elements = root.findall(pattern)
            present_dict = dict_from_node(elements[1],True)

        expectedDict = {'author': ['Askell Dove', 'Doris Love']}
        self.assertEqual(expectedDict,present_dict.get('authors'))



if __name__ == '__main__':
    unittest.main()
