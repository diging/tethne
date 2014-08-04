"""
Classes and methods for persisting Tethne data objects in HDF5.

.. autosummary::
   :nosignatures:

   to_hdf5
   from_hdf5
   
"""

import graphcollection, ldamodel, tapmodel, dtmmodel, corpus
from util import get_h5file
from ...classes import GraphCollection, Corpus
from ...model import LDAModel, TAPModel, DTMModel

htypes = {
    'GraphCollection': graphcollection.from_hdf5,
    'LDAModel': ldamodel.from_hdf5,
    'TAPModel': tapmodel.from_hdf5,
    'DTMModel': dtmmodel.from_hdf5,
    }


def to_hdf5(obj, datapath=None):
    """
    Convert a Tethne data object to its HDF5 representation.
    
    Parameters
    ----------
    obj : object
        Can be a :class:`.Corpus`\, :class:`.GraphCollection`\, or an object
        from :mod:`.model`\.
    datapath : str
        Path to HDF5 file (will be created).
        
    Returns
    -------
    HDF5 object
    
    Examples
    --------
    
    .. code-block:: python
    
       >>> from tethne.persistence import hdf5
       >>> MyHDF5Corpus = hdf5.to_hdf5(MyCorpus, datapath='/path/to/my/data.h5')
       >>> MyHDF5Corpus
       <tethne.persistence.hdf5.corpus.HDF5Corpus object at 0x10770fd10>
       
    """
    
    if type(obj) is GraphCollection:
        return graphcollection.to_hdf5(obj, datapath=datapath)
    elif type(obj) is LDAModel:
        return ldamodel.to_hdf5(obj, datapath=datapath)
    elif type(obj) is TAPModel:
        return tapmodel.to_hdf5(obj, datapath=datapath)
    elif type(obj) is DTMModel:
        return dtmmodel.to_hdf5(obj, datapath=datapath)
    elif type(obj) is Corpus:
        return corpus.to_hdf5(obj, datapath=datapath)

def from_hdf5(HD_or_path):
    """
    Load a data object from a HDF5 object, or a path to an HDF5 repository.
    
    Parameters
    ----------
    HD_or_path : str or object
        If an object, expects an object from :mod:`.persistence.hdf5`\. If str,
        expects a path to an H5 repo, and will determine object type from the
        contents of that file.
        
    Returns
    -------
    object
        Corresponding Tethne data object (e.g. :class:`.Corpus`\).
        
    Examples
    --------
    
    From an HDF5 object:
    
    .. code-block:: python
    
       >>> from tethne.persistence import hdf5
       >>> MyCorpus = hdf5.from_hdf5(MyHDF5Corpus)
       >>> MyCorpus
       <tethne.classes.corpus.Corpus object at 0x1007d5fd0>
    
    From an HDF5 repo containing a :class:`.HDF5Corpus`\:
    
    .. code-block:: python
    
       >>> MyCorpus = hdf5.from_hdf5('/path/to/my/corpus.h5')
       >>> MyCorpus
       <tethne.classes.corpus.Corpus object at 0x1007d5fd0>
        
    """
    
    if type(HD_or_path) is str:     # Determine object type from File.title.
        h5file,a,b = get_h5file('', HD_or_path)
        htype = h5file.title.split('-')[0]
        
        return htypes[htype](HD_or_path)

    # Load directly from HDF5 object.
    if type(HD_or_path) is graphcollection.HDF5GraphCollection:
        return graphcollection.from_hdf5(HD_or_path)

    elif type(HD_or_path) is ldamodel.HDF5LDAModel:
        return ldamodel.from_hdf5(HD_or_path)

    elif type(HD_or_path) is tapmodel.HDF5TAPModel:
        return tapmodel.from_hdf5(HD_or_path)

    elif type(HD_or_path) is dtmmodel.HDF5DTMModel:
        return dtmmodel.from_hdf5(HD_or_path)

    elif type(HD_or_path) is corpus.HDF5Corpus:
        return coprus.from_hdf5(HD_or_path)
