"""
Classes and methods related to the :class:`.LDAModel`\.
"""

#from ..basemodel import BaseModel
#from ...classes.paper import Paper
#
#import numpy as np
#
#import csv
#from scipy.sparse import coo_matrix
#
class LDAModel(BaseModel):
    """
    Represents a Latent Dirichlet Allocation (LDA) topic model.
    
    In the LDA model, topics (dimensions) are probability distributions over 
    words (features), and documents (items) are comprised of mixtures of topics.
    For a complete description of the model, see 
    `Blei & Jordan (2003) <http://jmlr.org/papers/v3/blei03a.html>`_.
    
    To generate a :class:`.LDAModel` from a :class:`.Corpus` using
    `MALLET <http://mallet.cs.umass.edu/>`_, use the 
    :class:`.MALLETModelManager`\. Additional managers for :class:`.LDAModel`\s
    will be added shortly.
    
    You can also initialize a :class:`.LDAModel` directly by providing the
    following parameters:
    
    * ``theta``, describes the proportion of topics (cols) in each document 
      (rows).
    * ``phi`` describes the topic (rows) distributions over words (cols).
    * ``metadata`` should map matrix indices for documents onto :class:`.Paper`
      IDs (or whatever you use to identify documents).
    * ``vocabulary`` should map matrix indices for words onto word-strings.
    ``metadata`` and ``vocabulary`` mappings.
    
    Finally, you can use :func:`.from_mallet` to generate a :class:`.LDAModel`
    from MALLET output.
    
    .. autosummary::
       :nosignatures:
       
       list_topic
       list_topics
       print_topic
       print_topics
    
    Parameters
    ----------
    theta : matrix-like
        Distribution of topics (cols) in documents (rows). Rows sum to 1.
    phi : matrix-like
        Distribution over words (cols) for topics (rows). Rows sum to 1.
    metadata : dict
        Maps matrix indices onto document datadata.
    vocabulary : dict
        Maps W indices onto words.
    """

    def __init__(self, theta, phi, metadata, vocabulary):
        """
        Initialize the :class:`.LDAModel`\.
        """
        
        self.theta = theta
        self.M = theta.shape[0] # Number of documents.

        self.phi = phi
        self.Z = phi.shape[0]   # Number of topics.
        self.W = phi.shape[1]   # Number of terms.

        self.metadata = metadata
        self.vocabulary = vocabulary
        
        self.lookup = { v['id']:k for k,v in metadata.iteritems() }
    
#
