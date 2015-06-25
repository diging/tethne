"""
Corpus models describe latent topics (dimensions) that explain the
distribution of features (eg words) among documents in a :class:`.Corpus`\.

Tethne presently represents two corpus models:

.. autosummary::
   :nosignatures:
   
   ldamodel.LDAModel
   dtmmodel.DTMModel
   
Most model classes are subclasses of :class:`.BaseModel`\. It is assumed that
each model describes a set of items (eg :class:`.Paper`\s or authors), a set 
of dimensions that describe those items (eg topics), and a set of features 
that comprise those dimensions (eg words).
"""

#from dtmmodel import *
#from ldamodel import *