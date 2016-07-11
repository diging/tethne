import sys
sys.path.append('./')

import unittest
from tethne import GraphCollection
from tethne.readers.wos import read
from tethne import coauthors
from tethne.analyze.collection import attachment_probability
from collections import Counter

datapath = './tethne/tests/data/wos_altman_yale.txt'


class TestAttachmentProbability(unittest.TestCase):
    def setUp(self):
        self.corpus = read(datapath)
        self.collection = GraphCollection(self.corpus, coauthors)

    def test_attachment_probability(self):
        result = attachment_probability(self.collection, raw=True)

        # The result set should be a dictionary with the same keys as the
        #  GraphCollection.
        self.assertIsInstance(result, dict)
        self.assertEqual(result.keys(), self.collection.keys())

        for key, value in result.iteritems():
            # The result set for each year should be a dict mapping node IDs
            #  onto attachment probability values.
            self.assertIsInstance(value, dict)

            # There should be a result for each node in each year, even if that
            #  result is 0.
            self.assertEqual(sorted(value.keys()),
                             sorted(self.collection[key].nodes()))

            # The nodes in each graph in the collection should be updated
            #  in-place with an ``attachment_probability`` attribute.
            for k, v in value.iteritems():
                self.assertIsInstance(v, float)
                self.assertIn('attachment_probability',
                              self.collection[key].node[k])

        node_8 = self.collection.values()[0].node[8]
        self.assertEqual(node_8['attachment_probability'], 1.)


if __name__ == '__main__':
    unittest.main()
