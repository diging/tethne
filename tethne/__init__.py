"""
Tethne is a Python package that draws together tools and techniques from 
bibliometrics, computational linguistics, and social influence modeling into a
single easy-to-use corpus analysis framework. Scholars can use Tethne to parse 
and organize data from the ISI Web of Science and JSTOR Data-for-Research 
databases, and generate time-variant citation-based network models, topic 
models, and social influence models. Tethne also provides mechanisms for 
visualizing those models using mainstream network visualization software (e.g. 
Cyotoscape and Gephi) and the MatPlotLib Python library.

.. autosummary::

   analyze
   classes
   model
   networks
   persistence
   readers
   writers
   
"""

from analyze import *
from classes import *
from model import *
from networks import *
from persistence import *
from readers import *
from services import *
from writers import *

from persistence import hdf5
from persistence.hdf5 import *

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')