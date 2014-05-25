"""
Classes for handling bibliographic data.

.. autosummary::

   Paper
   DataCollection
   GraphCollection
   LDAModel
   
"""

# TODO: redefine ModelCollections and Models
# TODO: rename this module?

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from paper import *
from datacollection import *
from graphcollection import *
from modelcollection import *
