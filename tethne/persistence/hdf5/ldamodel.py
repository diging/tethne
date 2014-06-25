import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from util import *
from ...model import LDAModel

class HDF5LDAModel(LDAModel):
    """
    Provides HDF5 persistence for :class:`.LDAModel`\.
    """

    def __init__(self, theta, phi, metadata, vocabulary, datapath=None):
        logger.debug('HDF5LDAModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('LDAModel', datapath)
        logger.debug('HDF5LDAModel: got h5file at path {0}'.format(self.path))
        
        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5LDAModel: initialized array group.')
        
        self.theta = get_or_create_array(self.h5file, self.agroup,
                                         'theta', theta)
        self.M = theta.shape[0]
        logger.debug('HDF5LDAModel: initialized theta with shape {0}'
                                                      .format(self.theta.shape))

        self.phi = get_or_create_array(self.h5file, self.agroup, 'phi', phi)
        self.Z = phi.shape[0]
        self.W = phi.shape[1]
        logger.debug('HDF5LDAModel: initialized phi with shape {0}'
                                                        .format(self.phi.shape))

        self.metadata = HDF5Metadata(self.h5file, metadata)
        logger.debug('HDF5LDAModel: initialized metadata with {0} records'
                                                    .format(len(self.metadata)))
        
        self.vgroup = get_or_create_group(self.h5file, 'vocabulary')
        logger.debug('HDF5LDAModel: initialized vocabulary group')
        
        vocab_sorted = [ vocabulary[k] for k in sorted(vocabulary.keys()) ]
        self.vocabulary = HDF5ArrayDict(self.h5file, self.vgroup,
                                        'vocabulary', vocab_sorted)

        self.h5file.flush()
        
        logger.debug('HDF5LDAModel: initialized vocabulary with {0} entries'
                                                  .format(len(self.vocabulary)))

        # Doesn't get stored.
        self.lookup = { v['id']:k for k,v in metadata.iteritems() }

        logger.debug('HDF5LDAModel: initialization complete')