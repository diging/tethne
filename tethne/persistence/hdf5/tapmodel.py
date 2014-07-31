import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from util import *
from ...model import TAPModel
from .graphcollection import HDF5Graph

import numpy

class HDF5TAPModel(TAPModel):
    """
    Provides HDF5 persistence for :class:`.TAPModel`\.
    """

    def __init__(self, T=None, datapath=None):
        logger.debug('HDF5TAPModel: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('TAPModel', datapath)
        logger.debug('HDF5TAPModel: got h5file at path {0}'.format(self.path))
        
        if T is not None:
            graph = T.G
        else:
            graph = None
        
        self.group = get_or_create_group(self.h5file, 'graph')
        self.G = HDF5Graph(self.h5file, self.group, 'graph', graph)
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
        self.yold_values = { i: { k:0. for k in xrange(self.T) }
                                  for i in sorted(self.G.nodes()) }

        logger.debug('HDF5TAPModel: initialized parameters.')

    def _init_param(self, param, T):
        if param in self.pgroup:
            setattr(self, param, vlarray_dict(self.h5file, self.pgroup, param,
                                       tables.Float32Atom(),tables.Int32Atom()))
            if param == 'theta':
                self.T = self.theta.values()[0].shape[0]
        else:
            if param == 'theta':
                self.T = int(T.T)
                atom = tables.Float32Atom()
            else:
                atom = tables.Float32Atom(shape=(self.T,))
            setattr(self, param, vlarray_dict(self.h5file, self.pgroup, param,
                                                      atom, tables.Int32Atom()))
            for k,v in getattr(T, param).iteritems():
                getattr(self, param)[k] = numpy.array(v)

def to_hdf5(model, datapath=None):
    """
    Generate a :class:`.HDF5TAPModel` from the current instance.
    
    Parameters
    ----------
    model : :class:`.TAPModel`
    datapath : str
        (optional) Path to an HDF5 repository. If not provided, generates
        a temporary path, which can be accessed as the ``.path`` attribute.
    
    Returns
    -------
    hdf5_model : :class:`.HDF5TAPModel`
    """

    hdf5_model = HDF5TAPModel(model, datapath=datapath)

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
        hmodel = HDF5TAPModel(datapath=HD_or_path)
    elif type(HD_or_path) is HDF5TAPModel:
        hmodel = HD_or_path
    else:
        raise AttributeError('Must provide datapath or HDF5LDAModel object.')

    G = hmodel.G.to_graph()
    theta = { k:numpy.array(v) for k,v in hmodel.theta.iteritems() }
    model = TAPModel(G, theta)#, damper=hmodel.damper)

    model.a = { k:numpy.array(v) for k,v in hmodel.a.iteritems() }
    model.r = { k:numpy.array(v) for k,v in hmodel.r.iteritems() }
    model.b = { k:numpy.array(v) for k,v in hmodel.b.iteritems() }
    model.g = { k:numpy.array(v) for k,v in hmodel.g.iteritems() }

    model.N = hmodel.N
    model.M = hmodel.M
    model.T = hmodel.T

    model.yold = hmodel.yold
    model.yold_values = hmodel.yold_values

    return model
