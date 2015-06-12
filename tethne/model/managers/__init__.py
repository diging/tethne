"""
This module provides manager classes for generating, visualizing, and
analyzing :mod:`.model`\s.

The following managers are presently available:

.. autosummary::
   :nosignatures:

   dtm.DTMModelManager
   mallet.MALLETModelManager
   tap.TAPModelManager

More managers will be added regularly.
"""

import os
import re
import shutil
import shutil
import tempfile
import subprocess

from networkx import Graph


       

#class SocialModelManager(object):
#    """
#    Base class for social model managers.
#    """
#    
#    def __init__(self, **kwargs):
#        pass
#        
#    def build(self, max_iter=1000, **kwargs):
#        self._run_model(max_iter, **kwargs)
#        self._load_model()
#        
#from mallet import *
#from dtm import *
#from tap import *