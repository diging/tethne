import sys
sys.path.append('../tethne')

import unittest
import csv

from unidecode import unidecode

from tethne.readers import scopus
from tethne import Corpus, Paper, Feature, FeatureSet


scopus_datapath = './tethne/tests/data/scopus.csv'



class MyTestCase(unittest.TestCase):
    def setUp(self):
       rawdata = []
       with open(scopus_datapath, 'rb') as f:
            reader = csv.reader(f)
            for row in reader:
                rawdata.append([ unidecode(r.decode('UTF-8')) for r in row ])
       headers = rawdata[0]
       datum = rawdata[1]
       self.rawdatum = {headers[i]:datum[i] for i in xrange(len(headers))}

'''

    def test_reader(self):
        """
        PURPOSE : To test the Scopus reader functionality.

        TESTED FOR : Return Type.

        Returns
        -------
        List of Papers.

        """
        papers = scopus.read(scopus_datapath)
        self.assertIsNotNone(papers)
        self.assertIsInstance(papers[0], Paper)

    def test_handle_Authors(self):
        """
        PURPOSE :
        To test the Scopus-Reader handle_authors functionality

        TESTED FOR:
        The 2 lists returned for the Author's LAST NAME and INIT-name are not none.

        Returns
        -------
        List of author's LAST and INIT name.

        """
        paper = Paper()
        paper['aulast'], paper['auinit'] = scopus._handle_authors(self.rawdatum['Authors'])
        self.assertIsNotNone(paper['aulast'])
        self.assertIsNotNone(paper['auinit'])
        paper['aulast'] = filter(None, paper['aulast'])
        paper['auinit'] = filter(None, paper['auinit'])
        self.assertGreater(len(paper['aulast']), 0)
        self.assertGreater(len(paper['auinit']), 0)



    def test_handle_Affiliations(self):
        """
        PURPOSE : To test the Scopus-Reader handle_affiliations functionality

        TESTED FOR: The list of institutions returned should not be none.


        Returns
        -------

        """
        paper = Paper()
        paper['aulast'], paper['auinit'] = scopus._handle_authors(self.rawdatum['Authors'])
        paper['institutions'] = scopus._handle_affiliations(
                self.rawdatum['Authors with affiliations'], paper['aulast'], paper['auinit'])
        self.assertIsNotNone(paper['institutions'])
        paper['institutions'] = filter(None, paper['institutions'])
        self.assertGreater(len(paper['institutions']), 0)

'''

if __name__ == '__main__':
    unittest.main()
