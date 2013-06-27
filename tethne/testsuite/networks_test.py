import tethne.readers as rd
import tethne.networks as nt
import tethne.writers as wr
import unittest
import networkx as nx
import os
import os.path

class TestCitationGraph(unittest.TestCase):
    """
    Test the citations, internal_citations networks (assuming the reader 
        is functioning) by checking both 'citation' and 'internal' networks
        each with either 'doi' or 'ayjid' node_ids and either no
        node attributes or 4 node attributes of 4 different variable
        types
    The sparse data file networks are built on is //testin/wos_citations.txt
   """
    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_citations.txt')
        meta_list = rd.wos2meta(wos_data)

        # ayjid with no attributes
        (self.ayjid_citations, 
         self.ayjid_internal) = nt.nx_citations(meta_list, 'ayjid')

        # doi with no attributes                                          
        (self.doi_citations, 
         self.doi_internal) = nt.nx_citations(meta_list, 'doi')

        #int, string, list, dict
        self.node_attribs = ('date', 'atitle', 'aulast', 'citations')
        # ayjid with attribs 
        (self.ayjid_cit_attrib,
         self.ayjid_int_attrib) = nt.nx_citations(meta_list,
                                                  'ayjid',
                                                  *self.node_attribs)
        # doi with attribs
        (self.doi_cit_attrib,
         self.doi_int_attrib) = nt.nx_citations(meta_list,
                                                'doi',
                                                *self.node_attribs)

    def test_ayjid(self):
        """
        Test of nx_citations with ayjid as node_id and no node attributes

        If fails, something is wrong with the construction of ayjid's
        """
        # three papers in file each with author, year, journal information
        self.assertEqual(nx.number_of_nodes(self.ayjid_internal), 3)

        # ayjid of first paper's first reference does not match exactly
        # with the ayjid of the second paper
        self.assertEqual(nx.number_of_edges(self.ayjid_internal), 0)

        # since inexact match, 3 papers with 9 citations
        self.assertEqual(nx.number_of_nodes(self.ayjid_citations), 12)

        # one edge from paper to its citations
        self.assertEqual(nx.number_of_edges(self.ayjid_citations), 9)

    def test_doi(self):
        """
        Test of nx_citations with doi as node_id and no node attributes

        If fails, something is wrong with the parsing of WOS files at
        either the DI field tag for papers or the DOI number in the CR
        field tag
        """
        # three papers in file, each with DI(=DOI) field tags
        self.assertEqual(nx.number_of_nodes(self.doi_internal), 3)

        # DOI does match exactly: first paper references second paper
        self.assertEqual(nx.number_of_edges(self.doi_internal), 1)

        # only 7 of the papers/references have DOI numbers
        self.assertEqual(nx.number_of_nodes(self.doi_citations), 7)

        # first paper has edges to its 3 citations, second has one to its
        # and third has one
        self.assertEqual(nx.number_of_edges(self.doi_citations), 5)

    def test_node_attribs(self):
        """
        Test adding of node attributes to 4 graphs: ayjid no attribs, ayjid
            with attribs, doi no attribs, and doi with attribs

        If fails, something is wrong with the assigning of node attributes
        from a meta_dict in the citations networks
        """
        # check that the attributes got added to each node
        graphs = [self.ayjid_cit_attrib, self.ayjid_int_attrib,
                  self.doi_cit_attrib, self.doi_int_attrib]
        for graph in graphs:
            for node in graph.nodes():
                node_attribs = sorted(graph.node[node])
                check_attribs = sorted(self.node_attribs)
                self.assertEqual(node_attribs, check_attribs)
        
    def test_edge_attribs(self):
        """
        Test adding of edge attributes indicating what date a paper is cited

        If fails, something is wrong with assigning the edge attribute from a
        paper to its citation indicating the date of citation
        """
        # attributes of first paper citing its first reference
        edge_attribs = self.doi_citations.edge['10.1007/s10646-013-1042-4']['10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2']
        keys = edge_attribs.keys()
        self.assertIn('date', keys)
        self.assertEqual(edge_attribs['date'], 2013)

    def test_no_edge_attrib(self):
        """
        Test adding of edge attributes when citating paper's date is missing

        If the publication date is unknown (that is, PY field tag is missing
        from the WOS data file), the edge_attribute has value None; if
        fails that assumption is wrong
        """
        # attributes of third paper citing its only reference, PY=date key
        # missing
        edge_attribs = self.doi_citations.edge['10.1016/j.ecolind.2011.07.024']['10.1016/j.ecss.2008.08.010']
        keys = edge_attribs.keys()
        self.assertIn('date', keys)
        self.assertEqual(edge_attribs['date'], None)

    def tearDown(self):
        pass

