import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from util import *
from ...model import DTMModel

class HDF5DTMModel(DTMModel):
    """
    Provides HDF5 persistence for :class:`.DTMModel`\.
    """

    def __init__(self, e_theta, phi, metadata, vocabulary, datapath=None):
        """
        Initialize the :class:`.DTMModel`\.
        
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
        """

        logger.debug('HDF5DTMModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('DTMModel', datapath)
        logger.debug('HDF5DTMModel: got h5file at path {0}'.format(self.path))

        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5DTMModel: initialized array group.')
        
        self.e_theta = get_or_create_array(self.h5file, self.agroup,
                                           'e_theta', e_theta)
        self.Z = e_theta.shape[0]   # Number of topics.
        self.M = e_theta.shape[1]   # Number of documents.
        logger.debug('HDF5DTMModel: initialized theta with shape {0}'
                                                    .format(self.e_theta.shape))

        self.phi = get_or_create_array(self.h5file, self.agroup, 'phi', phi)
        self.W = phi.shape[1]    # Number of words.
        self.T = phi.shape[2]    # Number of time periods.
        logger.debug('HDF5DTMModel: initialized phi with shape {0}'
                                                        .format(self.phi.shape))

        self.metadata = HDF5Metadata(self.h5file, metadata)
        logger.debug('HDF5DTMModel: initialized metadata with {0} records'
                                                    .format(len(self.metadata)))
        
        self.vgroup = get_or_create_group(self.h5file, 'vocabulary')
        logger.debug('HDF5DTMModel: initialized vocabulary group')
        
        vocab_sorted = [ vocabulary[k] for k in sorted(vocabulary.keys()) ]
        self.vocabulary = HDF5ArrayDict(self.h5file, self.vgroup,
                                        'vocabulary', vocab_sorted)

        self.h5file.flush()
        
        logger.debug('HDF5DTMModel: initialized vocabulary with {0} entries'
                                                  .format(len(self.vocabulary)))

        # Doesn't get stored.
        self.lookup = { v['id']:k for k,v in metadata.iteritems() }

        logger.debug('HDF5DTMModel: initialization complete')