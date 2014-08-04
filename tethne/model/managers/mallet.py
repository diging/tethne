"""
Classes and methods related to the :class:`.MALLETModelManager`\.
"""

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
#from ..social import TAPModel
from ..managers import ModelManager
from ...writers.corpora import to_documents
from ..corpus.ldamodel import from_mallet, LDAModel

class MALLETModelManager(ModelManager):
    """
    Generates a :class:`.LDAModel` from a :class:`.Corpus` using
    `MALLET <http://mallet.cs.umass.edu/>`_.
    
    The :class:`.Corpus` should already contain at least one featurset,
    indicated by the `feature` parameter, such as wordcounts. You may
    specify two working directories: `temppath` should be a working
    directory that will contain intermediate files (e.g. documents, data
    files, metadata), while `outpath` will contain the final model and any 
    plots generated during the modeling process. If `temppath` is not
    provided, generates and uses a system temporary directory.
    
    Tethne comes bundled with a recent version of MALLET. If you would
    rather use your own install, you can do so by providing the 
    `mallet_path` parameter. This should point to the directory containing
    ``/bin/mallet``.
    
    .. autosummary::
       :nosignatures:
       
       topic_over_time
    
    Parameters
    ----------
    D : :class:`.Corpus`
    feature : str
        Key from D.features containing wordcounts (or whatever
        you want to model with).
    outpath : str
        Path to output directory.
    temppath : str
        Path to temporary directory.
    mallet_path : str
        Path to MALLET install directory (contains bin/mallet).
        
    Examples
    --------
        
    Starting with some JSTOR DfR data (with wordcounts), a typical workflow
    might look something like this:
    
    .. code-block:: python
    
       >>> from nltk.corpus import stopwords                 #  1. Get stoplist.
       >>> stoplist = stopwords.words()
       
       >>> from tethne.readers import dfr                    #  2. Build Corpus.
       >>> C = dfr.corpus_from_dir('/path/to/DfR/datasets', 'uni', stoplist)
       
       >>> def filt(s, C, DC):                           # 3. Filter wordcounts.
       ...     if C > 3 and DC > 1 and len(s) > 3:
       ...         return True
       ...     return False
       >>> C.filter_features('wordcounts', 'wc_filtered', filt)
       
       >>> from tethne.model import MALLETModelManager       #   4. Get Manager.
       >>> outpath = '/path/to/my/working/directory'
       >>> mallet = '/Applications/mallet-2.0.7'
       >>> M = MALLETModelManager(C, 'wc_filtered', outpath, mallet_path=mallet)
       
       >>> M.prep()                                          #    5. Prep model.
       
       >>> model = M.build(Z=50, max_iter=300)               #   6. Build model.
       >>> model                                             # (may take awhile)
       <tethne.model.corpus.ldamodel.LDAModel at 0x10bfac710>

    A plot showing the log-likelihood/topic over modeling iterations should be
    generated in your `outpath`. For example:
    
    .. figure:: _static/images/ldamodel_LL.png
       :width: 400
       :align: center
       
    Behind the scenes, the :func:`.prep` procedure generates a plain-text corpus
    file at `temppath`, along with a metadata file. MALLET's ``import-file``
    procedure is then called, which translates the corpus into MALLET's internal
    format (also stored at the `temppath`).
    
    The :func:`.build` procedure then invokes MALLET's ``train-topics``
    procedure. This step may take a considerable amount of time, anywhere from 
    a few minutes (small corpus, few topics) to a few hours (large corpus, many
    topics).

    For a :class:`.Corpus` with a few thousand :class:`.Paper`\s, 300 - 500 
    iterations is often sufficient to achieve convergence for 20-100 topics.
    
    Once the :class:`.LDAModel` is built, you can access its methods directly.
    See full method descriptions in :class:`.LDAModel`\.
    
    For more information about topic modeling with MALLET see 
    `this tutorial <http://programminghistorian.org/lessons/topic-modeling-and-mallet>`_.
    
    """
    
    def __init__(self, D, feature='unigrams', outpath='/tmp/', temppath=None,
                          mallet_path='./model/bin/mallet-2.0.7'):
        super(MALLETModelManager, self).__init__(outpath, temppath)
        
        self.D = D
        self.mallet_path = mallet_path
        self.feature = feature
        
        self.input_path = '{0}/input.mallet'.format(self.temp)
        self.corpus_path = self.temp+'/tethne_docs.txt'
        self.meta_path = self.temp+'/tethne_meta.csv'
    
        self.dt = '{0}/dt.dat'.format(self.temp)
        self.wt = '{0}/wt.dat'.format(self.temp)
        self.om = '{0}/model.mallet'.format(self.outpath)
    
        self.vocabulary = self.D.features[self.feature]['index']

    def _generate_corpus(self, meta):
        """
        Writes a corpus to disk amenable to MALLET topic modeling.
        """
        
        # Metadata to export with corpus.
        metadata = ( meta, { p: { k:paper[k] for k in meta }
                       for p,paper in self.D.papers.iteritems() } )
        
        # Export the corpus.
        to_documents(
            self.temp+'/tethne',            # Temporary files.
            self.D.features[self.feature]['features'],
            metadata=metadata,
            vocab=self.D.features[self.feature]['index'] )
        
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

    def topic_over_time(self, k, threshold=0.05, mode='documents', 
                                 normed=True, plot=False, 
                                 figargs={'figsize':(10,10)} ):
        """
        Representation of topic ``k`` over 'date' slice axis.
        
        The :class:`.Corpus` used to initialize the :class:`.LDAModelManager`
        must have been already sliced by 'date'.
        
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
            
        Examples
        --------
        
        .. code-block:: python
        
           >>> keys, repr = M.topic_over_time(1, plot=True)

        ...should return ``keys`` (date) and ``repr`` (% documents) for topic 1,
        and generate a plot like this one in your ``outpath``.
        
        .. figure:: _static/images/topic_1_over_time.png
           :width: 400
           :align: center
           
        """
        
        if k >= self.model.Z:
            raise ValueError('No such topic in this model.')
        
        items = self.model.dimension_items(k, threshold)
        slices = self.D.get_slices('date')
        keys = sorted(slices.keys())

        R = []

        topic_label = self.model.print_topic(k)

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