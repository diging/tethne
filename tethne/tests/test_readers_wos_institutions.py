import sys
sys.path.append('../tethne')

import re

import unittest
from tethne.readers.wos import WoSParser, read
from tethne import Corpus, Paper, StreamingCorpus

datapath_0 = './tethne/tests/data/wos.txt'
datapath = './tethne/tests/data/wos2.txt'
datapath_3 = './tethne/tests/data/wos3.txt'
datapath_v = './tethne/tests/data/valentin.txt'

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


class TestParseInstitution(unittest.TestCase):
    def test_explicit_addresses(self):
        corpus = read(datapath)
        for paper in corpus:
            if hasattr(paper, 'authorAddress'):
                self.assertTrue(hasattr(paper, 'addresses'))
                self.assertIsInstance(paper.addresses, dict)

                # There should be at least as many authors as addresses.
                self.assertTrue(len(paper.authors) >= len(paper.addresses))

    def test_ambiguous_addresses(self):
        corpus = read(datapath_v)
        for i, paper in enumerate(corpus):
            if hasattr(paper, 'authorAddress'):
                self.assertTrue(hasattr(paper, 'addresses'))
                self.assertIsInstance(paper.addresses, dict)

                self.assertIn('__all__', paper.addresses)
                addresses = paper.addresses.get('__all__')
                self.assertIsInstance(addresses, list)

                self.assertIsInstance(addresses[0], tuple)
                self.assertEqual(len(addresses[0]), 3)
                if i == 0:
                    self.assertEqual(addresses[0][0], u'UNIV WESTERN SYDNEY')
                    self.assertEqual(addresses[0][1], u'AUSTRALIA')
                elif i == 1:
                    self.assertEqual(addresses[0][0], u'QUEENSLAND UNIV TECHNOL')
                    self.assertEqual(addresses[0][1], u'AUSTRALIA')

    def test_more_addresses(self):
        corpus = read(datapath_0)
        for paper in corpus:
            if hasattr(paper, 'authorAddress'):
                self.assertTrue(hasattr(paper, 'addresses'))
                self.assertIsInstance(paper.addresses, dict)

                self.assertIn('__all__', paper.addresses)
                addresses = paper.addresses.get('__all__')
                self.assertIsInstance(addresses, list)

                self.assertIsInstance(addresses[0], tuple)
                self.assertEqual(len(addresses[0]), 3)

    def test_even_more_addresses(self):
        corpus = read(datapath_0)
        for paper in corpus:
            if hasattr(paper, 'authorAddress'):
                self.assertTrue(hasattr(paper, 'addresses'))
                self.assertIsInstance(paper.addresses, dict)

                self.assertIn('__all__', paper.addresses)
                addresses = paper.addresses.get('__all__')
                self.assertIsInstance(addresses, list)

                self.assertIsInstance(addresses[0], tuple)
                self.assertEqual(len(addresses[0]), 3)



if __name__ == '__main__':
    unittest.main()
