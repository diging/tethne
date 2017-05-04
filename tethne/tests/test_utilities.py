import sys
sys.path.append('../tethne')
datapath = './tethne/tests/data/test_citations_sample.xml'
datapath2 = './tethne/tests/data/wos.txt'
datapath3 = './tethne/tests/data/dfr'

import numpy as np
import pandas as pd
import unittest

from tethne.readers import wos, dfr, zotero
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
from tethne.utilities import to_pandas
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


class TestToPandas(unittest.TestCase):
    """
    Class for testing corpus object to pandas export functionality.
    """

    def test_cols_present(self):
        """
        Ensure all standard columns are present in papers DataFrame
        """
        corpus = dfr.read(datapath3)
        papers_df = to_pandas(corpus)
        col_set = { 'doi', 'ayjid', 'title', 'citationCount',
            'date', 'journal', 'volume', 'issue', 'pageStart',
            'pageEnd', 'documentType', 'isoSource', 'language',
            'publisherAddress', 'publisherCity', 'address',
            'uri', 'link', 'abstract'
        }
        self.assertEqual(col_set, set(papers_df.columns))

    def _assert_col_datatype_str(self, column):
        corpus = wos.read(datapath2)
        papers_df = to_pandas(corpus)
        for value, notnull in zip(papers_df[column], pd.notnull(papers_df[column])):
            if notnull:
                self.assertIsInstance(
                    column, basestring,
                    '{} must be of type str, is {}'.format(column, value))

    def _assert_col_datatype_int(self, column):
        corpus = wos.read(datapath2)
        papers_df = to_pandas(corpus)
        for column, notnull in zip(papers_df[column], pd.notnull(papers_df[column])):
            if notnull:
                isNumeric = ((column.dtype == np.float) or (column.dtype == np.int))
                self.assertTrue(
                    isNumeric, '{} must be of type int/float'.format(column))

    def test_doi_datatype(self):
        """
        Ensure doi is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('doi')

    def test_ayjid_datatype(self):
        """
        Ensure ayjid is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('ayjid')

    def test_title_datatype(self):
        """
        Ensure title is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('title')

    def test_journal_datatype(self):
        """
        Ensure journal is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('journal')

    def test_volume_datatype(self):
        """
        Ensure volume is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('volume')

    def test_issue_datatype(self):
        """
        Ensure issue is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('issue')

    def test_documentType_datatype(self):
        """
        Ensure documentType is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('documentType')

    def test_isoSource_datatype(self):
        """
        Ensure isoSource is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('isoSource')

    def test_language_datatype(self):
        """
        Ensure language is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('language')

    def test_publisherAddress_datatype(self):
        """
        Ensure publisherAddress is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('publisherAddress')

    def test_publisherCity_datatype(self):
        """
        Ensure publisherCity is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('publisherCity')

    def test_address_datatype(self):
        """
        Ensure address is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('address')

    def test_uri_datatype(self):
        """
        Ensure uri is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('uri')

    def test_link_datatype(self):
        """
        Ensure link is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('link')

    def test_abstract_datatype(self):
        """
        Ensure abstract is of type str in papers DataFrame
        """
        self._assert_col_datatype_str('abstract')

    def test_citationCount_datatype(self):
        """
        Ensure citationCount is of type int/float in papers DataFrame
        """
        self._assert_col_datatype_int('citationCount')

    def test_pageStart_datatype(self):
        """
        Ensure pageStart is of type int in papers DataFrame
        """
        self._assert_col_datatype_int('pageStart')

    def test_pageEnd_datatype(self):
        """
        Ensure pageEnd is of type int in papers DataFrame
        """
        self._assert_col_datatype_int('pageEnd')

    def test_date_datatype(self):
        """
        Ensure date is of type `pandas.Period` in papers DataFrame
        """
        corpus = wos.read(datapath2)
        papers_df = to_pandas(corpus)
        for value, notnull in zip(papers_df['date'], pd.notnull(papers_df['date'])):
            if notnull:
                self.assertIsInstance(value, pd.Period)

if __name__ == '__main__':
    unittest.main()
