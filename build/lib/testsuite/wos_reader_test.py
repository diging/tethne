import unittest
import tethne.readers as rd
import tethne.utilities as util
import os
from pprint import pprint


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

        # No authors in the C1 field and the N authors must be mapped with
        # 1 institution - N-1 Mapping

        institutions = self.meta_list[3]['institutions']
        expected_dict4 = {'Huang, TCK': ['Natl Chung Cheng Univ']}

        #Check if the expected and resulted 'institutions' field are the same.
        #self.assertListEqual(institutions, expected_dict4,"Not equal")
        self.assertDictEqual(institutions, expected_dict4,"Not equal")
    

    

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

# Cases for parsing files from a directory.

    def test_from_dir(self):
    
        self.dir_path = "../testsuite/testin/only3"
        self.wrong_path = "../testsuite/testin232/only3"
        
        # Check if objects
        a  = rd.wos.from_dir(self.dir_path)
        self.assertIsInstance(a,type(a), msg="yes it is a list of objects")
        
        ayjid_list = []
        for obj in a :
            ayjid_list.append(obj['ayjid'])
            
                
        # NEED TO FORMAT THESE. 
        expected_ayjid_list = ['MODIS K 2014 ', 'TUERHONG G 2014 ', 'WU Z 2013 NEUROCOMPUTING', 'ACAMPORA G 2013 INFORMATION SCIENCES', 'HRISTOSKOVA A 2013 AUTOMATED SOFTWARE ENGINEERING', 'SUN F 2013 NEUROCOMPUTING', 'WU Z 2013 NEUROCOMPUTING', 'ACAMPORA G 2013 INFORMATION SCIENCES', 'ZADEH P 2013 INFORMATION SCIENCES', 'KEATOR D 2013 NEUROIMAGE', 'POELMANS J 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'SANCHEZ D 2013 INFORMATION SCIENCES', 'DENG J 2013 IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING', 'TAHIR A 2013 JOURNAL OF SYSTEMS AND SOFTWARE', 'ZHONG Y 2013 COMPUTER-AIDED DESIGN', 'HAN L 2013 ADVANCES IN ENGINEERING SOFTWARE', 'RIOS-ALVARADO A 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DUAN J 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'ABANDA F 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DUTTA R 2013 IEEE SENSORS JOURNAL', 'KARLA P 2013 JOURNAL OF MEDICAL SYSTEMS', 'CHENG S 2013 WIRELESS PERSONAL COMMUNICATIONS', 'SINACI A 2013 JOURNAL OF BIOMEDICAL INFORMATICS', 'TAO C 2013 JOURNAL OF BIOMEDICAL INFORMATICS', 'BALLATORE A 2013 KNOWLEDGE AND INFORMATION SYSTEMS', 'GOASDOUE F 2013 VLDB JOURNAL', 'FURCHE T 2013 VLDB JOURNAL', 'BOZZON A 2013 VLDB JOURNAL', 'GRACY K 2013 JOURNAL OF THE AMERICAN SOCIETY FOR INFORMATION SCIENCE AND TECHNOLOGY', 'GUNS R 2013 JOURNAL OF THE AMERICAN SOCIETY FOR INFORMATION SCIENCE AND TECHNOLOGY', 'CUXAC P 2013 SCIENTOMETRICS', 'CASES M 2013 JOURNAL OF INTERNAL MEDICINE', 'FELBER P 2013 SOFTWARE-PRACTICE & EXPERIENCE', 'VIZCARRA J 2013 JOURNAL OF WEB ENGINEERING', 'MANGIONE G 2013 JOURNAL OF WEB ENGINEERING', 'ZHANG Z 2013 NATURAL LANGUAGE ENGINEERING', 'ANGROSH M 2013 NATURAL LANGUAGE ENGINEERING', 'CHEN Y 2013 IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING', 'LAZNIK J 2013 INFORMATION AND SOFTWARE TECHNOLOGY', 'KOLOZALI S 2013 IEEE TRANSACTIONS ON AUDIO SPEECH AND LANGUAGE PROCESSING', 'MAZANDU G 2013 BMC BIOINFORMATICS', 'BOLLEGALA D 2013 PLOS ONE', 'THORLEUCHTER D 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DIXON B 2013 ARTIFICIAL INTELLIGENCE IN MEDICINE', 'MARTELL R 2013 CLINICAL THERAPEUTICS', 'FARNAGHI M 2013 COMPUTERS ENVIRONMENT AND URBAN SYSTEMS', 'KHATTAK A 2013 JOURNAL OF INFORMATION SCIENCE AND ENGINEERING', 'ZHANG J 2013 CANADIAN JOURNAL OF INFORMATION AND LIBRARY SCIENCE-REVUE CANADIENNE DES SCIENCES DE L INFORMATION ET DE BIBLIOTHECONOMIE', 'AZZAOUI K 2013 DRUG DISCOVERY TODAY', 'ZHANG C 2013 JOURNAL OF COMPUTER SCIENCE AND TECHNOLOGY', 'ZHANG J 2013 JOURNAL OF COMPUTER SCIENCE AND TECHNOLOGY', 'BOBILLO F 2013 APPLIED SOFT COMPUTING', 'KHAN W 2013 COMPUTING', 'YUE P 2013 ISPRS JOURNAL OF PHOTOGRAMMETRY AND REMOTE SENSING']
                
        self.assertSetEqual(set(ayjid_list),set(expected_ayjid_list), \
                            "AYJID list is not as expected")
        
        # Check for OS Error if there is no such file or directory
        with self.assertRaises(OSError):
            a = rd.wos.from_dir(self.wrong_path)
    
    

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
