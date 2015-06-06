"""
Classes and methods related to the :class:`.DTMModelManager`\.
"""

#import os
#import re
#import shutil
#import tempfile
#import subprocess
#import numpy as np
#
#from networkx import Graph
#
#import logging
#logging.basicConfig()
#logger = logging.getLogger(__name__)
#logger.setLevel('ERROR')
#
#from ...classes import GraphCollection
#from ..social import TAPModel
#from ..managers import ModelManager
#from ..corpus.dtmmodel import from_gerrish
#
#class DTMModelManager(ModelManager):
#    """
#    Generates a :class:`.DTMModel` from a :class:`.Corpus` using 
#    `Gerrish's C++ implementation <http://code.google.com/p/princeton-statistical-learning/downloads/detail?name=dtm_release-0.8.tgz>`_.
#
#    You should be sure to slice your :class:`.Corpus` by 'date' using the 
#    'time_period' method (for details, see :meth:`.Corpus.slice`\).
#    
#    .. autosummary::
#       :nosignatures:
#       
#       plot_topic_evolution
#       topic_over_time
#       
#    
#    Parameters
#    ----------
#    D : :class:`.Corpus`
#    outpath : str
#        Path to output directory.
#    dtm_path : str
#        Path to MALLET install directory (contains bin/mallet).
#        
#    Examples
#    --------
#    
#    Starting with some JSTOR DfR data (with wordcounts), a typical workflow
#    might look something like this:
#    
#    .. code-block:: python
#    
#       >>> from nltk.corpus import stopwords                 #  1. Get stoplist.
#       >>> stoplist = stopwords.words()
#       
#       >>> from tethne.readers import dfr                    #  2. Build Corpus.
#       >>> C = dfr.corpus_from_dir('/path/to/DfR/datasets', 'uni', stoplist)
#       
#       >>> def filt(s, C, DC):                           # 3. Filter wordcounts.
#       ...     if C > 3 and DC > 1 and len(s) > 3:
#       ...         return True
#       ...     return False
#       >>> C.filter_features('wordcounts', 'wc_filtered', filt)
#       
#       >>> C.slice('date', 'time_period', window_size=5)     #  4. Slice Corpus.
#       
#       >>> from tethne.model import DTMModelManager          #   5. Get Manager.
#       >>> outpath = '/path/to/my/working/directory'
#       >>> dtm = '/path/to/dtm/bin/main'
#       >>> M = DTMModelManager(C, 'wc_filtered', outpath, dtm_path=dtm)
#       
#       >>> M.prep()                                          #    6. Prep model.
#       
#       >>> model = M.build(Z=50)                             #   7. Build model.
#       >>> model                                             # (may take awhile)
#       <tethne.model.corpus.dtmmodel.DTMModel at 0x10bfac710>
#       
#    A plot showing the log-likelihood/topic over modeling iterations should be
#    generated in your `outpath`. For example:
#    
#    .. figure:: _static/images/dtmmodel_LL.png
#       :width: 400
#       :align: center
#    
#    Behind the scenes, the :func:`.prep` procedure generates data files at
#    ``temppath`` describing your :class:`.Corpus`\:
#    
#    * ``tethne-vocab.dat`` contains all of the words in the corpus, one per
#      line.
#    * ``tethne-mult.dat`` contains wordcounts for each document; words are
#      represented by integer indices corresponding to line numbers in 
#      ``tethne-vocab.dat``. Documents are ordered by publication date (earliest
#      to latest).
#    * ``tethne-seq.dat`` describes how documents are to be apportioned among
#      time-periods. The first line is the number of time periods, and the 
#      subsequent lines specify the number of documents in each successive
#      time-period.
#    * ``tethne-meta.dat`` is a tab-delimted metadata file. Those records occur 
#      in the same order as in the documents in ``tethne-mult.dat``. For
#      example::
#      
#       id	date	atitle
#       10.2307/2437162	1945	SOME ECOTYPIC RELATIONS OF DESCHAMPSIA CAESPITOSA
#       10.2307/4353229	1940	ENVIRONMENTAL INFLUENCE AND TRANSPLANT EXPERIMENTS
#       10.2307/4353158	1937	SOME FUNDAMENTAL PROBLEMS OF TAXONOMY AND PHYLOGENETICS
#
#    The :func:`.build` procedure then starts the DTM modeling algorithm. This 
#    step may take a considerable amount of time, anywhere from a few minutes 
#    (small corpus, few topics) to a few hours (large corpus, many topics).
#    **Warning:** this implementation of DTM is known to run into memory issues
#    with large vocabularies. If a memory-leak does occur, try using a more
#    restrictive filter to the featureset, using 
#    :func:`.Corpus.filter_features`\.
#    
#    Once the :class:`.DTMModel` is built, you can access its methods directly.
#    See full method descriptions in :class:`.DTMModel`\. Of special interest 
#    are:
#    
#    
#    .. currentmodule:: tethne.model.corpus.dtmmodel
#    
#    .. autosummary::
#       :nosignatures:
#    
#       DTMModel.list_topic_diachronic
#       DTMModel.print_topic_diachronic
#       DTMModel.topic_evolution
#    
#    To plot the evolution of a topic over time, use 
#    :func:`.plot_topic_evolution`\. 
#    
#    .. code-block:: python
#    
#       >>> M.plot_topic_evolution(2, plot=True)
#       
#    ...should generate a plot at ``outpath`` called ``topic_2_evolution.png``:
#
#    .. figure:: _static/images/topic_2_evolution.png
#       :width: 400
#       :align: center
#    """
#    
#    def __init__(self, D, feature='unigrams', outpath='/tmp',
#                          temppath=None, dtm_path='./bin/main'):
#        """
#        """
#        super(DTMModelManager, self).__init__(outpath, temppath)
#        
#        self.D = D
#        self.dtm_path = dtm_path
#        
#        self.feature = feature
#        self.outname = '{0}/model_run'.format(self.outpath)
#
#        self.mult_path = '{0}/tethne-mult.dat'.format(self.temp)
#        self.seq_path = '{0}/tethne-seq.dat'.format(self.temp)        
#        self.vocab_path = '{0}/tethne-vocab.dat'.format(self.temp)        
#        self.meta_path = '{0}/tethne-meta.dat'.format(self.temp)
#    
#    def _generate_corpus(self, meta):
#        from tethne.writers.corpora import to_dtm_input    
#        
#        to_dtm_input(self.temp+'/tethne', self.D, self.feature, fields=meta)
#    
#    def _run_model(self, **kwargs):
#        ## Run the dynamic topic model.
#        #./main \
#        #  --ntopics=20 \
#        #  --mode=fit \
#        #  --rng_seed=0 \
#        #  --initialize_lda=true \
#        #  --corpus_prefix=example/test \
#        #  --outname=example/model_run \
#        #  --top_chain_var=0.005 \
#        #  --alpha=0.01 \
#        #  --lda_sequence_min_iter=6 \
#        #  --lda_sequence_max_iter=20 \
#        #  --lda_max_em_iter=10
#        
#        top_chain_var = kwargs.get('top_chain_var', 0.005)
#        lda_seq_min_iter = kwargs.get('lda_seq_min_iter', 6)
#        lda_seq_max_iter = kwargs.get('lda_seq_max_iter', 20)
#        lda_max_em_iter = kwargs.get('lda_max_em_iter', 10)  
#        alpha = kwargs.get('alpha', 0.01) 
#        
#        max_v = lda_seq_min_iter*lda_max_em_iter*len(self.D.get_slices('date'))
#        
#        self.conv = []
#        i = 1
#
#        corpus_prefix = '{0}/tethne'.format(self.temp)
#        
#        FNULL = open(os.devnull, 'w')
#        
#        p = subprocess.Popen( [ self.dtm_path,
#                    '--ntopics={0}'.format(self.Z),
#                    '--mode=fit',
#                    '--rng_seed=0',
#                    '--initialize_lda=true',
#                    '--corpus_prefix={0}'.format(corpus_prefix),
#                    '--outname={0}'.format(self.outname),
#                    '--top_chain_var={0}'.format(top_chain_var),
#                    '--alpha={0}'.format(alpha),
#                    '--lda_sequence_min_iter={0}'.format(lda_seq_min_iter),
#                    '--lda_sequence_max_iter={0}'.format(lda_seq_max_iter),
#                    '--lda_max_em_iter={0}'.format(lda_max_em_iter) ],
#                stderr=subprocess.PIPE,
#                stdout=FNULL)
#        
#        while p.poll() is None:
#            l = p.stderr.readline()
#            try:    # Find the LL
#                this_ll = float(re.findall(r'^lhood\s+=\s+([-]?\d+\.\d+)', l)[0])
#                self.ll.append(this_ll)
#                
#                self.ll_iters.append(i)
#                i += 1
#            except IndexError:
#                pass
#            
#            try:    # Find conv
#                conv = re.findall(r'conv\s+=\s+([-]?\d+\.\d+e[-]\d+)', l)
#                self.conv.append(float(conv[0]))
#
#                progress = int(100 * float(len(self.conv))/float(max_v))
#
#            except IndexError:
#                pass
#    
#        self.num_iters += lda_max_em_iter   # TODO: does this make sense?
#            
#    def _load_model(self):
#        """Load and return a :class:`.DTMModel`\."""
#        
#        self.model = from_gerrish(self.outname, self.meta_path, self.vocab_path)
#        self.vocabulary = self.model.vocabulary
#        return self.model
#
#    def plot_topic_evolution(self, k, Nwords=5, plot=False,
#                                      figargs={'figsize':(10,10)} ):
#        """
#        Plot the probability of the top ``Nwords`` words in topic ``k`` over
#        time.
#        
#        If ``plot`` is True, generates a plot image at ``outpath``.
#        
#        TODO: should return a Figure object.
#           
#        Parameters
#        ----------
#        k : int
#            Topic index.
#        Nwords : int
#            Number of words to include in plot.
#        plot : bool
#            (default: False) If True, generates a plot image at ``outpath``.
#        figargs : dict
#            Keyword arguments to pass to :func:`matplotlib.pyplot.plot`\.
#        
#        Returns
#        -------
#        keys : list
#            Start-date of each time-period.
#        t_series : list
#            Array of p(w|t) for Nwords for each time-period.
#            
#        Examples
#        --------
#
#        .. code-block:: python
#        
#           >>> M.plot_topic_evolution(2, plot=True)
#           
#        ...should generate a plot at ``outpath`` called 
#        ``topic_2_evolution.png``:
#
#        .. figure:: _static/images/topic_2_evolution.png
#           :width: 400
#           :align: center
#        """
#        
#        t_keys, t_series = self.model.topic_evolution(k, Nwords)
#        
#        slices = self.D.get_slices('date')
#        keys = sorted(slices.keys())
#        
#        if plot:
#            import matplotlib.pyplot as plt
#            fig = plt.figure(**figargs)
#            ax = fig.add_axes([0.1, 0.1, 0.6, 0.75])
#            for word, series in t_series.iteritems():
#                plt.plot(keys, series, label=word)
#            plt.xlabel('Time Slice')
#            plt.ylabel('Probability of word in topic')
#            plt.title('Evolution of topic {0}'.format(k))
#            plt.legend(bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
#            plt.xlim(keys[0], keys[-1])
#            plt.savefig('{0}/topic_{1}_evolution.png'.format(self.outpath, k))
#    
#        return keys, t_series
#
#    def topic_over_time(self, k, threshold=0.05, mode='documents', 
#                                 normed=True, plot=False, 
#                                 figargs={'figsize':(10,10)} ):
#        """
#        Representation of topic ``k`` over 'date' slice axis.
#        
#        The :class:`.Corpus` used to initialize the :class:`.DTMModelManager`
#        must have been already sliced by 'date'.
#        
#        Parameters
#        ----------
#        k : int
#            Topic index.
#        threshold : float
#            Minimum representation of ``k`` in a document.
#        mode : str
#            'documents' counts the number documents that contain ``k``;
#            'proportions' sums the representation of ``k`` in each document
#            that contains it.
#        normed : bool
#            (default: True) Normalizes values by the number of documents in each
#            slice.
#        plot : bool
#            (default: False) If True, generates a MatPlotLib figure and saves
#            it to the :class:`MALLETModelManager` outpath.
#        figargs : dict
#            kwargs dict for :func:`matplotlib.pyplot.figure`\.
#            
#        Returns
#        -------
#        keys : array
#            Keys into 'date' slice axis.
#        R : array
#            Representation of topic ``k`` over time.
#            
#        Examples
#        --------
#        
#        .. code-block:: python
#        
#           >>> keys, repr = M.topic_over_time(1, plot=True)
#
#        ...should return ``keys`` (date) and ``repr`` (% documents) for topic 1,
#        and generate a plot like this one in your ``outpath``.
#        
#        .. figure:: _static/images/topic_1_over_time.png
#           :width: 400
#           :align: center
#        """
#        
#        if k >= self.model.Z:
#            raise ValueError('No such topic in this model.')
#        
#        items = self.model.dimension_items(k, threshold)
#        slices = self.D.get_slices('date')
#        keys = sorted(slices.keys())
#
#        R = []
#
#        topic_label = self.model.print_topic(k,0)
#
#        if mode == 'documents': # Documents that contain k.
#            for t in keys:
#                docs = slices[t]
#                Ndocs = float(len(docs))
#                Ncontains = 0.
#                for i,w in items:
#                    if i in docs:
#                        Ncontains += 1.
#                if normed:  # As a percentage of docs in each slice.
#                    ylabel = 'Percentage of documents containing topic.'
#                    if Ndocs > 0.:
#                        R.append( Ncontains/Ndocs )
#                    else:
#                        R.append( 0. )
#                else:       # Raw count.
#                    ylabel = 'Number of documents containing topic.'                
#                    R.append( Ncontains )
#
#        elif mode == 'proportions': # Representation of topic k.
#            for t in keys:
#                docs = slices[t]
#                Ndocs = float(len(docs))
#                if normed:      # Normalized by number of docs in each slice.
#                    ylabel = 'Normed representation of topic in documents.'                
#                    if Ndocs > 0.:
#                        R.append( sum([ w for i,w in items if i in docs ])
#                                                                        /Ndocs )
#                    else:
#                        R.append( 0. )
#                else:
#                    ylabel = 'Sum of topic representation in documents.'                
#                    R.append( sum([ w for i,w in items if i in docs ]) )
#        
#        if plot:    # Generates a simple lineplot and saves it in the outpath.
#            import matplotlib.pyplot as plt
#            fig = plt.figure(**figargs)
#            plt.plot(np.array(keys), np.array(R))
#            plt.xlabel('Time Slice')
#            plt.ylabel(ylabel)      # Set based on mode.
#            plt.title(topic_label)
#            plt.savefig('{0}/topic_{1}_over_time.png'.format(self.outpath, k))        
#        
#        return np.array(keys), np.array(R)