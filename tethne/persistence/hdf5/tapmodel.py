import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from util import *
from ...model import TAPModel
from .graphcollection import HDF5Graph

class HDF5TAPModel(TAPModel):
    """
    Provides HDF5 persistence for :class:`.TAPModel`\.
    """

    def __init__(self, T, datapath=None):
        logger.debug('HDF5TAPModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('TAPModel', datapath)
        logger.debug('HDF5TAPModel: got h5file at path {0}'.format(self.path))
        
        self.group = get_or_create_group(self.h5file, 'graph')
        self.G = HDF5Graph(self.h5file, self.group, 'graph', T.G)
        self.N = len(self.G.nodes())
        self.M = len(self.G.edges())
        logger.debug('HDF5TAPModel: HDF5Graph with {0} nodes'.format(self.N) + \
                     ' and {0} edges'.format(self.M))
        
        
        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5TAPModel: initialized array group.')

        self.pgroup = get_or_create_group(self.h5file, 'parameters')
        
        self._init_param('theta', T)
        self._init_param('a', T)
        self._init_param('b', T)
        self._init_param('r', T)
        self._init_param('g', T)

        self.N_d = len(self.theta)

        # Not stored.
        self.yold = { i:{k:0 for k in xrange(self.T) }
                        for i in sorted(self.G.nodes()) }
        self.yold_values = { i:{k:0. for k in xrange(self.T) }
                                for i in sorted(self.G.nodes()) }

        logger.debug('HDF5TAPModel: initialized parameters.')

    def _init_param(self, param, T):
        if param in self.pgroup:
            setattr(self, param, vlarray_dict(self.h5file, self.pgroup, param,
                                       tables.Float32Atom(),tables.Int32Atom()))
            if param == 'theta':
                self.T = self.theta.atom.shape[0]
        else:
            if param == 'theta':
                self.T = T.T
                atom = tables.Float32Atom()
            else:
                atom = tables.Float32Atom(shape=(self.T,))
            setattr(self, param, vlarray_dict(self.h5file, self.pgroup, param,
                                                      atom, tables.Int32Atom()))
            for k,v in getattr(T, param).iteritems():
                getattr(self, param)[k] = v

