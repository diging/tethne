import unittest

import sys
sys.path.append('../../')

from tethne.readers.dfr import read, ngrams, GramGenerator

# Set log level to ERROR to avoid debug output.
import logging
logging.basicConfig()
logger = logging.getLogger('tethne.readers.dfr')
#logger.setLevel('ERROR')

#class TestNGrams(unittest.TestCase):
#    def setUp(self):
#        self.dfrdatapath = '{0}/dfr'.format(datapath)
#
#    def test_ngrams_heavy(self):
#        """
#        In 'heavy' mode (default), :func:`.ngrams` should return a dict.
#        """
#        self.unigrams = ngrams(self.dfrdatapath, N='uni')    
#        self.assertEqual(len(self.unigrams), 241)
#        self.assertIsInstance(self.unigrams, dict)
#        self.assertIsInstance(self.unigrams.values()[0], list)
#        self.assertIsInstance(self.unigrams.values()[0][0], tuple)
#        
#    def test_ngrams_light(self):
#        """
#        'light' mode should behave just like 'heavy'
#        """
#        self.unigrams = ngrams(self.dfrdatapath, N='uni', mode='light')
#        self.assertEqual(len(self.unigrams), 241)
#        self.assertIsInstance(self.unigrams, GramGenerator)
#        self.assertIsInstance(self.unigrams.values()[0], list)
#        self.assertIsInstance(self.unigrams.values()[0][0], tuple)    
        
class TestGramGenerator(unittest.TestCase):
    def setUp(self):
        self.dfrdatapath = '{0}/dfr'.format(datapath)
        
    def test_len(self):
        """
        Should return the number of XML files in /wordcounts
        """
        g = GramGenerator(self.dfrdatapath+'/wordcounts', 'wordcount')
        self.assertEqual(len(g), 241)
    
    def test_items(self):
        """
        :func:`GramGenerator.items` should return a new indexable
        :class:`.GramGenerator` that returns tuples.
        """
        g = GramGenerator(self.dfrdatapath+'/wordcounts', 'wordcount')
        self.assertIsInstance(g.items(), GramGenerator)
        self.assertIsInstance(g.items()[0], tuple)
        
    def test_iteritems(self):
        """
        :func:`GramGenerator.iteritems` should return a new indexable
        :class:`.GramGenerator` that returns tuples.
        """
        g = GramGenerator(self.dfrdatapath+'/wordcounts', 'wordcount')
        self.assertIsInstance(g.iteritems(), GramGenerator)
        self.assertIsInstance(g.items()[0], tuple)                

    def test_values(self):
        """
        :func:`GramGenerator.values` should return a new indexable
        :class:`.GramGenerator` that returns lists of tuples.
        """
        g = GramGenerator(self.dfrdatapath+'/wordcounts', 'wordcount')
        self.assertIsInstance(g.values(), GramGenerator)    
        self.assertIsInstance(g.values()[0], list)                
        self.assertIsInstance(g.values()[0][0], tuple)  
        
    def test_keys(self):
        """
        :func:`GramGenerator.keys` should return a new indexable
        :class:`.GramGenerator` that returns strings.
        """
        g = GramGenerator(self.dfrdatapath+'/wordcounts', 'wordcount')
        self.assertIsInstance(g.keys(), GramGenerator)    
        self.assertIsInstance(g.keys()[0], str)                
        
        
#        print g.values().V     
        
#
#    def test_write_corpus(self):
#        """will fail if non-ascii characters aren't stripped."""
#        ret = wr.corpora.to_documents('./testout/mycorpus', self.unigrams)
#        self.assertEqual(ret, None)
#
#    def test_write_corpus_papers(self):
#        ret = wr.corpora.to_documents('./testout/mycorpus', self.unigrams,
#                                                             papers=self.papers)
#        self.assertEqual(ret, None)
#
#    def test_write_dtm(self):
#        ret = wr.corpora.to_dtm_input('./testout/mydtm', self.D, self.unigrams,
#                                      self.voc)
                                      
if __name__ == '__main__':
    
    datapath = './data'
    unittest.main()                                      