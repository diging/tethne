import unittest
import tethne.crossref as cr

class TestCrossrefQuery(unittest.TestCase):
    """
    Tests a sample query with a known DOI number
    The query is based on an early sample record from Pubmed
    """
    def setUp(self):
        author = 'Griffiths'
        title = 'Seasonal changes in the carotenoids of the sea urchin'
        journal = ('Comparative Biochemistry and Physiology Part B: ' +
                   'Comparative Biochemistry')
        year = 1976
        volume = 55
        fpage = 435
        self.doi = cr.query(aulast=author, atitle = title, jtitle=journal, 
                            volume=volume, spage=fpage, date=year)
    def test_query(self):
        self.assertEqual(self.doi, '10.1016/0305-0491(76)90317-5')

if __name__ == '__main__':
    unittest.main()
