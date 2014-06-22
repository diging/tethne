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
from ...writers.corpora import to_documents
from ..corpus.ldamodel import from_mallet

class MALLETModelManager(ModelManager):
    """
    Model Manager for LDA topic modeling with MALLET.
    """
    
    def __init__(self, datacollection,
                       feature='unigrams', outpath='/tmp/',
                       temppath=None, mallet_path='./model/bin/mallet-2.0.7'):
        """
        
        Parameters
        ----------
        datacollection : :class:`.DataCollection`
        feature : str
            Key from datacollection.features containing wordcounts (or whatever
            you want to model with).
        mallet_path : str
            Path to MALLET install directory (contains bin/mallet).
        """
        super(MALLETModelManager, self).__init__(outpath, temppath)
        
        self.datacollection = datacollection
        self.mallet_path = mallet_path
        self.feature = feature
        
        self.input_path = '{0}/input.mallet'.format(self.temp)
        self.corpus_path = self.temp+'/tethne_docs.txt'
        self.meta_path = self.temp+'/tethne_meta.csv'
    
        self.dt = '{0}/dt.dat'.format(self.temp)
        self.wt = '{0}/wt.dat'.format(self.temp)
        self.om = '{0}/model.mallet'.format(self.outpath)
    
        self.vocabulary = self.datacollection.features[self.feature]['index']

    def prep(self, meta=['date', 'atitle', 'jtitle']):
        """
        Generates a corpus that can be used as input for modeling.

        Parameters
        ----------
        meta : list
            A list of keys onto :class:`.Paper` to include in the exported
            metadata file. Default: ['date', 'jtitle']
        """
        
        self._generate_corpus(meta)
        self.prepped = True

    def _generate_corpus(self, meta):
        """
        Writes a corpus to disk amenable to MALLET topic modeling.
        """
        
        # Metadata to export with corpus.
        metadata = ( meta, { p: { k:paper[k] for k in meta }
                       for p,paper in self.datacollection.papers.iteritems() } )
        
        # Export the corpus.
        to_documents(
            self.temp+'/tethne',            # Temporary files.
            self.datacollection.features[self.feature]['features'],
            metadata=metadata,
            vocab=self.datacollection.features[self.feature]['index'] )
        
        self._export_corpus()
    
    def _export_corpus(self):
        """
        Calls MALLET's `import-file` method.
        """
        # bin/mallet import-file --input /Users/erickpeirson/mycorpus_docs.txt
        #     --output mytopic-input.mallet --keep-sequence --remove-stopwords
        
        self.mallet = self.mallet_path + "/bin/mallet"
        try:
            exit = subprocess.call( [ self.mallet, 
                    'import-file',
                    '--input {0}'.format(self.corpus_path),
                    '--output {0}'.format(self.input_path),
                    '--keep-sequence',          # Required (oddly) for LDA.
                    '--remove-stopwords' ])     # Probably redundant.

        except OSError:     # Raised if mallet_path is bad.
            raise OSError("MALLET path invalid or non-existent.")

        if exit != 0:
            raise RuntimeError("MALLET import-file failed: {0}.".format(exit))

    def _run_model(self, max_iter=20, **kwargs):
        """
        Calls MALLET's `train-topic` method.
        """
        #$ bin/mallet train-topics --input mytopic-input.mallet --num-topics 100 
        #> --output-doc-topics /Users/erickpeirson/doc_top 
        #> --word-topic-counts-file /Users/erickpeirson/word_top 
        #> --output-topic-keys /Users/erickpeirson/topic_keys
        
        prog = re.compile('\<([^\)]+)\>')
        ll_prog = re.compile(r'(\d+)')
        try:
            p = subprocess.Popen( [ self.mallet,
                        'train-topics',
                        '--input {0}'.format(self.input_path),
                        '--num-topics {0}'.format(self.Z),
                        '--num-iterations {0}'.format(max_iter),
                        '--output-doc-topics {0}'.format(self.dt),
                        '--word-topic-counts-file {0}'.format(self.wt),
                        '--output-model {0}'.format(self.om) ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE)
        
            # Handle output of MALLET in real time.
            while p.poll() is None:
                l = p.stderr.readline()
                
                # Keep track of LL/topic.
                try:
                    this_ll = float(re.findall('([-+]\d+\.\d+)', l)[0])
                    self.ll.append(this_ll)
                except IndexError:  # Not every line will match.
                    pass
                
                # Keep track of modeling progress.
                try:
                    this_iter = float(prog.match(l).group(1))
                    self.ll_iters.append(this_iter)
                    progress = int(100 * this_iter/max_iter)
                    logger.debug('Modeling progress: {0}%.\r'.format( progress ),)
                except AttributeError:  # Not every line will match.
                    pass
            logger.debug('Modeling complete.')
            
        except OSError:     # Raised if mallet_path is bad.
            raise OSError("MALLET path invalid or non-existent.")
            
        self.num_iters += max_iter
            
    def _load_model(self):
        self.model = from_mallet(   self.dt, 
                                    self.wt, 
                                    self.meta_path  )
    
    def list_topic(self, k, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_list : list
            List of words in topic.
        """
        words = self.model.dimension(k, top=Nwords)
        as_list = [ self.vocabulary[w] for w,p in words ]

        return as_list
    
    def print_topic(self, k, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_string : str
            Joined list of words in topic.
        """

        as_string = ', '.join(self.list_topic(k, Nwords))
    
        return as_string
    
    def list_topics(self, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_dict : dict
            Keys are topic indices, values are list of words.
        """
        
        as_dict = {}
        for k in xrange(self.model.Z):
            as_dict[k] = self.list_topic(k, Nwords)
    
        return as_dict
    
    def print_topics(self, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_string : str
            Newline-delimited lists of words for each topic.
        """
            
        as_dict = self.list_topics(Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)
        
        return as_string

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
        slices = self.datacollection.get_slices('date')
        keys = sorted(slices.keys())

        R = []

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
            plt.savefig('{0}/topic_{1}_over_time.png'.format(self.outpath, k))        
        
        return np.array(keys), np.array(R)