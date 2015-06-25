import sys
sys.path.append('./')

import unittest

import networkx as nx

from tethne.readers.wos import read
from tethne.networks.authors import author_papers, coauthors

datapath = './tethne/tests/data/wos.txt'


class TestAuthorPapers(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)

    def test_author_papers(self):
        g = author_papers(self.corpus)
        N_authors = len(self.corpus.indices['authors'])
        N_papers = len(self.corpus.papers)

        # A node for every paper and for every author.
        self.assertEqual(g.order(), N_authors + N_papers)


class TestCoauthors(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)

    def test_author_papers(self):
        g = coauthors(self.corpus)
        N_authors = len(self.corpus.indices['authors'])

        # A node for every author.
        self.assertEqual(g.order(), N_authors)


if __name__ == '__main__':
    unittest.main()
