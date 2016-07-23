import unittest, sys
sys.path.append('../tethne')

from tethne.readers import wos


datapath = 'tethne/tests/data/21001-21500.txt'


class TestAYJID(unittest.TestCase):
    def test_ayjid(self):
        corpus = wos.read(datapath)
        for paper in corpus:
            getattr(paper, 'ayjid')
            for reference in paper.citedReferences:    
                getattr(reference, 'ayjid')

if __name__ == '__main__':
    unittest.main()
