import unittest
import tethne.readers as rd
import tethne.utilities as util
import os


class TestConvert(unittest.TestCase):

    def setUp(self):
       filepath =  "./testin/authorinstitutions_test.txt"
       self.wos_list  = rd.wos.parse(filepath)
       self.meta_list = rd.wos.convert(self.wos_list)


    def test_institutions_1(self):
        # Define expected values for C1 meta_dict key
        # CASES : TESTED
        # Overlapping of authors - whether append works correctly or not
        # KeyError is not creating exception issues.

        institutions = self.meta_list[0]['institutions']

        expected_dict1 =  {'ZHANG, YC': ['Victoria Univ'],\
                            'WU, ZD': \
                                ['Wenzhou Univ', 'Univ Sci & Technol China'],
                            'LU, CL': \
                                ['Wenzhou Univ', 'Northwestern Polytech Univ'],
                            'CHEN, EH': ['Univ Sci & Technol China'],
                            'ZHANG, H': \
                                ['Inst Sci & Technol Informat Zhejiang Prov'],
                            'XU, GD': ['Univ Technol Sydney']}

        self.assertDictEqual(institutions, expected_dict1,"Not equal")

        # Writing the remaining tests.

    def test_institutions_2(self):
        # Define expected values for C1 meta_dict key
        # 2 authors - 2 institutions .. both should be mapped.
        # No overlapping or missing out of expected mappings.

        institutions = self.meta_list[1]['institutions']
        expected_dict2 =  {'VITIELLO, A': ['Univ Salerno'],\
                            'LOIA, V': ['Univ Salerno'], \
                            'ACAMPORA, G': ['Eindhoven Univ Technol']}

        # Check if the expected and resulted 'institutions' field are the same.
        # Changed to Dict Check from List check
        self.assertDictEqual(institutions, expected_dict2,"Not equal")

   # Commented the following block as it will throw Key Error ( as expected).
   # We can uncomment it anytime.
   #============================================================================

    def test_institutions_3(self):
        # define expected values for C1 meta_dict key

        # CASES : TESTED
        # What if the record did not contain C1 input field info.
        institutions = self.meta_list[2]['institutions']
        expected_dict3 = {}
        try:
           institutions = self.meta_list[2]['institutions']
        except AssertationError:
           self.assertDictEqual(institutions, expected_dict3,"Not equal")


    def test_institutions_4(self):
        # define expected values for C1 meta_dict key

        # No authors in the C1 field and the N authors must be mapped with 1 institution - N-1 Mapping

        institutions = self.meta_list[3]['institutions']
        expected_dict4 = {'Huang, TCK': ['Natl Chung Cheng Univ']}

        #Check if the expected and resulted 'institutions' field are the same.
        #self.assertListEqual(institutions, expected_dict4,"Not equal")
        self.assertDictEqual(institutions, expected_dict4,"Not equal")
    def tearDown(self):
        pass

# Commenting the Pubmed test cases as of now.
#
#class TestPubmedXmlParse(unittest.TestCase):
#
#    def setUp(self):
#       filepath = './testin/pmc_sample1.xml'
#       self.meta_list = rd.pubmed.parse_pubmed_xml(filepath)
#
#    def test_schema_validation(self):
#        pass
#
#    def test_sample1_front(self):
#        # define expected values for each meta_dict key
#        # citations left out for front matter test
#        expected = {'aulast':['Peng', 'Yuan', 'Wang'],
#                    'auinit':['J', 'J', 'J'],
#                    'atitle':('Effect of Diets Supplemented with Different' +
#                              ' Sources of Astaxanthin on the Gonad of the' +
#                              ' Sea Urchin Anthocidaris crassispina'),
#                    'jtitle':'Nutrients',
#                    'volume':4,
#                    'issue':8,
#                    'spage':922,
#                    'epage':934,
#                    'date':2012,
#                    'ayjid':'Peng J 2012 Nutrients',
#                    'doi':'10.3390/nu4080922',
#                    'pmid':23016124,
#                    'wosid':None}
#
#        obtained = self.meta_list[0]
#        for key in expected.iterkeys():
#            self.assertEqual(expected[key], obtained[key])
#
#    def test_sample1_back(self):
#        pass
#
#    def test_sample2_result(self):
#        pass
#
#    def tearDown(self):
#        pass
#




if __name__ == '__main__':
    unittest.main()
