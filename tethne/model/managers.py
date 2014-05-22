import os
import re
import shutil
import tempfile
import subprocess
import numpy as np

import sys
sys.path.append('/Users/erickpeirson/tethne')
from tethne.model import TAPModel, LDAModel
from tethne.data import ModelCollection, GraphCollection


class ModelManager(object):
    """
    Base class for Model Managers.
    """
    
    def __init__(self, D, outpath):
        """
        Initialize the ModelManager.
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        outpath : str
            Path to output directory.
        """
        
        self.D = D
        self.temp = tempfile.mkdtemp()    # Temp directory for stuff.
        self.outpath = outpath
        self.prepped = False
        self.ll = []
        self.ll_iters = []
        self.num_iters = 0

    def __del__(self):
        """
        Delete temporary directory and all files contained therein.
        """
        
        shutil.rmtree(self.temp)        
        
    def plot_ll(self):
        """
        Plots LL/topic over iterations.
        """
        
        import matplotlib.pyplot as plt
        plt.plot(self.ll_iters, self.ll)
        plt.xlabel('Iteration')
        plt.ylabel('LL/Topic')
        plt.savefig('{0}/ll.png'.format(self.outpath))
    
    def prep(self, gram='uni', meta=['date', 'atitle', 'jtitle']):
        """
        Generates a corpus that can be used as input for a modeling algorithm.
        """
        
        self._generate_corpus(gram, meta)
        
        self.prepped = True

    def build(self, Z=20, max_iter=1000, prep=False):
        """
        
        """
        
        if not self.prepped:
            if prep:
                self.prep()
            else:
                raise RuntimeError('Not so fast! Call prep() or set prep=True.')

        self.Z = Z
        self._run_model(max_iter)  # The action happens here.
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
        

