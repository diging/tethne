import os
import re
import shutil
import tempfile
import numpy as np

class ModelCollectionManager(object):
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