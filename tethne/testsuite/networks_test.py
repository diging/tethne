import tethne.readers as rd
import tethne.networks as nt
import tethne.writers as wr
import unittest
import networkx as nx
import os
import os.path

class TestCitationGraph(unittest.TestCase):
    """
    Test the citations, internal_citations networks
    Assumes reader is functioning
    Doesn't perform that rigorous of a test: should we pickle a
        sample graph and check the result against that graph?
    """

    def setUp(self):
        #read data from docs folder
        self.wos_data = rd.build('../../docs/savedrecs.txt')

    def test_citations(self):
        self.G1, self.G2 = nt.nx_citations(self.wos_data)
        self.assertIsNotNone(self.G1)
        self.assertIsNotNone(self.G2)

    def tearDown(self):
        pass


class TestAuthorPapersGraph(unittest.TestCase):
    """
    Test the author_papers network
    Assumes reader is functioning
    Doesn't perform that rigorous of a test: should we pickle a
        sample graph and check the result against that graph?
    """

    def setUp(self):
        #read data from docs folder
        self.wos_data = rd.build('../../docs/savedrecs.txt')

    def test_citations(self):
        self.G1  = nt.nx_author_papers(self.wos_data)
        self.assertIsNotNone(self.G1)

    def tearDown(self):
        pass


class TestCoauthorsGraph(unittest.TestCase):
    """
    Test the coauthors network
    Assumes reader is functioning
    Doesn't perform that rigorous of a test: should we pickle a
        sample graph and check the result against that graph?
    """

    def setUp(self):
        #read data from docs folder
        self.wos_data = rd.build('../../docs/savedrecs.txt')

    def test_citations(self):
        self.G1  = nt.nx_coauthors(self.wos_data)
        self.assertIsNotNone(self.G1)

    def tearDown(self):
        pass


class TestBiblioGraph(unittest.TestCase):
    """
    Test the bibliographic_coupling network
    Assumes reader is functioning
    Doesn't perform that rigorous of a test: should we pickle a
        sample graph and check the result against that graph?
    """

    def setUp(self):
        #read data from docs folder
        self.wos_data = rd.build('../../docs/savedrecs.txt')

    def test_citations(self):
        self.G1  = nt.nx_biblio_coupling(self.wos_data,1)
        self.assertIsNotNone(self.G1)

    def tearDown(self):
        pass


class TestAuthorCouplingGraph(unittest.TestCase):
    """
    Test the author_coupling network
    Assumes reader is functioning
    Doesn't perform that rigorous of a test: should we pickle a
        sample graph and check the result against that graph?
    """

    def setUp(self):
        #read data from docs folder
        self.wos_data = rd.build('../../docs/savedrecs.txt')

    def test_citations(self):
        self.G1  = nt.nx_author_coupling(self.wos_data,1)
        self.assertIsNotNone(self.G1)

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
