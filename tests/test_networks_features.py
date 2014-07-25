from settings import *

import unittest
from tethne.readers import dfr
from tethne.networks.features import pointwise_mutual_information

corpus = dfr.read_corpus(datapath+'/dfr', features=['uni'])

class TestPMI(unittest.TestCase):
    def test_npmi(self):
        featureset = corpus.features['unigrams']
        papers = corpus.all_papers()
        g = pointwise_mutual_information(papers, featureset)

if __name__ == '__main__':
    unittest.main()