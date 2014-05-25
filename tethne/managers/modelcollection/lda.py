import os
import re
import shutil
import tempfile
import subprocess
import numpy as np

from . import ModelCollectionManager

class LDAManager(ModelCollectionManager):
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