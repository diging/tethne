import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

from util import *
from ...model import LDAModel

class HDF5LDAModel(LDAModel):
    """
    Provides HDF5 persistence for :class:`.LDAModel`\.
    """

    def __init__(   self, theta=None, phi=None, metadata=None,
                    vocabulary=None, datapath=None):
                    
        logger.debug('HDF5LDAModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('LDAModel', datapath)
        logger.debug('HDF5LDAModel: got h5file at path {0}'.format(self.path))
        
        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5LDAModel: initialized array group.')
        
        self.theta = get_or_create_array(   self.h5file, self.agroup,
                                            'theta', theta  )
        self.M = self.theta.shape[0]
        logger.debug('HDF5LDAModel: initialized theta with shape {0}'
                                                      .format(self.theta.shape))

        self.phi = get_or_create_array(self.h5file, self.agroup, 'phi', phi)
        self.Z = self.phi.shape[0]
        self.W = self.phi.shape[1]
        logger.debug('HDF5LDAModel: initialized phi with shape {0}'
                                                        .format(self.phi.shape))

        self.metadata = HDF5Metadata(self.h5file, metadata)
        logger.debug('HDF5LDAModel: initialized metadata with {0} records'
                                                    .format(len(self.metadata)))
        
        self.vgroup = get_or_create_group(self.h5file, 'vocabulary')
        logger.debug('HDF5LDAModel: initialized vocabulary group')
        
        if 'vocabulary' not in self.vgroup:
            vocab_sorted = [ vocabulary[k] for k in sorted(vocabulary.keys()) ]
        else:
            vocab_sorted = []
        self.vocabulary = HDF5ArrayDict(    self.h5file, self.vgroup,
                                            'vocabulary', vocab_sorted  )
        self.h5file.flush()
        
        logger.debug('HDF5LDAModel: initialized vocabulary with {0} entries'
                                                  .format(len(self.vocabulary)))

        # Doesn't get stored.
        self.lookup = { v['id']:k for k,v in self.metadata.iteritems() }

        logger.debug('HDF5LDAModel: initialization complete')

def to_hdf5(model, datapath=None):
    """
    Generate a :class:`.HDF5LDAModel` from the current instance.
    
    Parameters
    ----------
    model : :class:`.LDAModel`
    datapath : str
        (optional) Path to an HDF5 repository. If not provided, generates
        a temporary path, which can be accessed as the ``.path`` attribute.
    
    Returns
    -------
    hdf5_model : :class:`.HDF5LDAModel`
    """

    hdf5_model = HDF5LDAModel(  theta = numpy.array(model.theta),
                                phi = numpy.array(model.phi),
                                metadata = model.metadata,
                                vocabulary = model.vocabulary,
                                datapath = datapath )

    return hdf5_model

def from_hdf5(HD_or_path):
    """
    Load a :class:`.LDAModel` from a :class:`.HDF5LDAModel`\.
    
    Parameters
    ----------
    HD_or_path : str or :class:`.HDF5LDAModel`
        If str, must be a path to a :class:`.HDF5LDAModel` HDF5 repo.
        
    Returns
    -------
    model : :class:`.LDAModel`
    
    Examples
    --------

    From a path:
    
    .. code-block:: python
    
       >>> model = from_hdf5('/path/to/my/HDF5LDAModel.h5')
       
    """

    if type(HD_or_path) is str:
        hmodel = HDF5LDAModel(datapath=HD_or_path)
    elif type(HD_or_path) is HDF5LDAModel:
        hmodel = HD_or_path
    else:
        raise AttributeError('Must provide datapath or HDF5LDAModel object.')

    model = LDAModel(   theta=hmodel.theta, phi=hmodel.phi,
                        metadata=hmodel.metadata,
                        vocabulary=hmodel.vocabulary    )

    return model
