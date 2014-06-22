import os
import re
import shutil
import tempfile
import subprocess
import numpy as np

from networkx import Graph

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

from ...classes import GraphCollection
from ..social import TAPModel
from ..managers import ModelManager
from ..corpus.dtmmodel import from_gerrish

class DTMModelManager(ModelManager):
    """
    Model Manager for DTM.
    """
    
    def __init__(self, D, feature='unigrams', outpath='/tmp',
                          temppath=None, dtm_path='./bin/main'):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        outpath : str
            Path to output directory.
        dtm_path : str
            Path to MALLET install directory (contains bin/mallet).
        """
        super(DTMModelManager, self).__init__(outpath, temppath)
        
        self.D = D
        self.dtm_path = dtm_path
        
        self.feature = feature
        self.outname = '{0}/model_run'.format(self.outpath)

        self.mult_path = '{0}/tethne-mult.dat'.format(self.temp)
        self.seq_path = '{0}/tethne-seq.dat'.format(self.temp)        
        self.vocab_path = '{0}/tethne-vocab.dat'.format(self.temp)        
        self.meta_path = '{0}/tethne-meta.dat'.format(self.temp)
    
    def list_topic(self, k, t, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        t : int
            A time index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_list : list
            List of words in topic.
        """
        words = self.model.dimension(k, t=t, top=Nwords)
        as_list = [ self.vocabulary[w] for w,p in words ]

        return as_list
    
    def list_topic_diachronic(self, k, Nwords=10):
        as_dict = { t:self.list_topic(k, t, Nwords)
                        for t in xrange(self.model.T) }
        return as_dict
    
    def print_topic(self, k, t, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        t : int
            A time index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_string : str
            Joined list of words in topic.
        """

        as_string = ', '.join(self.list_topic(k, t=t, Nwords=Nwords))
    
        return as_string
    
    def print_topic_diachronic(self, k, Nwords=10):
        as_dict = self.list_topic_diachronic(k, Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)
        
        return as_string
    
    def list_topics(self, t, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        t : int
            A time index.
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_dict : dict
            Keys are topic indices, values are list of words.
        """
        
        as_dict = {}
        for k in xrange(self.model.Z):
            as_dict[k] = self.list_topic(k, t, Nwords)
    
        return as_dict
    
    def print_topics(self, t, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        t : int
            A time index.
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_string : str
            Newline-delimited lists of words for each topic.
        """
            
        as_dict = self.list_topics(t, Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)
        
        return as_string
    
    def _generate_corpus(self, meta):
        from tethne.writers.corpora import to_dtm_input    
        
        to_dtm_input(self.temp+'/tethne', self.D, self.feature, fields=meta)
    
    def _run_model(self, **kwargs):
        ## Run the dynamic topic model.
        #./main \
        #  --ntopics=20 \
        #  --mode=fit \
        #  --rng_seed=0 \
        #  --initialize_lda=true \
        #  --corpus_prefix=example/test \
        #  --outname=example/model_run \
        #  --top_chain_var=0.005 \
        #  --alpha=0.01 \
        #  --lda_sequence_min_iter=6 \
        #  --lda_sequence_max_iter=20 \
        #  --lda_max_em_iter=10
        
        top_chain_var = kwargs.get('top_chain_var', 0.005)
        lda_seq_min_iter = kwargs.get('lda_seq_min_iter', 6)
        lda_seq_max_iter = kwargs.get('lda_seq_max_iter', 20)
        lda_max_em_iter = kwargs.get('lda_max_em_iter', 10)  
        alpha = kwargs.get('alpha', 0.01) 
        
        max_v = lda_seq_min_iter*lda_max_em_iter*len(self.D.get_slices('date'))
        
        self.conv = []
        i = 1

        corpus_prefix = '{0}/tethne'.format(self.temp)
        
        FNULL = open(os.devnull, 'w')
        
        p = subprocess.Popen( [ self.dtm_path,
                    '--ntopics={0}'.format(self.Z),
                    '--mode=fit',
                    '--rng_seed=0',
                    '--initialize_lda=true',
                    '--corpus_prefix={0}'.format(corpus_prefix),
                    '--outname={0}'.format(self.outname),
                    '--top_chain_var={0}'.format(top_chain_var),
                    '--alpha={0}'.format(alpha),
                    '--lda_sequence_min_iter={0}'.format(lda_seq_min_iter),
                    '--lda_sequence_max_iter={0}'.format(lda_seq_max_iter),
                    '--lda_max_em_iter={0}'.format(lda_max_em_iter) ],
                stderr=subprocess.PIPE,
                stdout=FNULL)
        
        while p.poll() is None:
            l = p.stderr.readline()
            try:    # Find the LL
                this_ll = float(re.findall(r'^lhood\s+=\s+([-]?\d+\.\d+)', l)[0])
                self.ll.append(this_ll)
                
                self.ll_iters.append(i)
                i += 1
            except IndexError:
                pass
            
            try:    # Find conv
                conv = re.findall(r'conv\s+=\s+([-]?\d+\.\d+e[-]\d+)', l)
                self.conv.append(float(conv[0]))

                progress = int(100 * float(len(self.conv))/float(max_v))

            except IndexError:
                pass
            
            
        self.num_iters += lda_max_em_iter   # TODO: does this make sense?
            
    def _load_model(self):
        """Load and return a :class:`.DTMModel`\."""
        
        self.model = from_gerrish(self.outname, self.meta_path, self.vocab_path)
        self.vocabulary = self.model.vocabulary
        return self.model