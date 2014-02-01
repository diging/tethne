"""
To do: move testing of different types of attributes to writers testing
rather than graph testing; NetworkX can support any data structure as an
attribute but the graph file formats may not.
"""

import tethne.readers as rd
import tethne.networks as nt
import tethne.writers as wr
import tethne.utilities as util
import unittest
import networkx as nx
import sys

class TestDirectCitationGraph(unittest.TestCase):
    """
    Test the citations, internal_citations networks (assuming the reader
        is functioning) by checking both 'citation' and 'internal' networks
        each with either 'doi' or 'ayjid' node_ids and either no
        node attributes or 4 node attributes of 4 different variable
        types
    The sparse data file networks are built on is //testin/wos_citations.txt
    """
    def setUp(self):
        wos_data = rd.wos.parse('./testin/wos_citations.txt')
        meta_list = rd.wos.convert(wos_data)

        # ayjid with no attributes
        (self.ayjid_citations,
         self.ayjid_internal) = nt.papers.direct_citation(meta_list, 'ayjid')

        # doi with no attributes
        (self.doi_citations,
         self.doi_internal) = nt.papers.direct_citation(meta_list, 'doi')

        # int, string, list, dict
        self.node_attribs = ('date', 'atitle', 'aulast', 'citations')

        # ayjid with attribs
        (self.ayjid_cit_attrib,
         self.ayjid_int_attrib) = nt.papers.direct_citation(meta_list,
                                                  'ayjid',
                                                  *self.node_attribs)
        # doi with attribs
        (self.doi_cit_attrib,
         self.doi_int_attrib) = nt.papers.direct_citation(meta_list,
                                                'doi',
                                                *self.node_attribs)

    def test_ayjid(self):
        """
        Test of citations with ayjid as node_id and no node attributes

        If fails, something is wrong with the construction of ayjid's
        """
        # three papers in file each with author, year, journal information
        self.assertEqual(nx.number_of_nodes(self.ayjid_internal), 3)

        # ayjid of first paper's first reference does not match exactly
        # with the ayjid of the second paper
        self.assertEqual(nx.number_of_edges(self.ayjid_internal), 0)

        # since inexact match, 3 papers with 8 citations
        self.assertEqual(nx.number_of_nodes(self.ayjid_citations), 11)

        # one edge from paper to its citations
        self.assertEqual(nx.number_of_edges(self.ayjid_citations), 8)

    def test_doi(self):
        """
        Test of citations with doi as node_id and no node attributes

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
        edge_attribs = self.doi_citations.edge \
                ['10.1007/s10646-013-1042-4'] \
                    ['10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2']
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
        edge_attribs = self.doi_citations.edge \
                ['10.1016/j.ecolind.2011.07.024']['10.1016/j.ecss.2008.08.010']
        keys = edge_attribs.keys()
        self.assertIn('date', keys)
        self.assertEqual(edge_attribs['date'], None)

    def tearDown(self):
        pass

class TestDirectCitation_DAG(unittest.TestCase):
    """
    Test the citations, internal_citations networks
    (assuming the reader is functioning)
    by checking both 'citation' and 'internal' networks
    each with either 'doi' or 'ayjid' node_ids and date as an attribute,

    This is the somewhat similar to the class TestDirectCitationGraph
    but it has extra tests to check if it is a DAG or not, and if the
    ancestors/descendants are populated correctly. The sparse data file networks
    are built on is "../testsuite/testin/citations_test.txt"

    It has 2 papers.
    """
    def setUp(self):

        wos_data = rd.wos.parse("../testsuite/testin/citations_test.txt")
        meta_list = rd.wos.convert(wos_data)

        # ayjid with no attributes
        (self.ayjid_citations,
         self.ayjid_internal) = nt.papers.direct_citation(meta_list, 'ayjid')

        # doi with no attributes
        (self.doi_citations,
         self.doi_internal) = nt.papers.direct_citation(meta_list, 'doi')


        # ayjid with attribs
        (self.ayjid_cit_attrib,
         self.ayjid_int_attrib) = nt.papers.direct_citation(meta_list,
                                                  'ayjid',
                                                  'date')
        # doi with attribs
        (self.doi_cit_attrib,
         self.doi_int_attrib) = nt.papers.direct_citation(meta_list,
                                                'doi',
                                                'date')

    def test_ayjid(self):
        """
        Test of citations with ayjid as node_id and no node attributes

        If fails, something is wrong with the construction of ayjid's
        """
        # three papers in file each with author, year, journal information
        self.assertEqual(nx.number_of_nodes(self.ayjid_internal), 2)

        # only 1 edge between 2 internal nodes
        self.assertEqual(nx.number_of_edges(self.ayjid_internal), 1)

        # 56
        self.assertEqual(nx.number_of_nodes(self.ayjid_citations), 56)

        # 65 edges
        self.assertEqual(nx.number_of_edges(self.ayjid_citations), 65)

    def test_doi(self):
        """
        Test of citations with doi as node_id and no node attributes

        If fails, something is wrong with the parsing of WOS files at
        either the DI field tag for papers or the DOI number in the CR
        field tag
        """
        # 2 internal papers
        self.assertEqual(nx.number_of_nodes(self.doi_internal), 2)

        # DOI does match exactly:
        self.assertEqual(nx.number_of_edges(self.doi_internal), 0)

        # only 19 of the papers/references have DOI numbers
        self.assertEqual(nx.number_of_nodes(self.doi_citations), 19)

        #22 edges between the nodes.
        self.assertEqual(nx.number_of_edges(self.doi_citations), 22)

    def is_citationnetwork_dag(self):
        """
        Testing if the citations graph is Directed Acyclic Graph or not.
        If it is false then the network will not be created and
        a Networkxerror will be thrown that it is not a DAG.
        """
        # Returns true if citations graph is DAG
        self.assert_(nx.is_directed_acyclic_graph(self.ayjid_cit_attrib),
                        "Citations Graph is not DAG")

    def is_internal_citationnetwork_dag(self):
        """
        Testing if Internal citations graph is Directed Acyclic Graph or not.
        If it is false then the network will not be created and an Networkxerror
        will be thrown that it is not a DAG.

        """
        # Returns true if citations graph is DAG
        self.assert_(nx.is_directed_acyclic_graph(self.ayjid_int_attrib),
                     "Internal Citations Graph is not DAG")


    def test_ancestors(self):
        """
        Testing the ancestors for a particular node which is specified
        in the input.It throws the error "Node not in the graph"
        if that node is not present.
        """

        #ESHELMAN is one of the citation of paper 1.
        c_ans = nx.ancestors(self.ayjid_citations,
                             'ESHELMAN LJ 1993 FDN GENETIC ALGORITH')
        #ALAMPORA G is a citation as well as a paper,
            #hence its a node in internal citations
        i_ans = nx.ancestors(self.ayjid_internal,
                             'ALAMPORA G 1999 INFORMATION SCIENCES')

    def test_descendants(self):
        """
        Testing the descendants of a particular node given in the  input.
        It throws the error "Node not in the graph" if that node is not present.
        """

        c_des = nx.descendants(self.ayjid_citations,
                               'ALAMPORA G 1999 INFORMATION SCIENCES')
        i_des = nx.descendants(self.ayjid_internal,
                               'WU Z 2012 NEUROCOMPUTING')

        # to check if error is raised if a node which
        # is not in the graph is called.

        # commented as of now
        # c_des_err = \
        # nx.descendants(self.ayjid_citations, \
        #     'ALAMPORA G 1999 addadaddsa SCIENCES')

        # self.assertRaises(NetworkXError, \
        # testsuite.networks_test.TestDirectCitation_DAG)

        #=======================================================================
        # try:
        #     c_des_err = nx.descendants(self.ayjid_citations, \
        #                   'ALAMPORA G 1999 addadaddsa SCIENCES')
        # except NetworkXError :
        #     self.fail('NetworkXerror thrown:', NetworkXError)
        #=======================================================================

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
        wos_data = rd.wos.parse('./testin/wos_authors.txt')
        meta_list = rd.wos.convert(wos_data)
        self.no_attribs = nt.authors.author_papers(meta_list, 'doi')

        # int, string, list, dict
        node_attribs = ('date', 'atitle', 'aulast', 'citations')
        self.node_attribs = nt.authors.author_papers(meta_list, 'doi',
                                                *node_attribs)

    def test_case_sensitivity(self):
        """
        Fails if case sensitivity of author names matters
        This is particularly relevant for author_papers network because
        a string identifier is all we have to identify authors

        more of a reader test case
        """
        person_count = 0
        for node in self.no_attribs:
            if self.no_attribs.node[node]['type'] == 'person':
                person_count += 1

        self.assertEqual(person_count, 2)

    def test_no_attribs(self):
        # 2 authors; 2 papers
        self.assertEqual(nx.number_of_nodes(self.no_attribs), 4)

        # ADAMS has 2 papers, MCLEAN has 1 paper
        self.assertEqual(nx.number_of_edges(self.no_attribs), 3)

        # each node minimally has the type attribute distinguishing
        # paper nodes from person nodes
        expected_keys = ['type']
        for node in self.no_attribs.nodes(data=True):
            node_attribs = node[1]
            obtained_keys = node_attribs.keys()
            self.assertEqual(expected_keys, obtained_keys)

    def test_node_attribs(self):
        # 2 authors; 2 papers
        self.assertEqual(nx.number_of_nodes(self.no_attribs), 4)

        # ADAMS has 2 papers, MCLEAN has 1 paper
        self.assertEqual(nx.number_of_edges(self.no_attribs), 3)

        # 2 edges from author Adams S to his 2 papers
        # the following information is pulled from the test WoS file
        paper1_node_id = '10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2'

        # paper 1 node attributes
        atitle1 = None
        aulast1 = ['ADAMS']
        date1 = 1993
        cr1_list = ['Adams S. M., 1990, AM FISHERIES SOC S',
                    ('ADAMS SM, 1985, J FISH BIOL, V26, P111,' +
                        'DOI 10.1111/j.1095-8649.1985.tb04248.x'),
                    'ADAMS SM, 1992, ECOTOX ENVIRON SAFE, V24, P347',
                    'Adams SM, 1990, AM FISHERIES SOC S, V8, P1']
        citations1 = []
        for cite in cr1_list:
            cite_dict = rd.wos.parse_cr(cite)
            citations1.append(cite_dict)

        # and those attributes in the expected form: a 'primitive' dictionary
        paper1_expected_attribs = {'atitle':atitle1,
                                   'aulast':aulast1,
                                   'date':date1,
                                   'citations':citations1,
                                   'type':'paper'}
        paper1_expected_keys = paper1_expected_attribs.keys()
        paper1_expected_attribs = util.subdict(paper1_expected_attribs,
                                                      paper1_expected_keys)

        # and for paper 2 nodes (note ADAMS S is an author for both papers)
        paper2_node_id = '10.1111/j.1095-8649.1985.tb04248.x'

        # and paper 2 node attributes
        atitle2 = None
        aulast2 = ['Adams', 'MCLEAN']
        date2 = 1985
        cr2_list = [('CR ADAMS SM, 1982, CAN J FISH AQUAT SCI, V39,' +
                        'P1175, DOI 10.1139/f82-155'),
                    ('ADAMS SM, 1982, T AM FISH SOC, V111, P549,' +
                        'DOI 10.1577/1548-8659(1982)111<549:EPILBU>2.0.CO;2'),
                    ('ALLEN JRM, 1982, J FISH BIOL, V21, P537,' +
                        'DOI 10.1111/j.1095-8649.1982.tb02858.x')]
        citations2 = []
        for cite in cr2_list:
            cite_dict = rd.wos.parse_cr(cite)
            citations2.append(cite_dict)

        # and those attributes in the expected form: a 'primitive' dictionary
        paper2_expected_attribs = {'atitle':atitle2,
                                   'aulast':aulast2,
                                   'date':date2,
                                   'citations':citations2,
                                   'type':'paper'}
        paper2_expected_keys = paper2_expected_attribs.keys()
        paper2_expected_attribs = util.subdict(paper2_expected_attribs,
                                                      paper2_expected_keys)



        # verify the contents of paper 1
        paper1_obtained_attribs = self.node_attribs.node[paper1_node_id]
        self.assertItemsEqual(paper1_expected_attribs,
                              paper1_obtained_attribs)

        # and paper 2
        paper2_obtained_attribs = self.node_attribs.node[paper2_node_id]
        self.assertItemsEqual(paper2_expected_attribs,
                              paper2_obtained_attribs)

    def tearDown(self):
        pass


class TestCoauthorsGraph(unittest.TestCase):
    """
    Test the coauthors network, assumes reader is functioning
    The file has 2 papers in which 2 pairs of authors are co-authors in both.
    The edges attributes should contain a list which identifies each paper
    It should be a Normal graph and not a MultiGraph.
    """

    def setUp(self):

        wos_data =rd.wos.parse("../testsuite/testin/coauthors_2_recs.txt")
        meta_list = rd.wos.convert(wos_data)

        # There is no concept of user input threshold testcases as the authors \
        # will be mapped with their respective co-authors anyways.
        self.coauthors_noattribs  = nt.authors.coauthors(meta_list,)
        self.coauthors_one_attribs  = nt.authors.coauthors \
                            (meta_list,'ayjid')
        self.coauthors_three_attribs  = nt.authors.coauthors \
                            (meta_list,'ayjid','jtitle','date')

    # When no attribs are provided by the user.
    def test_coauthors_no_attribs(self):
        # 9 nodes: one for each author and his co-author
        self.assertEqual(nx.number_of_nodes(self.coauthors_noattribs), 9)
        # 26 edges between them
        self.assertEqual(nx.number_of_edges(self.coauthors_noattribs), 26)
        obtained_edge_attribs_dict = nx.get_edge_attributes \
                            (self.coauthors_noattribs,"")
        expected_edge_attribs_dict = {}
        self.assertDictEqual(expected_edge_attribs_dict, \
                        obtained_edge_attribs_dict, "Edge Attribs are equal")

    # When no attribs are provided by the user.
    def test_coauthors_one_attribs(self):
        # 9 nodes: one for each author and his co-author
        self.assertEqual(nx.number_of_nodes(self.coauthors_one_attribs),9)
        # 26 edges between them
        self.assertEqual(nx.number_of_edges(self.coauthors_one_attribs),26)
        obtained_edge_attribs_dict = nx.get_edge_attributes \
                (self.coauthors_one_attribs, "ayjid")
        expected_edge_attribs_dict = \
        {   ('JIN M', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('IZAGIRRE U', 'JIN M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('IZAGIRRE U', 'SOTO M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('MARIGOMEZ I', 'ORBEA A'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('ORBEA A', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('JIN M', 'SOTO M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('CAJARAVILLE M', 'SOTO M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('IZAGIRRE U', 'MARIGOMEZ I'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('IZAGIRRE U', 'CAJARAVILLE M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('IZAGIRRE U', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('TONG X', 'CAJARAVILLE M'):
                    ('HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'),
            ('CAJARAVILLE M', 'MARIGOMEZ I'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('JIN M', 'TONG X'):
                    'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT',
            ('JIN M', 'CAJARAVILLE M'): ['MARIGOMEZ I 2013 ECOTOXICOLOGY',
             'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'],
            ('ORBEA A', 'SOTO M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('CAJARAVILLE M', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('CAJARAVILLE M', 'ORBEA A'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('JIN M', 'ORBEA A'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('SOTO M', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('HAN D', 'JIN M'): \
                'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT',
            ('HAN D', 'CAJARAVILLE M'): \
                'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT',
            ('MARIGOMEZ I', 'GARMENDIA L'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('HAN D', 'TONG X'): \
                'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT',
            ('IZAGIRRE U', 'ORBEA A'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('JIN M', 'MARIGOMEZ I'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY',
            ('MARIGOMEZ I', 'SOTO M'): 'MARIGOMEZ I 2013 ECOTOXICOLOGY'
        }


        self.assertDictEqual(expected_edge_attribs_dict,\
                             obtained_edge_attribs_dict)


        # When three attribs are provided by the user.
    def test_coauthors_three_attribs(self):
        # 9 nodes: one for each author and his co-author
        self.assertEqual(nx.number_of_nodes(self.coauthors_three_attribs),9)
        # 26 edges between them
        self.assertEqual(nx.number_of_edges(self.coauthors_three_attribs),26)
        obtained_edge_attribs_list = \
                        self.coauthors_three_attribs.edges(data=True)
        #Need to properly format them in 80Char limit.
        expected_edge_attribs_list = \
        [('IZAGIRRE U', 'JIN M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('IZAGIRRE U', 'CAJARAVILLE M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('IZAGIRRE U', 'MARIGOMEZ I', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('IZAGIRRE U', 'ORBEA A', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('IZAGIRRE U', 'SOTO M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('IZAGIRRE U', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('HAN D', 'CAJARAVILLE M', {'date': 2013, 'ayjid': 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT', 'jtitle': 'ENVIRONMENTAL MONITORING AND ASSESSMENT'}), ('HAN D', 'JIN M', {'date': 2013, 'ayjid': 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT', 'jtitle': 'ENVIRONMENTAL MONITORING AND ASSESSMENT'}), ('HAN D', 'TONG X', {'date': 2013, 'ayjid': 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT', 'jtitle': 'ENVIRONMENTAL MONITORING AND ASSESSMENT'}), ('JIN M', 'TONG X', {'date': 2013, 'ayjid': 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT', 'jtitle': 'ENVIRONMENTAL MONITORING AND ASSESSMENT'}), ('JIN M', 'CAJARAVILLE M', {'date': [2013, 2013], 'jtitle': ['ECOTOXICOLOGY', 'ENVIRONMENTAL MONITORING AND ASSESSMENT'], 'ayjid': ['MARIGOMEZ I 2013 ECOTOXICOLOGY', 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT']}), ('JIN M', 'MARIGOMEZ I', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('JIN M', 'ORBEA A', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('JIN M', 'SOTO M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('JIN M', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('TONG X', 'CAJARAVILLE M', {'date': 2013, 'ayjid': 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT', 'jtitle': 'ENVIRONMENTAL MONITORING AND ASSESSMENT'}), ('CAJARAVILLE M', 'MARIGOMEZ I', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('CAJARAVILLE M', 'ORBEA A', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('CAJARAVILLE M', 'SOTO M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('CAJARAVILLE M', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('MARIGOMEZ I', 'ORBEA A', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('MARIGOMEZ I', 'SOTO M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('MARIGOMEZ I', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('ORBEA A', 'SOTO M', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('ORBEA A', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'}), ('SOTO M', 'GARMENDIA L', {'date': 2013, 'ayjid': 'MARIGOMEZ I 2013 ECOTOXICOLOGY', 'jtitle': 'ECOTOXICOLOGY'})]

        self.assertListEqual(expected_edge_attribs_list,obtained_edge_attribs_list)


    def tearDown(self):
            pass



class TestBiblioGraph(unittest.TestCase):
    """
    Test the bibliographic_coupling network; assumes reader is functioning

    The viewer will note that the input file has 4 papers trimmed down
    and modified from the sample //docs/savedrecs.txt.

    The references
    were constructed so that the first paper shares two citations with the
    second paper, one (of the two shared between first and second) citation
    with the third paper, and zero citations with the fourth paper.
    """
    def setUp(self):
        wos_data = rd.wos.parse('./testin/wos_biblio.txt')
        wos_meta = rd.wos.convert(wos_data)
        self.ayjid_zero = nt.papers.bibliographic_coupling(wos_meta,
                                                 'ayjid',
                                                 0,
                                                 'ayjid')
        self.ayjid_one = nt.papers.bibliographic_coupling(wos_meta,
                                               'ayjid',
                                               1,
                                               'ayjid')
        self.ayjid_two = nt.papers.bibliographic_coupling(wos_meta,
                                               'ayjid',
                                               2,
                                               'ayjid')
        self.ayjid_attribs = nt.papers.bibliographic_coupling(wos_meta,
                                                   'ayjid',
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'aulast',
                                                   'date',
                                                   'citations')
        self.weighted = nt.papers.bibliographic_coupling(wos_meta,
                                               'ayjid',
                                               0.5,
                                               'ayjid',
                                               weighted=True)

        # define a separate file for the missing citations test case
        # with the same data as the other test file with the exception
        # that the fourth paper is missing its citation record
        wos_cite = rd.wos.parse('./testin/wos_biblio_cite.txt')
        doc_list_cite = rd.wos.convert(wos_cite)
        self.missing_citations_zero = \
                nt.papers.bibliographic_coupling(doc_list_cite,
                                                             'ayjid',
                                                             0,
                                                             'ayjid')

        self.missing_citations_one = \
                    nt.papers.bibliographic_coupling(doc_list_cite,
                                                            'ayjid',
                                                            1,
                                                            'ayjid')

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
        self.assertEqual(nx.number_of_nodes(self.ayjid_one), 3)
        # first paper shares 2 >= 1 references with second, 1 >= 1 references
        # with third, and the second and third share 1 >= 1 references
        self.assertEqual(nx.number_of_edges(self.ayjid_one), 3)



    def test_ayjid_two(self):
        """
        With threshold greater than 0, two papers must share at least 1
        reference in common. Test this when threshold is 2.
        """
        self.assertEqual(nx.number_of_nodes(self.ayjid_two), 2)
        # first paper shares 2 >= 2 references with second
        self.assertEqual(nx.number_of_edges(self.ayjid_two), 1)

    def test_unweighted(self):
        """
        Unweighted similarities.
        """
        edges = self.ayjid_one.edges(data=True)
        self.assertEqual(edges[0][2]['similarity'], 2)
        self.assertEqual(edges[1][2]['similarity'], 1)
        self.assertEqual(edges[2][2]['similarity'], 1)  
    
    def test_weighted(self):
        """
        Weighted similarities.
        """
        edges = self.weighted.edges(data=True)
        self.assertEqual(edges[0][2]['similarity'], 1.0)
        self.assertEqual(edges[1][2]['similarity'], 0.5)
        self.assertEqual(edges[2][2]['similarity'], 0.5)  

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
        # paper 1 meta data
        node1_atitle = ('Marine ecosystem health status assessment' +
                        ' through integrative biomarker indices:' +
                        ' a comparative study after the Prestige oil' +
                        ' spill "Mussel Watch"')
        node1_date = 2013
        node1_aulast = ['Marigomez', 'Garmendia', 'Soto', 'Orbea',
                        'Izagirre', 'Cajaraville']
        for i in xrange(len(node1_aulast)):
            node1_aulast[i] = node1_aulast[i].upper().strip()
        node1_cr_list = [('ADAMS SM, 1993, T AM FISH SOC, V122, P63, DOI' +
                          ' 10.1577/1548-8659(1993)122<0063:AQHAIF>2.3.CO;2'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' +
                          'P1316, DOI 10.1897/1551-5028(2002)021<1316:' +
                          'IBRAUT>2.0.CO;2')]
        node1_citations = []
        for cite in node1_cr_list:
            node1_citations.append(rd.wos.parse_cr(cite))
        node1_expected_attribs = {'atitle':node1_atitle,
                                  'date':node1_date,
                                  'aulast':node1_aulast,
                                  'citations':node1_citations}
        node1_ayjid = 'MARIGOMEZ I 2013 ECOTOXICOLOGY'

        # paper 2 meta data
        node2_atitle = ('Evaluation of organic contamination in urban ' +
                        'groundwater surrounding a municipal landfill, ' +
                        'Zhoukou, China')
        node2_date = 2013
        node2_aulast = ['Han', 'Tong', 'Jin', 'Hepburn', 'Tong', 'Song']
        for i in xrange(len(node2_aulast)):
            node2_aulast[i] = node2_aulast[i].upper().strip()
        node2_cr_list = [('ADAMS SM, 1993, T AM FISH SOC, V122, P63, ' +
                          'DOI 10.1577/1548-8659(1993)122<0063:AQHAIF>' +
                          '2.3.CO;2'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' +
                          'P1316, DOI 10.1897/1551-5028(2002)021<1316:' +
                          'IBRAUT>2.0.CO;2')]
        node2_citations = []
        for cite in node2_cr_list:
            node2_citations.append(rd.wos.parse_cr(cite))
        node2_expected_attribs = {'atitle':node2_atitle,
                                  'date':node2_date,
                                  'aulast':node2_aulast,
                                  'citations':node2_citations}
        node2_ayjid = 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'

        # paper 3 meta data
        node3_atitle = ('Multilevel governance and management of shared ' +
                        'stocks with integrated markets: The European ' +
                        'anchovy case')
        node3_date = 2013
        node3_aulast = ['Mulazzani', 'Curtin', 'Andres', 'Malorgio']
        for i in xrange(len(node3_aulast)):
            node3_aulast[i] = node3_aulast[i].upper().strip()
        node3_cr_list = [('AdriaMed, GEN OUTL MAR CAPT FI'),
                         ('Beliaeff B, 2002, ENVIRON TOXICOL CHEM, V21, ' +
                          'P1316, DOI 10.1897/1551-5028(2002)021' +
                          '<1316:IBRAUT>2.0.CO;2')]
        node3_citations = []
        for cite in node3_cr_list:
            node3_citations.append(rd.wos.parse_cr(cite))
        node3_expected_attribs = {'atitle':node3_atitle,
                                  'date':node3_date,
                                  'aulast':node3_aulast,
                                  'citations':node3_citations}
        node3_ayjid = 'MULAZZANI L 2013 MARINE POLICY'

    def test_missing_citations_zero(self):
        """
        if fails network is not robust to papers missing citation data
        test for threshold = 0
        """
        # 4 papers
        self.assertEqual(nx.number_of_nodes(self.missing_citations_zero), 4)
        # 4 choose 2 = 6 edges
        self.assertEqual(nx.number_of_edges(self.missing_citations_zero), 6)


    def test_missing_citations_one(self):
        """
        if fails network is not robust to papers missing citation data
        test for threshold = 1
        """
        # 3 papers
        self.assertEqual(nx.number_of_nodes(self.missing_citations_one), 3)
        # first paper shares 2 >= 1 references with second, 1 >= 1 references
        # with third, and the second and third share 1 >= 1 references and
        # fourth constructed to have no citations
        self.assertEqual(nx.number_of_edges(self.missing_citations_one), 3)

    def tearDown(self):
        pass


class TestAuthorCouplingGraph(unittest.TestCase):
    """
    Test the author_coupling network
    Assumes reader is functioning

    the //testin/wos_author_coupling.txt file has been constructed with
    the following properties:
        the first paper shares 2 authors with the second and 1 with the third
        the second paper shares 1 author with the third
        the fourth paper shares 0 authors with any other paper
    """
    def setUp(self):
        # read data from docs folder
        wos_data = rd.wos.parse('./testin/wos_author_coupling.txt')
        meta_list = rd.wos.convert(wos_data)

        self.ayjid_zero = nt.papers.author_coupling(meta_list,
                                                0,
                                                'ayjid')

        self.ayjid_one = nt.papers.author_coupling(meta_list,
                                               1,
                                               'ayjid')

        self.ayjid_two = nt.papers.author_coupling(meta_list,
                                               2,
                                               'ayjid')

        self.ayjid_attribs = nt.papers.author_coupling(meta_list,
                                                   1,
                                                   'ayjid',
                                                   'atitle',
                                                   'date')
    def test_ayjid_zero(self):
        # with four papers there are 4 nodes
        self.assertEqual(nx.number_of_nodes(self.ayjid_zero), 4)

        # every paper shares at least 0 >= 0 authors with other papers
        # so we expect 4 choose 2 = 6 edges
        self.assertEqual(nx.number_of_edges(self.ayjid_zero), 6)

    def test_ayjid_one(self):
        # four nodes: one for each paper
        self.assertEqual(nx.number_of_nodes(self.ayjid_one), 4)

        # as noted in doc string, only papers 1 2 and 3 share one author
        # among them; we expect 3 edges
        self.assertEqual(nx.number_of_edges(self.ayjid_one), 3)

    def test_ayjid_two(self):
        # four nodes: one for each paper
        self.assertEqual(nx.number_of_nodes(self.ayjid_two), 4)

        # as noted in the doc string, one papers 1 and 2 share two authors
        # we expect 1 edge
        self.assertEqual(nx.number_of_edges(self.ayjid_two), 1)

    def test_ayjid_attribs(self):
        # paper 1 meta data
        node1_atitle = ('Marine ecosystem health status assessment' +
                        'through integrative biomarker indices: a' +
                        'comparative study after the Prestige oil' +
                        'spill "Mussel Watch"')
        node1_date = 2013
        node1_expected_attribs = {'atitle':node1_atitle,
                                  'date':node1_date}
        node1_ayjid = 'MARIGOMEZ I 2013 ECOTOXICOLOGY'

        # paper 2 meta data
        node2_atitle = ('Evaluation of organic contamination in urban' +
                        'groundwater surrounding a municipal landfill,' +
                        'Zhoukou, China')
        node2_date = 2013
        node2_expected_attribs = {'atitle':node2_atitle,
                                  'date':node2_date}
        node2_ayjid = 'HAN D 2013 ENVIRONMENTAL MONITORING AND ASSESSMENT'

        # paper 3 meta data
        node3_atitle = ('Multilevel governance and management of shared' +
                        'stocks with integrated markets: The European' +
                        'anchovy case')
        node3_date = 2013
        node3_expected_attribs = {'atitle':node3_atitle,
                                  'date':node3_date}
        node3_ayjid = 'MULAZZANI L 2013 MARINE POLICY'

        # paper 4 meta data
        node4_atitle = ('Application of multiple geochemical markers to' +
                        'investigate organic pollution in a dynamic coastal' +
                        'zone')
        node4_date = 2013
        node4_expected_attribs = {'atitle':node4_atitle,
                                  'date':node4_date}
        node4_ayjid = 'LIU L 2013 ENVIRONMENTAL TOXICOLOGY AND CHEMISTRY'

        # test attribute expectations
        node_id_list = [node1_ayjid, node2_ayjid, node3_ayjid, node4_ayjid]
        node_attrib_list = [node1_expected_attribs, node2_expected_attribs,
                            node3_expected_attribs, node4_expected_attribs]
        for i in xrange(len(node_id_list)):
            node = node_id_list[i]
            obtained_attribs = self.ayjid_attribs.node[node]
            expected_attribs = node_attrib_list[i]
            self.assertItemsEqual(expected_attribs, obtained_attribs)

    def tearDown(self):
        pass

class TestAuthorCocitation(unittest.TestCase):
    """
    Test the author cocitation (analysis) network
    Assumes reader is functioning

    testfile is
    "/Users/ramki/tethne/tethne/testsuite/testin/cocitations_test_full.txt"


     """
    def setUp(self):

        wos_data =rd.wos.parse \
                ("../testsuite/testin/cocitations_test_full.txt")
        meta_list = rd.wos.convert(wos_data)

        #No need to check edge / node attribs as there are none.

        self.cocitations_zero  = nt.authors.author_cocitation(meta_list, 0)

        self.cocitations_one  = nt.authors.author_cocitation(meta_list, 1)

        self.cocitations_two  = nt.authors.author_cocitation(meta_list, 2)

        self.cocitations_three = nt.authors.author_cocitation(meta_list, 3)


    #When the Input threshold is
    def test_cocitations_zero(self):
        # 249 nodes: one for each author and his co-author
        self.assertEqual(nx.number_of_nodes(self.cocitations_zero), 249)
        # as noted in doc string, 12 edges between them
        self.assertEqual  (nx.number_of_edges(self.cocitations_zero), 4970)
    pass


    def test_cocitations_one(self):
        # 249 nodes: one for each author and his co-author
        self.assertEqual  (nx.number_of_nodes(self.cocitations_one), 249)
        # as noted in doc string, 12 edges between them
        self.assertEqual  (nx.number_of_edges(self.cocitations_one), 4970)
    pass


    def test_cocitations_two(self):
        # 19 nodes: one for each author, one for each institution
        self.assertEqual  (nx.number_of_nodes(self.cocitations_two), 13)
        # as noted in doc string, 12 edges between them
        self.assertEqual  (nx.number_of_edges(self.cocitations_two), 41)
    pass


    def test_cocitations_three(self):
        # 19 nodes: one for each author, one for each institution
        self.assertEqual (nx.number_of_nodes(self.cocitations_three), 2)
        # as noted in doc string, 12 edges between them
        self.assertEqual (nx.number_of_edges(self.cocitations_three), 1)
    pass


class TestAuthorInstitution(unittest.TestCase):
    """
    Test the author_institutions network
    Assumes reader is functioning

    "/Users/ramki/tethne/tethne/testsuite/testin/authorinstitutions_test.txt"
    file has been constructed with
    the following properties:
        - the first paper has 6 authors and 6 institutions ,
        where one author Wu,ZD shares affiliations with
        2 other different institutions and authors.
        - the second paper has 3 authors with 2 institutions,
        where 2 authors share same affliated institution.
        - the third paper has no 'institutions' key field ,
        hence no author-institutions sharing.
        - the fourth paper has 1 author and 1 institution ,
        with no shared institutions.

    """


    # There are 10 authors with 9 institutions, as given in the doc string.

    #Nodes:
    #-------
    # As the networks is built between 10 authors and 9 institutions,
    # there should be 19 nodes (10+9). - test 1 is checked in other tests.
    # Test the node attributes - (value="author / institutions")
    # It should match with number of nodes and ----
    #--- distinguished author and institutions count
    #(value = "authors" count=10,value = "Institutions" count= 9,total19)-test 2

    #Edges:
    #------
    # To test the edges, there is no concept of providing input 'threshold'
    # from the user.
    # 12 edges ( 10 + 2 ) between the 10 authors and 9 institutions
    # where 2 authors are affliated to 2 different institutions   - test 3
    # check the edge attributes - 'Date' is an edge attribute  - test 4
    # check the edge attributes - no edge attributes are provided - test 5


    def setUp(self):
        wos_data = rd.wos.parse("./testin/authorinstitutions_test.txt")
        meta_list = rd.wos.convert(wos_data)

        self.node_attribs_check = nt.authors.author_institution(meta_list)

        self.shared_institutions  = nt.authors.author_institution(meta_list)

        self.edge_attribs_zero = nt.authors.author_institution(meta_list)

        self.edge_attribs_one = nt.authors.author_institution(meta_list,'date')




    def test_shared_institutions(self):
        # 19 nodes: one for each author, one for each institution
        self.assertEqual(nx.number_of_nodes(self.shared_institutions), \
                         19, "Nodes Equal")
        # as noted in doc string, 12 edges between them
        self.assertEqual(nx.number_of_edges(self.shared_institutions),  \
                         12, "Edges Equal")

 
    def test_node_attribs_check(self):

        obtained_node_attribs_dict = nx.get_node_attributes \
                    (self.node_attribs_check,"type")

        expected_node_attribs_dict = {'Natl Chung Cheng Univ': 'institution', \
            'Victoria Univ': 'institution',
         'ZHANG, YC': 'author', 'ACAMPORA, G': 'author', \
             'Univ Sci & Technol China': 'institution',
         'Huang, TCK': 'author', 'Eindhoven Univ Technol': 'institution',
         'XU, GD': 'author', \
             'Inst Sci & Technol Informat Zhejiang Prov': 'institution',
         'WU, ZD': 'author', 'Wenzhou Univ': 'institution', \
             'Northwestern Polytech Univ': 'institution',
          'LU, CL': 'author', 'CHEN, EH': 'author', \
              'VITIELLO, A': 'author',
          'Univ Salerno': 'institution', 'ZHANG, H': 'author',
          'LOIA, V': 'author', 'Univ Technol Sydney': 'institution'}

        self.assertDictEqual(obtained_node_attribs_dict, \
                             expected_node_attribs_dict, \
                             "Node attribs of Author institutions Equal")

    def test_edge_attribs_zero(self):

        obtained_edge_attribs_dict = \
        nx.get_edge_attributes(self.edge_attribs_zero,"")

        expected_edge_attribs_dict = {}

        self.assertDictEqual(expected_edge_attribs_dict, \
                            obtained_edge_attribs_dict, \
                            "Edge Attribs are equal")


    def test_edge_attribs_one(self):

       obtained_edge_attribs_dict = \
            nx.get_edge_attributes(self.edge_attribs_one, "date")

       expected_edge_attribs_dict = {('Wenzhou Univ', 'LU, CL'): 2012, \
            ('ACAMPORA, G', 'Eindhoven Univ Technol'): 1999,
            ('Univ Technol Sydney', 'XU, GD'): 2012,\
            ('Northwestern Polytech Univ', 'LU, CL'): 2012, \
            ('Univ Salerno', 'LOIA, V'): 1999, \
            ('ZHANG, YC', 'Victoria Univ'): 2012,\
            ('Inst Sci & Technol Informat Zhejiang Prov', 'ZHANG, H'): 2012,\
            ('WU, ZD', 'Wenzhou Univ'): 2012,
            ('Natl Chung Cheng Univ', 'Huang, TCK'): 2013, \
            ('Univ Sci & Technol China', 'CHEN, EH'): 2012, \
            ('WU, ZD', 'Univ Sci & Technol China'): 2012, \
            ('VITIELLO, A', 'Univ Salerno'): 1999}

       self.assertDictEqual(expected_edge_attribs_dict, \
                            obtained_edge_attribs_dict, \
                            "Edge Attribs are equal")


    def tearDown(self):
         pass


class TestAuthorCoinstitution(unittest.TestCase):
    """
    Test the author_coinstitution network
    Assumes reader is functioning

    the //testin/authorinstitution_testrecords.txt file is constructed with
    the following properties:
    the first paper has 6 authors and 6 institutions , \ 
    where one author Wu,ZD shares affiliations with  \ 
    2 other different institutions and authors.
    the second paper has 3 authors with 2 institutions, \
        where 2 authors share same affliated institution.
    the third paper has no 'institutions' key field \
        hence no author-institutions sharing.
    the fourth paper has 1 author and 1 institution \
        with no shared institutions.

    """

    # There are 10 authors with 9 institutions, as given in the doc string.

    #Nodes:
    #-------
    # As the networks is built only between 10 authors ,
    # there should be 10 nodes. - test 1 satisfied in all other tests
    # Test the node attributes of the author-(value="author") -test 2

    #Edges:
    #------
    # To test the edges, we need to give various options
    # for the threshold of shared institutions between them.
    # Threshold =0,  45 edges between the 10 authors(nodes) N*(N-1) /2  - test 3
    # Threshold =1,  3 edges between the authors(nodes)
    # i.e 3 authors have 1 institution shared among them - test 4
    # Threshold =2,  no edges between the authors(nodes)
    # i.e no authors have 2 institutions shared among them - test 5
    # No edge attributes, hence no tests required.


    def setUp(self):
        wos_data = rd.wos.parse("./testin/authorinstitutions_test.txt")
        meta_list = rd.wos.convert(wos_data)

        self.node_attribs_check = \
                nt.authors.author_coinstitution(meta_list, 1) # test 2

        self.shared_institutions_zero = \
                nt.authors.author_coinstitution(meta_list, 0)  # test 3

        self.shared_institutions_one = \
                nt.authors.author_coinstitution(meta_list, 1)  # test 4

        self.shared_institutions_two = \
                nt.authors.author_coinstitution(meta_list, 2)  # test 5



    def test_shared_institutions_zero(self):
        # 10 nodes: one for each author
        self.assertEqual(nx.number_of_nodes(self.shared_institutions_zero), 10)
        # as noted in doc string, 45 edges between them
        self.assertEqual(nx.number_of_edges(self.shared_institutions_zero), 45)


    def test_shared_institutions_one(self):
        # 5 nodes: #63128668
        self.assertEqual(nx.number_of_nodes(self.shared_institutions_one), 5)
        # as noted in doc string, 3 edges between them
        self.assertEqual(nx.number_of_edges(self.shared_institutions_one), 3)

    def test_shared_institutions_two(self):
        # 0 nodes: #63128668
        self.assertEqual(nx.number_of_nodes(self.shared_institutions_two), 0)
        # as noted in doc string, 0 edges between them
        self.assertEqual(nx.number_of_edges(self.shared_institutions_two), 0)

    def test_node_attribs_check(self):

        obtained_node_attribs_dict = \
            nx.get_node_attributes(self.node_attribs_check,"type")

        expected_node_attribs_dict = \
            {'WU, ZD': 'author', 'VITIELLO, A': 'author',
                'LU, CL': 'author', 'LOIA, V': 'author', 'CHEN, EH': 'author'}

        self.assertDictEqual \
        (expected_node_attribs_dict, \
                    obtained_node_attribs_dict, " Node Attribs are not same")

    def tearDown(self):
         pass


class TestCocitation(unittest.TestCase):
    """
    Test the cocitations network
    Assumes reader is functioning

    The ./testin/cocitations_test_2recs.txt file has been constructed with
    The following properties:

    There are 2 article papers in the file

    number of citations in paper1 = n1(8 in this paper)
    number of citations in paper1 = n2(9 in this paper)

    They share 4 common citations among them ( threshold =2)

    """

    # There are 2 papers with n1+n2 cited papers ( 8+9 = 17) in this case

    #Nodes:
    #-------
    # As the networks is built between cited papers , there should be 17 nodes
    # As of now there are node attributes of the paper to be tested


    #Edges:
    #------
    # To test the edges, we need to give various options for the 'threshold'
    # value in input. of cocitations  between them.
    # Threshold =0,  58 edges between the cited papers
    # Threshold =1,  58 edges between the cited papers
    # Threshold =2,  6 edges between the cited papers
    # No edge attributes as of now, hence no tests required.


    def setUp(self):

        wos_data = rd.wos.parse("./testin/cocitations_test_2recs.txt")
        meta_list = rd.wos.convert(wos_data)
        self.cocitations_zero = nt.papers.cocitation(meta_list, 0) #test 1
        self.cocitations_one = nt.papers.cocitation(meta_list, 1)  # test 2
        self.cocitations_two = nt.papers.cocitation(meta_list, 2)  # test 5




    def test_cocitations_zero(self):
        # 8+9 - 4common nodes :
        self.assertEqual(nx.number_of_nodes(self.cocitations_zero), 13)
        self.assertEqual(nx.number_of_edges(self.cocitations_zero), 58)

        #check if the edges_list is same as expected.

        obtained_edges_list = self.cocitations_zero.edges()
        expected_edges_list = \
        [('XIAO HY 2011 SOIL SEDIMENT CONTAM', \
          'ADRIANO D. 2001 TRACE ELEMENTS TERRE'),\
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM', \
          'YU HL 2007 STOCH ENV RES RISK A'), \
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM', \
          'ZOU CK 2011 TECHNOMETRICS'),\
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM',\
          'FILIPPIDIS A 1992 FUEL'), \
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM', \
          'VATALIS K. 2006 ENVIRON MANAGE'), \
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM',\
          'LANG CL 2012 NAV RES LOG'), \
         ('XIAO HY 2011 SOIL SEDIMENT CONTAM', \
          'RAO J 1992 RNEA TECHN B SER LAN'), \
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'ZOU CK 2011 TECHNOMETRICS'), \
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'FILIPPIDIS A 1992 FUEL'),\
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'VATALIS K. 2006 ENVIRON MANAGE'), \
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), \
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'LANG CL 2012 NAV RES LOG'), \
         ('YU HL 2007 STOCH ENV RES RISK A', \
          'RAO J 1992 RNEA TECHN B SER LAN'), \
         ('ZOU CK 2011 TECHNOMETRICS', \
          'VATALIS K. 2006 ENVIRON MANAGE'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), \
         ('ZOU CK 2011 TECHNOMETRICS', 'FILIPPIDIS A 1992 FUEL'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'EFRON B. 1993 INTRO BOOTSTRAP'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'LANG CL 2012 NAV RES LOG'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'FRANK A. 2010 UCI MACHINE LEARNING'), \
         ('ZOU CK 2011 TECHNOMETRICS', 'RAO J 1992 RNEA TECHN B SER LAN'),\
         ('ZOU CK 2011 TECHNOMETRICS', 'DAS N 2009 QUAL TECHNOL QUANT M'), \
         ('FILIPPIDIS A 1992 FUEL', 'VATALIS K. 2006 ENVIRON MANAGE'), \
         ('FILIPPIDIS A 1992 FUEL', 'RAO J 1992 RNEA TECHN B SER LAN'), \
         ('FILIPPIDIS A 1992 FUEL', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), \
         ('FILIPPIDIS A 1992 FUEL', 'EFRON B. 1993 INTRO BOOTSTRAP'), \
         ('FILIPPIDIS A 1992 FUEL', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'),\
         ('FILIPPIDIS A 1992 FUEL', 'LANG CL 2012 NAV RES LOG'),\
         ('FILIPPIDIS A 1992 FUEL', 'FRANK A. 2010 UCI MACHINE LEARNING'), \
         ('FILIPPIDIS A 1992 FUEL', 'DAS N 2009 QUAL TECHNOL QUANT M'),
         ('FILIPPIDIS A 1992 FUEL', 'CHAKRABORTI S 2001 J QUAL TECHNOL'),\
         ('VATALIS K. 2006 ENVIRON MANAGE', 'RAO J 1992 RNEA TECHN B SER LAN'),\
         ('VATALIS K. 2006 ENVIRON MANAGE', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'),\
         ('VATALIS K. 2006 ENVIRON MANAGE', 'LANG CL 2012 NAV RES LOG'),\
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'CHAKRABORTI S 2001 J QUAL TECHNOL'),\
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'DAS N 2009 QUAL TECHNOL QUANT M'), \
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'LANG CL 2012 NAV RES LOG'), \
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'FRANK A. 2010 UCI MACHINE LEARNING'),\
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'RAO J 1992 RNEA TECHN B SER LAN'), \
         ('EFRON B. 1993 INTRO BOOTSTRAP', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'),\
         ('ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'LANG CL 2012 NAV RES LOG'), \
         ('ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'RAO J 1992 RNEA TECHN B SER LAN'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'LANG CL 2012 NAV RES LOG'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'RAO J 1992 RNEA TECHN B SER LAN'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('LANG CL 2012 NAV RES LOG', 'RAO J 1992 RNEA TECHN B SER LAN'), ('LANG CL 2012 NAV RES LOG', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('LANG CL 2012 NAV RES LOG', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('LANG CL 2012 NAV RES LOG', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'RAO J 1992 RNEA TECHN B SER LAN'), ('RAO J 1992 RNEA TECHN B SER LAN', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('RAO J 1992 RNEA TECHN B SER LAN', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('ANGIULLI F 2005 IEEE T KNOWL DATA EN', 'CHAKRABORTI S 2001 J QUAL TECHNOL')]
        self.assertListEqual(obtained_edges_list, expected_edges_list, "Edges List is not as expected")
        #print "cocitation_zero_edges:",obtained_edges_list
        #check if the nodes_list is same as expected

        expected_nodes_list = ['XIAO HY 2011 SOIL SEDIMENT CONTAM', 'YU HL 2007 STOCH ENV RES RISK A', 'ZOU CK 2011 TECHNOMETRICS', 'FILIPPIDIS A 1992 FUEL', 'VATALIS K. 2006 ENVIRON MANAGE', 'EFRON B. 1993 INTRO BOOTSTRAP', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'DAS N 2009 QUAL TECHNOL QUANT M', 'LANG CL 2012 NAV RES LOG', 'FRANK A. 2010 UCI MACHINE LEARNING', 'RAO J 1992 RNEA TECHN B SER LAN', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN', 'CHAKRABORTI S 2001 J QUAL TECHNOL']
        obtained_nodes_list = self.cocitations_zero.nodes()
        #print "cocitation_zero:",obtained_nodes_list
        self.assertListEqual(obtained_nodes_list, expected_nodes_list, "Nodes List is as expected")


    def test_cocitations_one(self):
        # 8+9 - 4common nodes :
        self.assertEqual(nx.number_of_nodes(self.cocitations_one), 13)
        self.assertEqual(nx.number_of_edges(self.cocitations_one), 58)

        #check if the edges_list is same as expected.

        obtained_edges_list = self.cocitations_one.edges()
        
        # Need to organize this.

        expected_edges_list = [('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'YU HL 2007 STOCH ENV RES RISK A'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'ZOU CK 2011 TECHNOMETRICS'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'FILIPPIDIS A 1992 FUEL'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'VATALIS K. 2006 ENVIRON MANAGE'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'LANG CL 2012 NAV RES LOG'), ('XIAO HY 2011 SOIL SEDIMENT CONTAM', 'RAO J 1992 RNEA TECHN B SER LAN'), ('YU HL 2007 STOCH ENV RES RISK A', 'ZOU CK 2011 TECHNOMETRICS'), ('YU HL 2007 STOCH ENV RES RISK A', 'FILIPPIDIS A 1992 FUEL'), ('YU HL 2007 STOCH ENV RES RISK A', 'VATALIS K. 2006 ENVIRON MANAGE'), ('YU HL 2007 STOCH ENV RES RISK A', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), ('YU HL 2007 STOCH ENV RES RISK A', 'LANG CL 2012 NAV RES LOG'), ('YU HL 2007 STOCH ENV RES RISK A', 'RAO J 1992 RNEA TECHN B SER LAN'), ('ZOU CK 2011 TECHNOMETRICS', 'VATALIS K. 2006 ENVIRON MANAGE'), ('ZOU CK 2011 TECHNOMETRICS', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('ZOU CK 2011 TECHNOMETRICS', 'FILIPPIDIS A 1992 FUEL'), ('ZOU CK 2011 TECHNOMETRICS', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), ('ZOU CK 2011 TECHNOMETRICS', 'EFRON B. 1993 INTRO BOOTSTRAP'), ('ZOU CK 2011 TECHNOMETRICS', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('ZOU CK 2011 TECHNOMETRICS', 'LANG CL 2012 NAV RES LOG'), ('ZOU CK 2011 TECHNOMETRICS', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('ZOU CK 2011 TECHNOMETRICS', 'RAO J 1992 RNEA TECHN B SER LAN'), ('ZOU CK 2011 TECHNOMETRICS', 'DAS N 2009 QUAL TECHNOL QUANT M'), ('FILIPPIDIS A 1992 FUEL', 'VATALIS K. 2006 ENVIRON MANAGE'), ('FILIPPIDIS A 1992 FUEL', 'RAO J 1992 RNEA TECHN B SER LAN'), ('FILIPPIDIS A 1992 FUEL', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), ('FILIPPIDIS A 1992 FUEL', 'EFRON B. 1993 INTRO BOOTSTRAP'), ('FILIPPIDIS A 1992 FUEL', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('FILIPPIDIS A 1992 FUEL', 'LANG CL 2012 NAV RES LOG'), ('FILIPPIDIS A 1992 FUEL', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('FILIPPIDIS A 1992 FUEL', 'DAS N 2009 QUAL TECHNOL QUANT M'), ('FILIPPIDIS A 1992 FUEL', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('VATALIS K. 2006 ENVIRON MANAGE', 'RAO J 1992 RNEA TECHN B SER LAN'), ('VATALIS K. 2006 ENVIRON MANAGE', 'ADRIANO D. 2001 TRACE ELEMENTS TERRE'), ('VATALIS K. 2006 ENVIRON MANAGE', 'LANG CL 2012 NAV RES LOG'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'DAS N 2009 QUAL TECHNOL QUANT M'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'LANG CL 2012 NAV RES LOG'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'RAO J 1992 RNEA TECHN B SER LAN'), ('EFRON B. 1993 INTRO BOOTSTRAP', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'LANG CL 2012 NAV RES LOG'), ('ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'RAO J 1992 RNEA TECHN B SER LAN'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'LANG CL 2012 NAV RES LOG'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'RAO J 1992 RNEA TECHN B SER LAN'), ('DAS N 2009 QUAL TECHNOL QUANT M', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('LANG CL 2012 NAV RES LOG', 'RAO J 1992 RNEA TECHN B SER LAN'), ('LANG CL 2012 NAV RES LOG', 'FRANK A. 2010 UCI MACHINE LEARNING'), ('LANG CL 2012 NAV RES LOG', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('LANG CL 2012 NAV RES LOG', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('FRANK A. 2010 UCI MACHINE LEARNING', 'RAO J 1992 RNEA TECHN B SER LAN'), ('RAO J 1992 RNEA TECHN B SER LAN', 'CHAKRABORTI S 2001 J QUAL TECHNOL'), ('RAO J 1992 RNEA TECHN B SER LAN', 'ANGIULLI F 2005 IEEE T KNOWL DATA EN'), ('ANGIULLI F 2005 IEEE T KNOWL DATA EN', 'CHAKRABORTI S 2001 J QUAL TECHNOL')]
        self.assertListEqual(obtained_edges_list, expected_edges_list, \
                             "Edges List is not as expected")

        #check if the nodes_list is same as expected

        expected_nodes_list = \
            ['XIAO HY 2011 SOIL SEDIMENT CONTAM', \
            'YU HL 2007 STOCH ENV RES RISK A', \
             'ZOU CK 2011 TECHNOMETRICS', \
             'FILIPPIDIS A 1992 FUEL', \
             'VATALIS K. 2006 ENVIRON MANAGE',\
             'EFRON B. 1993 INTRO BOOTSTRAP', \
             'ADRIANO D. 2001 TRACE ELEMENTS TERRE', \
             'DAS N 2009 QUAL TECHNOL QUANT M', \
             'LANG CL 2012 NAV RES LOG', \
             'FRANK A. 2010 UCI MACHINE LEARNING',\
             'RAO J 1992 RNEA TECHN B SER LAN', \
             'ANGIULLI F 2005 IEEE T KNOWL DATA EN', \
             'CHAKRABORTI S 2001 J QUAL TECHNOL']
        obtained_nodes_list = self.cocitations_one.nodes()
        #print "cocitation_one_nodes:",obtained_nodes_list
        self.assertListEqual(obtained_nodes_list, expected_nodes_list, \
                             "Nodes List is not as expected")


    def test_cocitations_two(self):
        # 8+9 - 4common nodes :
        self.assertEqual(nx.number_of_nodes(self.cocitations_two),4)
        self.assertEqual(self.cocitations_two.number_of_edges(), 6)

        #check if the edges_list is same as expected.

        obtained_edges_list = self.cocitations_two.edges()
        expected_edges_list = \
        [('LANG CL 2012 NAV RES LOG', 'RAO J 1992 RNEA TECHN B SER LAN'), \
        ('LANG CL 2012 NAV RES LOG', 'ZOU CK 2011 TECHNOMETRICS'), \
         ('LANG CL 2012 NAV RES LOG', 'FILIPPIDIS A 1992 FUEL'), \
         ('RAO J 1992 RNEA TECHN B SER LAN', 'ZOU CK 2011 TECHNOMETRICS'),\
         ('RAO J 1992 RNEA TECHN B SER LAN', 'FILIPPIDIS A 1992 FUEL'), \
         ('ZOU CK 2011 TECHNOMETRICS', 'FILIPPIDIS A 1992 FUEL')]
        self.assertListEqual(obtained_edges_list, expected_edges_list, \
                             "Edges List is not as expected")

        #check if the nodes_list is same as expected

        expected_nodes_list = ['LANG CL 2012 NAV RES LOG', \
                               'RAO J 1992 RNEA TECHN B SER LAN', \
                               'ZOU CK 2011 TECHNOMETRICS', \
                               'FILIPPIDIS A 1992 FUEL']
        obtained_nodes_list = self.cocitations_two.nodes()
        #print "cocitation_2_nodes:",obtained_nodes_list
        self.assertListEqual(obtained_nodes_list, expected_nodes_list, \
                             "Nodes List is not as expected")



    def tearDown(self):
         pass



class TestTopCitedParameters(unittest.TestCase):
    """
        Test all the types of network
        Presently for paper_cocitations.
        Assumes reader is functioning
        
        "../testsuite/testin/paper_cocitations#62809724.txt"
        file has been constructed with
        the following properties:
        
        There are 2 papers , 3 references are cited 2 times.
        ANGIULLI F 2005 IEEE T KNOWL DATA EN
        RAO J 1992 RNEA TECHN B SER LAN
        FILIPPIDIS A 1992 FUEL
        
        """
    
    def setUp(self):
        """ Setting up"""
        
        wos_data = \
         rd.wos.parse("../testsuite/testin/paper_cocitations#62809724.txt")
        meta_list = rd.wos.convert(wos_data)
        
        # Trying with no function arguments as there are default ones.
        self.top_cited,self.citation_count = nt.papers.top_cited(meta_list)
        
        self.top_parents,self.top_cited,self.citation_count = \
                                            nt.papers.top_parents(meta_list)
        
        self.citation_count = nt.papers.citation_count(meta_list)
        
        # Trying with different function argument other than default one.
        self.top_cited_date,self.citation_count_date = \
                                 nt.papers.top_cited(meta_list,10)
                
        self.top_parents_date,self.top_cited_date,self.citation_count_date  = \
                        nt.papers.top_parents(meta_list,12)
                
        self.citation_count_date = nt.papers.citation_count(meta_list,'date')
        
        # TypeError slice indices must be integers or None or \
        #  have an __index__ method
        # This error will be encountered if a wrong value is given in \
        #  top_parents and top_cited functions
    
    
    
    def test_top_cited(self):
        obtained_list = self.top_cited
        expected_list = ['RAO J 1992 RNEA TECHN B SER LAN', \
                         'YU HL 2007 STOCH ENV RES RISK A', \
                         'CHAKRABORTI S 2001 J QUAL TECHNOL', \
                         'FILIPPIDIS A 1992 FUEL', \
                         'VATALIS K. 2006 ENVIRON MANAGE', \
                         'EFRON B. 1993 INTRO BOOTSTRAP', \
                         'ADRIANO D. 2001 TRACE ELEMENTS TERRE',\
                         'DAS N 2009 QUAL TECHNOL QUANT M', \
                         'LANG CL 2012 NAV RES LOG', \
                         'FRANK A. 2010 UCI MACHINE LEARNING', \
                         'XIAO HY 2011 SOIL SEDIMENT CONTAM', \
                         'ANGIULLI F 2005 IEEE T KNOWL DATA EN', \
                         'ZOU CK 2011 TECHNOMETRICS']
        self.assertListEqual(obtained_list, \
                              expected_list, "Edges List is not as expected")

    def test_top_cited_date(self):
        obtained_list = self.top_cited_date
        expected_list = ['RAO J 1992 RNEA TECHN B SER LAN', \
                         'YU HL 2007 STOCH ENV RES RISK A', \
                         'CHAKRABORTI S 2001 J QUAL TECHNOL', \
                         'FILIPPIDIS A 1992 FUEL', \
                         'VATALIS K. 2006 ENVIRON MANAGE', \
                         'EFRON B. 1993 INTRO BOOTSTRAP', \
                         'ADRIANO D. 2001 TRACE ELEMENTS TERRE',\
                         'DAS N 2009 QUAL TECHNOL QUANT M', \
                         'LANG CL 2012 NAV RES LOG', \
                         'FRANK A. 2010 UCI MACHINE LEARNING', \
                         'XIAO HY 2011 SOIL SEDIMENT CONTAM', \
                         'ANGIULLI F 2005 IEEE T KNOWL DATA EN', \
                         'ZOU CK 2011 TECHNOMETRICS']
        self.assertListEqual(obtained_list, \
                             expected_list, "Edges List is not as expected")


    def test_top_parents(self):
        obtained_list = []
        for p in self.top_parents:
            obtained_list.append(p['ayjid'])
        expected_list = ['MODIS K 2014 ', 'TUERHONG G 2014 ']
        self.assertListEqual(obtained_list, \
                                expected_list, "Edges List is not as expected")
        pass
    def test_top_cited_date(self):
        obtained_list = []
        for p in self.top_parents:
            obtained_list.append(p['ayjid'])
        expected_list = ['MODIS K 2014 ', 'TUERHONG G 2014 ']
        self.assertListEqual(obtained_list, \
                             expected_list, "Edges List is not as expected")
    
    def test_citation_count(self):
        expected_citations_count_dict = \
            {'XIAO HY 2011 SOIL SEDIMENT CONTAM': 1,\
                'YU HL 2007 STOCH ENV RES RISK A': 1, \
                'CHAKRABORTI S 2001 J QUAL TECHNOL': 1,\
             'FILIPPIDIS A 1992 FUEL': 2, 'VATALIS K. 2006 ENVIRON MANAGE': 1, \
                'EFRON B. 1993 INTRO BOOTSTRAP': 1, \
                'ADRIANO D. 2001 TRACE ELEMENTS TERRE': 1, \
                'DAS N 2009 QUAL TECHNOL QUANT M': 1, \
                'LANG CL 2012 NAV RES LOG': 1, \
                'FRANK A. 2010 UCI MACHINE LEARNING': 1, \
                'RAO J 1992 RNEA TECHN B SER LAN': 2, \
                'ANGIULLI F 2005 IEEE T KNOWL DATA EN': 2, \
                'ZOU CK 2011 TECHNOMETRICS': 1}
        obtained_citations_count_dict = self.citation_count
        self.assertDictEqual(expected_citations_count_dict, \
                             obtained_citations_count_dict, \
                             "Edge Attribs are equal")

    def test_citation_count_date(self):
        expected_citations_count_dict = \
            {1992: 4, 1993: 1, 2001: 2, 2005: 2, 2006: 1, 2007: 1, 2009: 1, \
                2010: 1, 2011: 2, 2012: 1}
        obtained_citations_count_dict = self.citation_count_date
        self.assertDictEqual(expected_citations_count_dict, \
                             obtained_citations_count_dict,\
                             "Edge Attribs are equal")
        




#Custom Error Defined
class NetworkXError(Exception):
    pass

if __name__ == '__main__':
    unittest.main()
