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


    def topic_over_time(self, k, threshold=0.05, mode='documents', 
                                 normed=True, plot=False, 
                                 figargs={'figsize':(10,10)} ):
        """
        Representation of topic ``k`` over 'date' slice axis.
        
        Parameters
        ----------
        k : int
            Topic index.
        threshold : float
            Minimum representation of ``k`` in a document.
        mode : str
            'documents' counts the number documents that contain ``k``;
            'proportions' sums the representation of ``k`` in each document
            that contains it.
        normed : bool
            (default: True) Normalizes values by the number of documents in each
            slice.
        plot : bool
            (default: False) If True, generates a MatPlotLib figure and saves
            it to the :class:`MALLETModelManager` outpath.
        figargs : dict
            kwargs dict for :func:`matplotlib.pyplot.figure`\.
            
        Returns
        -------
        keys : array
            Keys into 'date' slice axis.
        R : array
            Representation of topic ``k`` over time.
        """
        
        if k >= self.model.Z:
            raise ValueError('No such topic in this model.')
        
        items = self.model.dimension_items(k, threshold)
        slices = self.D.get_slices('date')
        keys = sorted(slices.keys())

        R = []

        topic_label = self.model.print_topic(k,0)

        if mode == 'documents': # Documents that contain k.
            for t in keys:
                docs = slices[t]
                Ndocs = float(len(docs))
                Ncontains = 0.
                for i,w in items:
                    if i in docs:
                        Ncontains += 1.
                if normed:  # As a percentage of docs in each slice.
                    ylabel = 'Percentage of documents containing topic.'
                    if Ndocs > 0.:
                        R.append( Ncontains/Ndocs )
                    else:
                        R.append( 0. )
                else:       # Raw count.
                    ylabel = 'Number of documents containing topic.'                
                    R.append( Ncontains )

        elif mode == 'proportions': # Representation of topic k.
            for t in keys:
                docs = slices[t]
                Ndocs = float(len(docs))
                if normed:      # Normalized by number of docs in each slice.
                    ylabel = 'Normed representation of topic in documents.'                
                    if Ndocs > 0.:
                        R.append( sum([ w for i,w in items if i in docs ])
                                                                        /Ndocs )
                    else:
                        R.append( 0. )
                else:
                    ylabel = 'Sum of topic representation in documents.'                
                    R.append( sum([ w for i,w in items if i in docs ]) )
        
        if plot:    # Generates a simple lineplot and saves it in the outpath.
            import matplotlib.pyplot as plt
            fig = plt.figure(**figargs)
            plt.plot(np.array(keys), np.array(R))
            plt.xlabel('Time Slice')
            plt.ylabel(ylabel)      # Set based on mode.
            plt.title(topic_label)
            plt.savefig('{0}/topic_{1}_over_time.png'.format(self.outpath, k))        
        
        return np.array(keys), np.array(R)