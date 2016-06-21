import sys
sys.path.append('../tethne')

import re

import unittest

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


def is_number(value):
    try:
        int(value)
    except ValueError:
        try:
            float(value)
        except ValueError:
            return False
    return True


class TestWoSParserParseOnly(unittest.TestCase):
    def test_read_title(self):
        """
        Passing the ``parse_only`` parameter to ``read`` limits the fields in
        the resulting :class:`.Paper` instances to only those specified.
        """
        from tethne.readers.wos import WoSParser, read
        from tethne import Corpus, Paper

        datapath = './tethne/tests/data/wos2.txt'
        datapath_v = './tethne/tests/data/valentin.txt'

        corpus = read(datapath, parse_only=['title', 'date'])
        for e in corpus:
            self.assertFalse(hasattr(e, 'journal'))
            self.assertTrue(hasattr(e, 'date'))
            self.assertFalse(hasattr(e, 'authors_full'))
            self.assertFalse(hasattr(e, 'volume'))
            self.assertTrue(hasattr(e, 'title'))
            self.assertTrue(hasattr(e, 'wosid'))

    def test_parse(self):
        """
        Passing the ``parse_only`` parameter to :meth:`.WoSParser.parse` limits
        the fields in the resulting :class:`.Paper` instances to only those
        specified.
        """
        from tethne.readers.wos import WoSParser, read
        from tethne import Corpus, Paper

        datapath = './tethne/tests/data/wos2.txt'
        datapath_v = './tethne/tests/data/valentin.txt'

        parser = WoSParser(datapath)
        parser.parse(parse_only=['title'])


        for e in parser.data:
            self.assertFalse(hasattr(e, 'journal'))
            self.assertFalse(hasattr(e, 'date'))
            self.assertFalse(hasattr(e, 'authors_full'))
            self.assertFalse(hasattr(e, 'volume'))
            self.assertTrue(hasattr(e, 'title'))

        # Check number of records.
        N = len(parser.data)
        self.assertEqual(N, 100, 'Expected 100 entries, found {0}.'.format(N))

    datapath = './tethne/tests/data/dfr'
    datapath_float_weights = './tethne/tests/data/dfr_float_weights'
    sample_datapath = './tethne/tests/data/test_citations_sample.xml'


class TestDFRReaderParseOnly(unittest.TestCase):
    def test_read(self):

        from tethne.readers.dfr import read
        from tethne import Corpus, Paper, FeatureSet
        import xml.etree.ElementTree as ET

        datapath = './tethne/tests/data/dfr'
        datapath_float_weights = './tethne/tests/data/dfr_float_weights'
        sample_datapath = './tethne/tests/data/test_citations_sample.xml'

        corpus = read(datapath, parse_only=['date', 'title'])

        self.assertIsInstance(corpus, Corpus)

        for e in corpus:
            self.assertFalse(hasattr(e, 'journal'))
            self.assertTrue(hasattr(e, 'date'))
            self.assertFalse(hasattr(e, 'authors_full'))
            self.assertFalse(hasattr(e, 'volume'))
            self.assertTrue(hasattr(e, 'doi'))


if __name__ == '__main__':
    unittest.main()
