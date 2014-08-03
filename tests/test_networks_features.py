from settings import *

import unittest
from tethne.readers import dfr
from tethne.networks.features import *
from tethne.writers.graph import to_graphml

corpus = dfr.read_corpus(datapath+'/dfr', features=['uni'])
corpus.filter_features('unigrams', 'unigrams_filt')
corpus.transform('unigrams_filt', 'unigrams_tfidf')

class TestPMI(unittest.TestCase):
    def test_coo(self):
        featureset = corpus.features['unigrams_tfidf']
        papers = corpus.all_papers()

#        g = coo(papers, featureset)
        graph = pointwise_mutual_information(papers, featureset)
        to_graphml(graph, datapath + '/test.graphml')

#    def test_npmi(self):
#        featureset = corpus.features['unigrams']
#        papers = corpus.all_papers()
#        g = pointwise_mutual_information(papers, featureset)

if __name__ == '__main__':
    unittest.main()