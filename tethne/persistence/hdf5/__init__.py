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