class TestAuthorPapersGraph(unittest.TestCase):
    """
    Test the author_papers network
    Assumes reader is functioning

    The test file ./testin/wos_authors.txt contains two papers in WoS field tag
    format that are from the same author. One is fully capitalized and the
    other is not.

    We also test multiple authors and their link to the same paper
    """
    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_authors.txt')
        meta_list = rd.wos2meta(wos_data)
        self.author_papers = nt.nx_author_papers(meta_list, 'doi')

    def test_case_sensitivity(self):
        """
        Fails if case sensitivity of author names matters
        This is particularly relevant for author_papers network because
        a string identifier is all we have to identify authors

        more of a reader test case
        """
        person_count = 0
        for node in self.author_papers:
            if self.author_papers.node[node]['type'] == 'person':
                person_count += 1

        self.assertEqual(person_count, 2)

    def test_graph(self):
        """
        Fails if the number of nodes or edges are different than expected
        """
        self.assertEqual(nx.number_of_edges(self.author_papers), 3)

    def tearDown(self):
        pass


class TestCoauthorsGraph(unittest.TestCase):
    """
    Test the coauthors network, assumes reader is functioning
    """

    def setUp(self):
        #read data from docs folder
        wos_data = rd.parse_wos('./testin/wos_coauthors.txt')
        meta_list = rd.wos2meta(wos_data)
        self.coauthors = nt.nx_coauthors(meta_list)

    def test_no_shared_authors(self):
        pass

    def test_shared_author(self):
        # viewing the input file we see 2 papers, one with 6 authors and
        # another with 4 but Cajaraville is a common author
        self.assertEqual(nx.number_of_nodes(self.coauthors), 9)

        # 6 choose 2 + 4 choose 2 = 21 edges
        self.assertEqual(nx.number_of_edges(self.coauthors), 21)

    def test_edge_attribs(self):
        pass

    def tearDown(self):
        pass


class TestBiblioGraph(unittest.TestCase):
    """
    Test the bibliographic_coupling network; assumes reader is functioning

    The viewer will note that the input file has 4 papers trimmed down
    and modified from the sample //docs/savedrecs.txt. The references
    were constructed so that the first paper shares two citations with the
    second paper, one (of the two shared between first and second) citation 
    with the third paper, and zero citations with the fourth paper.
    """

    def setUp(self):
        wos_data = rd.parse_wos('./testin/wos_biblio.txt')
        wos_meta = rd.wos2meta(wos_data)
        self.ayjid_zero = nt.nx_biblio_coupling(wos_meta, 
                                                 'ayjid',
                                                 0,
                                                 'ayjid')
        self.ayjid_one = nt.nx_biblio_coupling(wos_meta, 
                                               'ayjid',
                                               1,
                                               'ayjid')
        self.ayjid_two = nt.nx_biblio_coupling(wos_meta, 
                                               'ayjid',
                                               2,
                                               'ayjid')
        self.ayjid_attribs = nt.nx_biblio_coupling(wos_meta,
                                                   'ayjid',
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'aulast',
                                                   'date',
                                                   'citations')

    def test_ayjid_zero(self):
        """
        Every paper shares at least 0 references with every other
        paper. This makes a complete graph.
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.ayjid_zero), 4)
        # 4 choose 2 = 6 edges 
        self.assertEqual(nx.number_of_edges(self.ayjid_zero), 6)

    def test_ayjid_one(self):
        """
        With threshold greater than 0, two papers must share at least 1
        reference in common. Test this when threshold is 1.
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.ayjid_one), 4)
        # first paper shares 2 >= 1 references with second, 1 >= 1 references
        # with third, and the second and third share 1 >= 1 references
        self.assertEqual(nx.number_of_edges(self.ayjid_one), 3)

    def test_ayjid_two(self):
        """
        With threshold greater than 0, two papers must share at least 1
        reference in common. Test this when threshold is 2.
        """
        self.assertEqual(nx.number_of_nodes(self.ayjid_two), 4)
        # first paper shares 2 >= 2 references with second
        self.assertEqual(nx.number_of_edges(self.ayjid_two), 1)

    def test_attribs(self):
        """
        Test the addition of four node attributes of different types:
            atitle - a string
            date - an int
            aulast - a list
            citations - a dictionary
        Presumably a double may be added to a network just as easily as an
        int, but we have no doubles to test in our standard meta_dict
        """
        pass

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
        wos_data = rd.parse_wos('../../docs/savedrecs.txt')
        meta_list = rd.wos2meta(wos_data)
        self.ayjid_one = nt.nx_author_coupling(meta_list,
                                               1,
                                               'ayjid')
        self.ayjid_attribs = nt.nx_author_coupling(meta_list,
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'citations',
                                                   'date',
                                                   'aulast')

    def test_ayjid_one(self):
        self.assertIsNotNone(self.ayjid_one)

    def test_ayjid_attribs(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
