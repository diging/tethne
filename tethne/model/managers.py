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

from ..classes import GraphCollection
from social import TAPModel

#from . import Model
#
#class ModelManager(object):
#    self.model = Model

class ModelManager(object):
    """
    Base class for Model Managers.
    """
    
    def __init__(self, feature='unigrams', outpath, temppath=None, **kwargs):
        """
        Initialize the ModelManager.
        
        Parameters
        ----------
        outpath : str
            Path to output directory.
        """
        
        if temppath is None:
            self.temp = tempfile.mkdtemp()    # Temp directory for stuff.
        else:
            self.temp = temppath
        self.outpath = outpath
        self.prepped = False
        
        self.feature = feature

        self.ll = []
        self.ll_iters = []
        self.num_iters = 0

#    def __del__(self):
#        """
#        Delete temporary directory and all files contained therein.
#        """
#        
#        shutil.rmtree(self.temp)        
        
    def plot_ll(self):
        """
        Plots LL/topic over iterations.
        """
        
        import matplotlib.pyplot as plt
        plt.plot(self.ll_iters, self.ll)
        plt.xlabel('Iteration')
        plt.ylabel('LL/Topic')
        plt.savefig('{0}/ll.png'.format(self.outpath))
    
    def prep(self, meta=['date', 'atitle', 'jtitle']):
        """
        Generates a corpus that can be used as input for a modeling algorithm.
        """
        
        self._generate_corpus(self.feature, meta)
        
        self.prepped = True

    def build(self, Z=20, max_iter=1000, prep=False, **kwargs):
        """
        
        """
        
        if not self.prepped:
            if prep:
                self.prep()
            else:
                raise RuntimeError('Not so fast! Call prep() or set prep=True.')

        self.Z = Z
        self._run_model(max_iter=max_iter, **kwargs)  # The action happens here.
        self.plot_ll()

        self._load_model()
        
        return self.model        

class SocialModelManager(object):
    """
    Base class for social model managers.
    """
    
    def __init__(self, **kwargs):
        pass
        
    def build(self, max_iter=1000, **kwargs):
        self._run_model(max_iter, **kwargs)
        self._load_model()
        

