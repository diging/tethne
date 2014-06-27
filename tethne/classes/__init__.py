"""
Classes for handling bibliographic data.

.. autosummary::

   Paper
   Corpus
   GraphCollection
   LDAModel
   
"""

# TODO: redefine ModelCollections and Models
# TODO: rename this module?

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from paper import Paper
from corpus import Corpus
from graphcollection import GraphCollection

from ..persistence import HDF5Paper, HDF5Corpus, HDF5GraphCollection
