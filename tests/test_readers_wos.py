from settings import *

# TODO: Cleanup and update these tests.

import unittest
import tethne.readers as rd
import tethne.utilities as util
import os
from pprint import pprint


class TestConvert(unittest.TestCase):

    def setUp(self):
       filepath =  "./tests/testin/authorinstitutions_test.txt"
       self.wos_list  = rd.wos.parse(filepath)
       self.meta_list = rd.wos.convert(self.wos_list)


    def test_institutions_1(self):
        # Define expected values for C1 meta_dict key
        # CASES : TESTED
        # Overlapping of authors - whether append works correctly or not
        # KeyError is not creating exception issues.

        institutions = self.meta_list[0]['institutions']

        expected_dict1 =  {'CHEN EH': ['UNIV SCI & TECHNOL CHINA, PEOPLES R CHINA'], 'XU GD': ['UNIV TECHNOL SYDNEY, AUSTRALIA'], 'ZHANG YC': ['VICTORIA UNIV, AUSTRALIA'], 'LU CL': ['WENZHOU UNIV, PEOPLES R CHINA', 'NORTHWESTERN POLYTECH UNIV, PEOPLES R CHINA'], 'ZHANG H': ['INST SCI & TECHNOL INFORMAT ZHEJIANG PROV, PEOPLES R CHINA'], 'WU ZD': ['WENZHOU UNIV, PEOPLES R CHINA', 'UNIV SCI & TECHNOL CHINA, PEOPLES R CHINA']}

        self.assertDictEqual(institutions, expected_dict1,"Not equal")

        # Writing the remaining tests.

    def test_institutions_2(self):
        # Define expected values for C1 meta_dict key
        # 2 authors - 2 institutions .. both should be mapped.
        # No overlapping or missing out of expected mappings.

        institutions = self.meta_list[1]['institutions']
        expected_dict2 =  {'LOIA V': ['UNIV SALERNO, ITALY'], 'ACAMPORA G': ['EINDHOVEN UNIV TECHNOL, NETHERLANDS'], 'VITIELLO A': ['UNIV SALERNO, ITALY']}

        # Check if the expected and resulted 'institutions' field are the same.
        # Changed to Dict Check from List check
        self.assertDictEqual(institutions, expected_dict2,"Not equal")

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
        expected_dict4 = {'HUANG TCK': ['NATL CHUNG CHENG UNIV, TAIWAN']}

        #Check if the expected and resulted 'institutions' field are the same.
        #self.assertListEqual(institutions, expected_dict4,"Not equal")
        self.assertDictEqual(institutions, expected_dict4,"Not equal")

