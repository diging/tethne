import unittest

import sys
sys.path.append('../../')

from nltk.corpus import stopwords
import numpy
import os

from tethne import DataCollection, HDF5DataCollection
from tethne.readers import dfr
from tethne.model.managers import DTMModelManager

import logging
logging.basicConfig()
#logger = logging.getLogger('tethne.classes.graphcollection')
#logger.setLevel('ERROR')
#logger = logging.getLogger('tethne.classes.datacollection')
#logger.setLevel('ERROR')


class TestMALLETModelManager(unittest.TestCase):
    def setUp(self):
        dfrdatapath = '{0}/dfr'.format(datapath)
        
        papers = dfr.read(dfrdatapath)
        ngrams = dfr.ngrams(dfrdatapath, 'uni')
        self.D = DataCollection(papers, features={'unigrams': ngrams},
                                        index_by='doi',
                                        exclude=set(stopwords.words()))
        self.D.slice('date', 'time_period', window_size=10)
        self.M = DTMModelManager(self.D, outpath=outpath,
                                temppath=temppath,
                                dtm_path=dtm_path)
        
#    def test_prep(self):
#        """
#        .prep() should result in four sizeable temporary corpus files.
#        """
#        self.M.prep()
#        self.assertIn('tethne-meta.dat', os.listdir(temppath))
#        self.assertGreater(os.path.getsize(temppath+'/tethne-meta.dat'), 15000)
#        
#        self.assertIn('tethne-mult.dat', os.listdir(temppath))
#        self.assertGreater(os.path.getsize(temppath+'/tethne-mult.dat'), 1400000)
#                
#        self.assertIn('tethne-seq.dat', os.listdir(temppath))        
#        self.assertGreater(os.path.getsize(temppath+'/tethne-seq.dat'), 10)
#
#        self.assertIn('tethne-vocab.dat', os.listdir(temppath))        
#        self.assertGreater(os.path.getsize(temppath+'/tethne-vocab.dat'), 400000)        
    
#    def test_build(self):
#        """
#        .build() should result in new sizeable files in both the temp and out
#        directories.
#        """
#        self.M.prep()
#        self.M.build(Z=5, lda_seq_min_iter=2, lda_seq_max_iter=4, lda_max_em_iter=4)
        

    def test_load(self):
        self.M.prep()
        self.M._load_model()
        
        print self.M.model.dimension_items(0, threshold=0.01)


if __name__ == '__main__':
    datapath = './data'
    temppath = './sandbox/temp'
    outpath = './sandbox/out'
    dtm_path = '/Users/erickpeirson/tethne/tethne/model/bin/main'
    unittest.main()