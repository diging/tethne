import unittest
import tethne.readers as rd

class TestPubmedXmlParse(unittest.TestCase):

    def setUp(self):
       filepath = './testin/pmc_sample1.xml' 
       self.meta_list = rd.parse_pubmed_xml(filepath)

    def test_schema_validation(self):
        pass

    def test_sample1_front(self):
        # define expected values for each meta_dict key
        # citations left out for front matter test
        expected = {'aulast':['Peng', 'Yuan', 'Wang'],
                    'auinit':['J', 'J', 'J'],
                    'atitle':('Effect of Diets Supplemented with Different' +
                              ' Sources of Astaxanthin on the Gonad of the' +
                              ' Sea Urchin Anthocidaris crassispina'),
                    'jtitle':'Nutrients',
                    'volume':4,
                    'issue':8,
                    'spage':922,
                    'epage':934,
                    'date':2012,
                    'ayjid':'Peng J 2012 Nutrients',
                    'doi':'10.3390/nu4080922',
                    'pmid':23016124,
                    'wosid':None}

        obtained = self.meta_list[0]
        for key in expected.iterkeys():
            self.assertEqual(expected[key], obtained[key])

    def test_sample1_back(self):
        pass

    def test_sample2_result(self):
        pass

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