# Cases for parsing files from a directory.

    def test_from_dir(self):
    
        self.dir_path = "./tests/testin/only3"
        self.wrong_path = "./tests/testin232/only3"
        
        # Check if objects
        a  = rd.wos.from_dir(self.dir_path)
        self.assertIsInstance(a,type(a), msg="yes it is a list of objects")
        
        ayjid_list = []
        for obj in a :
            ayjid_list.append(obj['ayjid'])
            
                
        # NEED TO FORMAT THESE. 
        expected_ayjid_list = ['MODIS K 2014 ', 'TUERHONG G 2014 ', 'WU ZD 2013 NEUROCOMPUTING', 'ACAMPORA G 2013 INFORMATION SCIENCES', 'HRISTOSKOVA A 2013 AUTOMATED SOFTWARE ENGINEERING', 'SUN FM 2013 NEUROCOMPUTING', 'WU ZD 2013 NEUROCOMPUTING', 'ACAMPORA G 2013 INFORMATION SCIENCES', 'ZADEH PDH 2013 INFORMATION SCIENCES', 'KEATOR DB 2013 NEUROIMAGE', 'POELMANS J 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'SANCHEZ D 2013 INFORMATION SCIENCES', 'DENG JT 2013 IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING', 'TAHIR A 2013 JOURNAL OF SYSTEMS AND SOFTWARE', 'ZHONG YR 2013 COMPUTER-AIDED DESIGN', 'HAN LX 2013 ADVANCES IN ENGINEERING SOFTWARE', 'RIOS-ALVARADO AB 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DUAN JJ 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'ABANDA FH 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DUTTA R 2013 IEEE SENSORS JOURNAL', 'KARLA PR 2013 JOURNAL OF MEDICAL SYSTEMS', 'CHENG ST 2013 WIRELESS PERSONAL COMMUNICATIONS', 'SINACI AA 2013 JOURNAL OF BIOMEDICAL INFORMATICS', 'TAO C 2013 JOURNAL OF BIOMEDICAL INFORMATICS', 'BALLATORE A 2013 KNOWLEDGE AND INFORMATION SYSTEMS', 'GOASDOUE F 2013 VLDB JOURNAL', 'FURCHE T 2013 VLDB JOURNAL', 'BOZZON A 2013 VLDB JOURNAL', 'GRACY KF 2013 JOURNAL OF THE AMERICAN SOCIETY FOR INFORMATION SCIENCE AND TECHNOLOGY', 'GUNS R 2013 JOURNAL OF THE AMERICAN SOCIETY FOR INFORMATION SCIENCE AND TECHNOLOGY', 'CUXAC P 2013 SCIENTOMETRICS', 'CASES M 2013 JOURNAL OF INTERNAL MEDICINE', 'FELBER P 2013 SOFTWARE-PRACTICE & EXPERIENCE', 'VIZCARRA J 2013 JOURNAL OF WEB ENGINEERING', 'MANGIONE GR 2013 JOURNAL OF WEB ENGINEERING', 'ZHANG ZQ 2013 NATURAL LANGUAGE ENGINEERING', 'ANGROSH MA 2013 NATURAL LANGUAGE ENGINEERING', 'CHEN YX 2013 IEEE TRANSACTIONS ON KNOWLEDGE AND DATA ENGINEERING', 'LAZNIK J 2013 INFORMATION AND SOFTWARE TECHNOLOGY', 'KOLOZALI S 2013 IEEE TRANSACTIONS ON AUDIO SPEECH AND LANGUAGE PROCESSING', 'MAZANDU GK 2013 BMC BIOINFORMATICS', 'BOLLEGALA D 2013 PLOS ONE', 'THORLEUCHTER D 2013 EXPERT SYSTEMS WITH APPLICATIONS', 'DIXON BE 2013 ARTIFICIAL INTELLIGENCE IN MEDICINE', 'MARTELL RE 2013 CLINICAL THERAPEUTICS', 'FARNAGHI M 2013 COMPUTERS ENVIRONMENT AND URBAN SYSTEMS', 'KHATTAK AM 2013 JOURNAL OF INFORMATION SCIENCE AND ENGINEERING', 'ZHANG J 2013 CANADIAN JOURNAL OF INFORMATION AND LIBRARY SCIENCE-REVUE CANADIENNE DES SCIENCES DE L INFORMATION ET DE BIBLIOTHECONOMIE', 'AZZAOUI K 2013 DRUG DISCOVERY TODAY', 'ZHANG CD 2013 JOURNAL OF COMPUTER SCIENCE AND TECHNOLOGY', 'ZHANG JJ 2013 JOURNAL OF COMPUTER SCIENCE AND TECHNOLOGY', 'BOBILLO F 2013 APPLIED SOFT COMPUTING', 'KHAN WA 2013 COMPUTING', 'YUE P 2013 ISPRS JOURNAL OF PHOTOGRAMMETRY AND REMOTE SENSING']
        
        self.assertSetEqual(set(ayjid_list),set(expected_ayjid_list), \
                            "AYJID list is not as expected")
        
        # Check for OS Error if there is no such file or directory
        with self.assertRaises(OSError):
            a = rd.wos.from_dir(self.wrong_path)

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
