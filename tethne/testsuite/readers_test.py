import unittest
import tethne.readers as rd
import tethne.utilities as util
import networkx as nx
import os
import os.path


class Testwos2meta(unittest.TestCase):

    def setUp(self):
       filepath = '/Users/ramki/tethne/tethne/testsuite/testin/semantic_web.txt' 
       self.wos_list  = rd.parse_wos(filepath)
       self.meta_list = rd.wos2meta(self.wos_list)
       
       
    
    def test_institutions_1(self):
        # define expected values for C1 meta_dict key
        # citations left out for front matter test
        expected_dict = {'institutions': {  'ZHANG, YC': ['Victoria Univ'], 
                                            'WU, ZD': ['Wenzhou Univ', 'Univ Sci & Technol China'],   
                                            'LU, CL': ['Wenzhou Univ', 'Northwestern Polytech Univ'], 
                                            'CHEN, EH': ['Univ Sci & Technol China'],
                                            'ZHANG, H': ['Inst Sci & Technol Informat Zhejiang Prov'], 
                                            'XU, GD': ['Univ Technol Sydney']}
                        }
        
        input_dict = {'C1': ['[Wu, Zongda; Lu, Chenglang] Wenzhou Univ, Wenzhou 325035, Peoples R China.', 
                             '[Wu, Zongda; Chen, Enhong] Univ Sci & Technol China, Hefei 230026, Anhui, Peoples R China.', 
                             '[Xu, Guandong] Univ Technol Sydney, Sydney, NSW 2007, Australia.', 
                             '[Lu, Chenglang] Northwestern Polytech Univ, Xian 710072, Peoples R China.', 
                             '[Zhang, Yanchun] Victoria Univ, Melbourne, Vic 8001, Australia.', 
                             '[Zhang, Hong] Inst Sci & Technol Informat Zhejiang Prov, Hangzhou 310006, Zhejiang, Peoples R China.']
                    }
        
        #assign obtained dict
        for key,val in self.meta_list[]:
            
        
        
        #for i in len(self.meta_list):
        #    obtained_dict = self.meta_list[i].index('institutions')
        #for key in expected.iterkeys():
         #   self.assertEqual(expected[key], obtained[key])

    def test_sample1_back(self):
        pass

    def test_sample2_result(self):
        pass

    def tearDown(self):
        pass


#===============================================================================
# class TestPubmedXmlParse(unittest.TestCase):
# 
#     def setUp(self):
#        filepath = './testin/pmc_sample1.xml' 
#        self.meta_list = rd.parse_pubmed_xml(filepath)
# 
#     def test_schema_validation(self):
#         pass
# 
#     def test_sample1_front(self):
#         # define expected values for each meta_dict key
#         # citations left out for front matter test
#         expected = {'aulast':['Peng', 'Yuan', 'Wang'],
#                     'auinit':['J', 'J', 'J'],
#                     'atitle':('Effect of Diets Supplemented with Different' +
#                               ' Sources of Astaxanthin on the Gonad of the' +
#                               ' Sea Urchin Anthocidaris crassispina'),
#                     'jtitle':'Nutrients',
#                     'volume':4,
#                     'issue':8,
#                     'spage':922,
#                     'epage':934,
#                     'date':2012,
#                     'ayjid':'Peng J 2012 Nutrients',
#                     'doi':'10.3390/nu4080922',
#                     'pmid':23016124,
#                     'wosid':None}
# 
#         obtained = self.meta_list[0]
#         for key in expected.iterkeys():
#             self.assertEqual(expected[key], obtained[key])
# 
#     def test_sample1_back(self):
#         pass
# 
#     def test_sample2_result(self):
#         pass
# 
#     def tearDown(self):
#         pass
#===============================================================================





if __name__ == '__main__':
    unittest.main()
