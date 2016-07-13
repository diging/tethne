import sys
sys.path.append('../tethne')

import re

import unittest
from tethne.readers.plain_text import read
from tethne import Corpus, Paper, Feature, FeatureSet, StructuredFeature, StructuredFeatureSet

datapath = './tethne/tests/data/plain_text'


class TestWoSParser(unittest.TestCase):
    def test_read(self):
        corpus = read(datapath)
        self.assertIsInstance(corpus, Corpus)
        self.assertIn('plain_text', corpus.features)
        self.assertEqual(len(corpus.features['plain_text'].features), len(corpus))
        for paper in corpus:
            self.assertTrue(hasattr(paper, 'fileid'))
            self.assertIn(paper.fileid, corpus.features['plain_text'].features)

    def test_read_nocorpus(self):
        papers, featureset = read(datapath, corpus=False)
        self.assertIsInstance(papers, list)
        self.assertIsInstance(papers[0], Paper)
        self.assertIsInstance(featureset, StructuredFeatureSet)

    def test_read_extractor(self):
        def extractor(fileid):
            name, title = fileid.split('__')
            return {'name': name, 'title': title}
        corpus = read(datapath, extractor=extractor)
        for paper in corpus:
            self.assertTrue(hasattr(paper, 'name'))
            self.assertTrue(hasattr(paper, 'title'))

    def test_model(self):
        from tethne import LDAModel
        corpus = read(datapath)
        model = LDAModel(corpus, featureset_name='plain_text')
        model.fit(Z=5, max_iter=200)
        model.list_topics()


if __name__ == '__main__':
    unittest.main()
