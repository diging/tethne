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

class ModelManager(object):
    """
    Base class for Model Managers.
    """
    
    def __init__(self, outpath=None, temppath=None, **kwargs):
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
        
        self._generate_corpus(meta)
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
        
from mallet import *
from dtm import *
from tap import *