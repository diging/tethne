import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from util import *
from ...model import DTMModel

import numpy

class HDF5DTMModel(DTMModel):
    """
    Provides HDF5 persistence for :class:`.DTMModel`\.
    
    If ``datapath`` is provided, and points to a real HDF5 file, then no other
    parameters need be provided.
    
    Parameters
    ----------
    e_theta : matrix-like
        Distribution of topics (Z) in documents (M). Shape: (Z, M).
    phi : matrix-like
        Topic (Z) distribution over words (W), over time (T). Shape: 
        (Z, W, T)
    metadata : dict
        Maps matrix indices onto document datadata.
    vocabulary : dict
        Maps W indices onto words.
    datapath : str
        (optional) Path to an HDF5 repository. If not provided, generates
        a temporary path, which can be accessed as the ``.path`` attribute.
    """

    def __init__(   self, e_theta=None, phi=None, metadata=None,
                    vocabulary=None, datapath=None  ):
        """
        Initialize the :class:`.HDF5DTMModel`\.
        
        """

        logger.debug('HDF5DTMModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('DTMModel', datapath)
        logger.debug('HDF5DTMModel: got h5file at path {0}'.format(self.path))

        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5DTMModel: initialized array group.')
        
        self.e_theta = get_or_create_array( self.h5file, self.agroup,
                                            'e_theta', e_theta)
        self.Z = self.e_theta.shape[0]   # Number of topics.
        self.M = self.e_theta.shape[1]   # Number of documents.
        logger.debug('HDF5DTMModel: initialized theta with shape {0}'
                                                    .format(self.e_theta.shape))

        self.phi = get_or_create_array(self.h5file, self.agroup, 'phi', phi)
        self.W = self.phi.shape[1]    # Number of words.
        self.T = self.phi.shape[2]    # Number of time periods.
        logger.debug('HDF5DTMModel: initialized phi with shape {0}'
                                                        .format(self.phi.shape))

        self.metadata = HDF5Metadata(self.h5file, metadata)
        logger.debug('HDF5DTMModel: initialized metadata with {0} records'
                                                    .format(len(self.metadata)))
        
        self.vgroup = get_or_create_group(self.h5file, 'vocabulary')
        logger.debug('HDF5DTMModel: initialized vocabulary group')
        
        if 'vocabulary' not in self.vgroup:
            vocab_sorted = [ vocabulary[k] for k in sorted(vocabulary.keys()) ]
        else:
            vocab_sorted = []
        self.vocabulary = HDF5ArrayDict(    self.h5file, self.vgroup,
                                            'vocabulary', vocab_sorted  )
        self.h5file.flush()
        
        logger.debug('HDF5DTMModel: initialized vocabulary with {0} entries'
                                                  .format(len(self.vocabulary)))

        # Doesn't get stored.
        self.lookup = { v['id']:k for k,v in self.metadata.iteritems() }

        logger.debug('HDF5DTMModel: initialization complete')

def to_hdf5(model, datapath=None):
    """
    Generate a :class:`.HDF5DTMModel` from the current instance.
    
    Parameters
    ----------
    model : :class:`.DTMModel`
    datapath : str
        (optional) Path to an HDF5 repository. If not provided, generates
        a temporary path, which can be accessed as the ``.path`` attribute.
    
    Returns
    -------
    hdf5_model : :class:`.HDF5DTMModel`
    """

    metadata = { k:v for k,v in model.metadata.iteritems() }
    vocabulary = { k:v for k,v in model.vocabulary.iteritems() }
    hdf5_model = HDF5DTMModel(  e_theta = numpy.array(model.e_theta),
                                phi = numpy.array(model.phi),
                                metadata = metadata,
                                vocabulary = vocabulary,
                                datapath = datapath )

    return hdf5_model

def from_hdf5(HD_or_path):
    """
    Load a :class:`.DTMModel` from a :class:`.HDF5DTMModel`\.
    
    Parameters
    ----------
    HD_or_path : str or :class:`.HDF5DTMModel`
        If str, must be a path to a :class:`.HDF5DTMModel` HDF5 repo.
        
    Returns
    -------
    model : :class:`.DTMModel`
    
    Examples
    --------

    From a path:
    
    .. code-block:: python
    
       >>> model = from_hdf5('/path/to/my/HDF5DTMModel.h5')
       
    """

    if type(HD_or_path) is str:
        hmodel = HDF5DTMModel(datapath=HD_or_path)
    elif type(HD_or_path) is HDF5DTMModel:
        hmodel = HD_or_path
    else:
        raise AttributeError('Must provide datapath or HDF5DTMModel object.')

    metadata = { k:v for k,v in hmodel.metadata.iteritems() }
    vocabulary = { k:v for k,v in hmodel.vocabulary.iteritems() }
    model = DTMModel(   e_theta=numpy.array(hmodel.e_theta),
                        phi=numpy.array(hmodel.phi),
                        metadata=metadata,
                        vocabulary=vocabulary    )

    return model