class LDAModelManager(ModelManager):
    """
    Model Manager for LDA topic modeling with MALLET.
    """
    
    def __init__(self, D, outpath, mallet_path):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        outpath : str
            Path to output directory.
        mallet_path : str
            Path to MALLET install directory (contains bin/mallet).
        """
        super(LDAModelManager, self).__init__(D, outpath)
        
        self.mallet_path = mallet_path
        
    def __del__(self):
        """
        Delete temporary directory and all files contained therein.
        """
        
        shutil.rmtree(self.temp)
    
    def _generate_corpus(self, gram, meta):
        from tethne.writers.corpora import to_documents    
        
        if not to_documents(self.temp+'/tethne',    # Temporary files.
                            self.D.grams[gram],     # e.g. uni, bi, tri.
                            papers=self.D.papers(),
                            fields=meta):
            return False

        self.corpus_path = '{0}/tethne_docs.txt'.format(self.temp)
        self.meta_path = '{0}/tethne_meta.csv'.format(self.temp)
        
        self._export_corpus()
        
    
    def _export_corpus(self):
        # bin/mallet import-file --input /Users/erickpeirson/mycorpus_docs.txt
        #     --output mytopic-input.mallet --keep-sequence --remove-stopwords
        
        self.mallet = self.mallet_path + "/bin/mallet"
        self.input_path = '{0}/input.mallet'.format(self.temp)
        
        try:
            exit = subprocess.call( [ self.mallet, 
                    'import-file',
                    '--input {0}'.format(self.corpus_path),
                    '--output {0}'.format(self.input_path),
                    '--keep-sequence',  # Required (oddly) for LDA.
                    '--remove-stopwords' ]) # Probably redundant.

        except OSError:     # Raised if mallet_path is bad.
            raise OSError("MALLET path invalid or non-existent.")

        if exit != 0:
            raise RuntimeError("MALLET import-file failed: {0}.".format(exit))

    def _run_model(self, max_iter):
        #$ bin/mallet train-topics --input mytopic-input.mallet --num-topics 100 
        #> --output-doc-topics /Users/erickpeirson/doc_top 
        #> --word-topic-counts-file /Users/erickpeirson/word_top 
        #> --output-topic-keys /Users/erickpeirson/topic_keys
            
        self.dt = '{0}/dt.dat'.format(self.temp)
        self.wt = '{0}/wt.dat'.format(self.temp)
        self.tk = '{0}/tk.dat'.format(self.temp)        
         
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
                        '--output-topic-keys {0}'.format(self.tk) ], 
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
                    print 'Modeling progress: {0}%.\r'.format( progress ),
                except AttributeError:  # Not every line will match.
                    pass
            print 'Modeling complete.'
            
        except OSError:     # Raised if mallet_path is bad.
            raise OSError("MALLET path invalid or non-existent.")
            
        self.num_iters += max_iter
            
    def _load_model(self):
        """Load and return a :class:`.LDAModel`\."""
        from tethne.readers import mallet
        self.model = mallet.load(   self.dt, 
                                    self.wt, 
                                    self.tk, 
                                    self.Z,
                                    self.meta_path  )     
    def slice(self, axis):
        M = ModelCollection()
        a = D.get_slices(axis)
        for key in sorted(a.keys()):
            ids = a[key]

            indices = { i:model.lookup[i] for i in ids if i in model.lookup.keys() }

            dt = np.zeros(( len(indices.keys()), self.model.doc_topic.shape[1] ))
            
            m = {}
            k = 0
            for i in ids:
                if i in indices.keys():
                    dt[k,:] = model.doc_topic[indices[i], :]
                    m[k] = i
                    k += 1
                
            tw = self.model.top_word
            tk = self.model.top_keys
            v = self.model.vocabulary

            smodel = LDAModel(dt, tw, tk, m, v)
            
            M[key] = smodel
        return M
        
class DTMModelManager(ModelManager):
    """
    Model Manager for DTM.
    """
    
    def __init__(self, D, outpath, dtm_path='./bin/main'):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        outpath : str
            Path to output directory.
        dtm_path : str
            Path to MALLET install directory (contains bin/mallet).
        """
        super(DTMModelManager, self).__init__(D, outpath)
        
        self.dtm_path = dtm_path
    
    def _generate_corpus(self, gram, meta):
        from tethne.writers.corpora import to_dtm_input    
        
        to_dtm_input(self.temp+'/tethne',
                            self.D,
                            self.D.grams[gram][0],     # e.g. uni, bi, tri.
                            self.D.grams[gram][1],
                            fields=meta)
                     

        self.mult_path = '{0}/tethne-mult.dat'.format(self.temp)
        self.seq_path = '{0}/tethne-seq.dat'.format(self.temp)        
        self.vocab_path = '{0}/tethne-vocab.dat'.format(self.temp)        
        self.meta_path = '{0}/tethne-meta.dat'.format(self.temp)
        

    def _run_model(self, max_iter, **kwargs):
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
        
        self.conv = []
        i = 1

        corpus_prefix = '{0}/tethne'.format(self.temp)
        outname = '{0}/model_run'.format(self.outpath)
        
        FNULL = open(os.devnull, 'w')
        
        p = subprocess.Popen( [ self.dtm_path,
                    '--ntopics={0}'.format(self.Z),
                    '--mode=fit',
                    '--rng_seed=0',
                    '--initialize_lda=true',
                    '--corpus_prefix={0}'.format(corpus_prefix),
                    '--outname={0}'.format(outname),
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
                print conv
            except IndexError:
                pass
            
            
        self.num_iters += max_iter
            
    def _load_model(self):
        """Load and return a :class:`.LDAModel`\."""
        
        pass  


class TAPModelManager(SocialModelManager):
    """
    For managing the :class:`.TAPModel` .
    """
    
    def __init__(self, D, G, M, **kwargs):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        G : :class:`.GraphCollection`
        M : :class:`.ModelCollection`
        """

        super(TAPModelManager, self).__init__(**kwargs)
        self.D = D
        self.M = M
        self.G = G
        self.SM = ModelCollection()
        self.SG = GraphCollection()
        
    def author_theta(self, papers, model, indexed_by='doi'):
        """
        Generates distributions over topics for authors, based on distributions
        over topics for their papers.
        """
        
        a_topics = {}

        for p in papers:
            try:
                t = model.topics_in_doc(p[indexed_by])
                dist = np.zeros(( len(t) ))
                for i,v in t:
                    dist[i] = v

                for author in p.authors():
                    if author in a_topics:
                        a_topics[author].append(dist)
                    else:
                        a_topics[author] = [ dist ]
            except KeyError:    # May not be corpus model repr for all papers.
                pass

        a_theta = np.zeros(( len(a_topics), model.num_topics() ))
        a = 0
        for author, dists in a_topics.iteritems():
            a_dist = np.zeros(( model.num_topics() ))
            for dist in dists:
                a_dist += dist
            a_dist = a_dist/len(dists)
            a_theta[a, :] = a_dist/np.sum(a_dist)   # Should sum to <= 1.0.

        
        return a_theta
    
    def _run_model(self, max_iter=1000, sequential=True, **kwargs):
        print 'run model'

        axis = kwargs.get('axis', None) # e.g. 'date'

        if axis is None:
            # single model.
            pass
        else:
            # model for each slice.
            if axis not in D.get_axes():
                raise RuntimeError('No such axis in DataCollection.')
                
            s = 0
            for slice in sorted(D.get_slices(axis).keys()):
                print 'modeling slice {0}'.format(slice) # TODO: logging.

                if s > 0 and sequential:
                    alt_r, alt_a, alt_G = model.r, model.a, model.G

                papers = D.get_slice(axis, slice, papers=True)

                theta = self.author_theta(papers, self.M[slice])
                model = TAPModel(self.G[slice], theta)
                
                if s > 0 and sequential:
                    model.prime(alt_r, alt_a, alt_G)
                
                model.build()
                self.SM[slice] = model
                
                s += 1
                
    
    def graph_collection(self, k):
        C = GraphCollection()
        for slice in self.SM.keys():
            C[slice] = self.SM[slice].graph(k)
    
        return C
                    
    
    def _load_model(self):
        pass

        
if __name__ == '__main__':
    import sys
    sys.path.append("/Users/erickpeirson/tethne")
    from tethne.builders import DFRBuilder, authorCollectionBuilder
    from tethne.data import DataCollection

    datapath = "/Users/erickpeirson/Genecology Project Archive/JStor DfR Datasets/2013.5.3.k2HUvXh9"
    
    dc_builder = DFRBuilder(datapath)
    D = dc_builder.build(slice_by=['date',], cumulative=True, method='time_period', window_size=10)
    
    import matplotlib.pyplot as plt
    fig = plt.figure(figsize=(40,15), dpi=600)
    D.plot_distribution('date', fig=fig)#,'jtitle')
    plt.savefig('/Users/erickpeirson/Desktop/test.png')


    builder = authorCollectionBuilder(D)
    GC = builder.build('date', 'coauthors', threshold=2)
    

    MM = LDAModelManager(D, '/Users/erickpeirson/Desktop/', '/Applications/mallet-2.0.7')
    MM.prep()
    model = MM.build(max_iter=100)
    M = MM.slice('date')

    SM = TAPModelManager(D, GC, M)
    SM.build(axis='date')
    
    
##    print D.grams['uni'].keys()
#    
#    MM = DTMModelManager(D, '/Users/erickpeirson/Desktop/')
#    MM.prep()
#    model = MM.build(max_iter=500)
##    model.print_topics()
##    
##    del MM

#    for slice in sorted(D.get_slices('date').keys()):
#        print 'modeled slice {0}'.format(slice)
#        papers = D.get_slice('date', slice, papers=True)
#
#        g_tok, vocab, counts = D.grams['uni']
#        g_tok_ = { k:g for k,g in g_tok.iteritems() if k in [ p['doi'] for p in papers ] }
#        grams = (g_tok_, vocab, counts)
#        
#        D_ = DataCollection(papers, grams={'uni':grams})