class MALLETModelManager(ModelManager):
    """
    Model Manager for LDA topic modeling with MALLET.
    """
    
    def __init__(self, datacollection, feature='unigrams', 
                       outpath='/tmp/',
                       temppath=None,
                       mallet_path='./model/bin/mallet-2.0.7',
                       meta=['date','jtitle']):
        """
        
        Parameters
        ----------
        datacollection : :class:`.DataCollection`
        feature : str
            Key from datacollection.features containing wordcounts (or whatever
            you want to model with).
        mallet_path : str
            Path to MALLET install directory (contains bin/mallet).
        meta : list
            A list of keys onto :class:`.Paper` to include in the exported
            metadata file. Default: ['date', 'jtitle']
        """
        super(MALLETModelManager, self).__init__(outpath, temppath)
        
        self.datacollection = datacollection
        self.mallet_path = mallet_path
        self.feature = feature
        self.meta = meta
        
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
        """
        
        self._generate_corpus(self.feature, meta)
        self._export_corpus()        
        self.prepped = True

    def _generate_corpus(self, feature, meta):
        """
        Writes a corpus to disk amenable to MALLET topic modeling.
        """
        from ..writers.corpora import to_documents
        
        # Metadata to export with corpus.
        metadata = ( self.meta, { p: { k:paper[k] for k in self.meta } 
                       for p,paper in self.datacollection.papers.iteritems() } )
        
        # Export the corpus.
        to_documents(
            self.temp+'/tethne',            # Temporary files.
            self.datacollection.features[feature]['features'],
            metadata=metadata,
            vocab=self.datacollection.features[feature]['index'] )
        
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
        from .corpus.ldamodel import from_mallet
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
        
#        self.M = ModelCollection()
#    
#    def slice(self, axis):
#        M = ModelCollection()
#        a = D.get_slices(axis)
#        for key in sorted(a.keys()):
#            ids = a[key]
#
#            indices = { i:model.lookup[i] for i in ids if i in model.lookup.keys() }
#
#            dt = np.zeros(( len(indices.keys()), self.model.doc_topic.shape[1] ))
#            
#            m = {}
#            k = 0
#            for i in ids:
#                if i in indices.keys():
#                    dt[k,:] = model.doc_topic[indices[i], :]
#                    m[k] = i
#                    k += 1
#                
#            tw = self.model.top_word
#            tk = self.model.top_keys
#            v = self.model.vocabulary
#
#            smodel = LDAModel(dt, tw, tk, m, v)
#            
#            M[key] = smodel
#        return M
        
class DTMModelManager(ModelManager):
    """
    Model Manager for DTM.
    """
    
    def __init__(self, D, outpath, temppath=None, dtm_path='./bin/main'):
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
    
    def _generate_corpus(self, feature, meta):
        from tethne.writers.corpora import to_dtm_input    
        
        to_dtm_input(self.temp+'/tethne', self.D, feature, fields=meta)
    
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
        from .corpus.dtmmodel import from_gerrish
        self.model = from_gerrish(self.outname, self.meta_path, self.vocab_path)
        self.vocabulary = self.model.vocabulary
        return self.model


class TAPModelManager(SocialModelManager):
    """
    For managing the :class:`.TAPModel` .
    """
    
    def __init__(self, D, G, model, **kwargs):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        G : :class:`.GraphCollection`
        model : :class:`.LDAModel`
        """

        super(TAPModelManager, self).__init__(**kwargs)
        self.D = D
        self.G = G
        self.topicmodel = model

        self.SM = {}
        self.SG = GraphCollection()
        
    def author_theta(self, papers, authors=None, indexed_by='doi'):
        """
        Generates distributions over topics for authors, based on distributions
        over topics for their papers.
        
        Parameters
        ----------
        papers : list
            Contains :class:`.Paper` instances.
        authors : dict
            Maps author names (LAST F) onto coauthor :class:`.Graph` indices.
        indexed_by : str
            Key in :class:`.Paper` used to index :class:`.DataCollection`\.
            
        Returns
        -------
        a_theta : dict
            Maps author indices (from coauthor :class:`.Graph`) onto arrays
            describing distribution over topics (normalized to 1).
        """
        
        a_topics = {}
        
        logger.debug('TAPModelManager.author_theta(): start for {0} papers'
                                                           .format(len(papers)))

        for p in papers:
            try:
                item = self.topicmodel.lookup[p[indexed_by]]
                t = self.topicmodel.item(item)
                
                dist = np.zeros(( len(t) ))
                for i,v in t:
                    dist[i] = v

                for author in p.authors():
                    # Only include authors in the coauthors graph.
                    if authors is not None:
                        if author not in authors:
                            continue
                
                    a = authors[author]
                    if a in a_topics:
                        a_topics[a].append(dist)
                    else:
                        a_topics[a] = [ dist ]

            except KeyError:    # May not be corpus model repr for all papers.
                logger.debug('TAPModelManager.author_theta(): KeyError on {0}'
                                                        .format(p[_indexed_by]))
                pass

        shape = ( len(a_topics), self.topicmodel.Z )
        logger.debug('TAPModelManager.author_theta(): initialize with shape {0}'
                                                                 .format(shape))

        a_theta = {}
        for a, dists in a_topics.iteritems():
            a_dist = np.zeros(( self.topicmodel.Z ))
            for dist in dists:
                a_dist += dist
            a_dist = a_dist/len(dists)
            a_theta[a] = a_dist/np.sum(a_dist)   # Should sum to <= 1.0.

        return a_theta
    
    def _run_model(self, max_iter=1000, sequential=True, **kwargs):
        logger.debug('TAPModelManager._run_model(): ' + \
                     'start with max_iter {0} and sequential {1}'
                                                  .format(max_iter, sequential))
        
        axis = kwargs.get('axis', None) # e.g. 'date'

        if axis is None:
            logger.debug('TAPModelManager._run_model(): axis is None')

            # single model.
            pass
        else:
            # model for each slice.
            if axis not in self.D.get_axes():
                raise RuntimeError('No such axis in DataCollection.')
                
            s = 0
            last = None
            for slice in sorted(self.D.get_slices(axis).keys()):
                logger.debug('TAPModelManager._run_model(): ' + \
                             'modeling slice {0}'.format(slice))

                if s > 0 and sequential:
                    alt_r, alt_a, alt_G = self.SM[last].r, self.SM[last].a, self.SM[last].G

                papers = self.D.get_slice(axis, slice, include_papers=True)
                include = {n[1]['label']:n[0] for n in self.G[slice].nodes(data=True) }

                if len(include) < 1:    # Skip slices with no coauthorship.
                    logger.debug('TAPModelManager._run_model(): ' + \
                                 'skipping slice {0}.'.format(slice))
                    continue

                theta = self.author_theta(papers, authors=include) #self.M[slice])
                model = TAPModel(self.G[slice], theta)
                
                if s > 0 and sequential:
                    model.prime(alt_r, alt_a, alt_G)
                
                logger.debug('TAPModelManager._run_model(): ' + \
                             'model.build() for slice {0}'.format(slice))
                model.build(max_iter=max_iter)
                logger.debug('TAPModelManager._run_model(): ' + \
                             'model.build() for slice {0} done'.format(slice))

                self.SM[slice] = model
                last = slice
                s += 1

    def graph_collection(self, k):
        """
        Generate a :class:`.GraphCollection` from the set of :class:`.TapModel`
        instances, for topic ``k``.
        
        Parameters
        ----------
        k : int
            Topic index.
        
        Returns
        -------
        C : :class:`.GraphCollection`
        """
        
        C = GraphCollection()
        for slice in self.SM.keys():
            C[slice] = self.SM[slice].graph(k)
    
        return C
                    
    
    def _load_model(self):
        pass
