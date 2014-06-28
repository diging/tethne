"""
Corpus models describe latent topics (dimensions) that explain the
distribution of features (eg words) among documents in a :class:`.Corpus`\.

Tethne presently represents two corpus models:

.. autosummary::
   :nosignatures:
   
   ldamodel.LDAModel
   dtmmodel.DTMModel

"""

from dtmmodel import *
from ldamodel import *