import unittest
import tethne.readers as rd
from tethne.data import Paper
import os
import numpy as np

class TestLoad(unittest.TestCase):

    def setUp(self):
        td_path = "./testin/mallet/top_doc"
        wt_path = "./testin/mallet/word_top"
        tk_path = "./testin/mallet/topic_keys"
        m_path = "./testin/mallet/metadata"
        
        Z = 100
        
        self.L = rd.mallet.load(td_path, wt_path, tk_path, Z, m_path)
                
    def test_top_doc(self):
        """
        Each row of L.doc_topic should sum to ~ 1.
        """
        
        D = self.L.doc_topic.shape[0]
        Z = self.L.doc_topic.shape[1]
        
        for d in xrange(D):
            self.assertEqual(1.0, np.around(np.sum(self.L.doc_topic[d,:])))
    
    def test_word_top(self):
        """
        Each row of L.top_word should sum to ~ 1.
        """        
        Z = self.L.top_word.shape[0]
        W = self.L.top_word.shape[1]
        
        for z in xrange(Z):
            self.assertEqual(1.0, np.around(np.sum(self.L.top_word[z,:])))
    
    def test_topic_keys(self):
        """
        There should be a list of words for each topic.
        """
        Z = self.L.doc_topic.shape[1]
        
        self.assertEqual(len(self.L.top_keys), Z)
        
    def tearDown(self):
        pass

class TestRead(unittest.TestCase):

    def setUp(self):
        td_path = "./testin/mallet/top_doc"
        wt_path = "./testin/mallet/word_top"
        tk_path = "./testin/mallet/topic_keys"
        m_path = "./testin/mallet/metadata"
        
        Z = 100

        self.L = rd.mallet.load(td_path, wt_path, tk_path, Z, m_path)        
        self.papers = rd.mallet.read(td_path, wt_path, tk_path, Z, m_path)
    
    def test_num_papers(self):
        """
        Each document in the LDAModel should yield a :class:`.Paper`\.
        """
        
        self.assertEqual(self.L.doc_topic.shape[0], len(self.papers))
    
    def test_papers_content(self):
        """
        Should return :class:`.Paper` objects.
        """
        
        self.assertIsInstance(self.papers[0], Paper)

if __name__ == '__main__':
    unittest.main()
