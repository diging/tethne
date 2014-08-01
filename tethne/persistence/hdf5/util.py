"""
Helper classes and methods for :mod:`tethne.persistence.hdf5`\.

TODO: move away from index table pattern, toward index array pattern.
"""

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

import numpy
import tables
import tempfile
import uuid
import cPickle as pickle
import urllib
from unidecode import unidecode

import os

from ...classes import Paper

pytype = {  tables.atom.BoolAtom: bool,
            tables.atom.UInt8Atom: int,
            tables.atom.Int16Atom: int,
            tables.atom.UInt16Atom: int,
            tables.atom.Int32Atom: int,
            tables.atom.UInt32Atom: long,
            tables.atom.Int64Atom: long,
            tables.atom.UInt64Atom: long,
            tables.atom.Float32Atom: float,
            tables.atom.Float64Atom: float,
            tables.atom.Complex64Atom: complex,
            tables.atom.Complex128Atom: complex,
            tables.atom.StringAtom: str,
            tables.atom.Time32Atom: int,
            tables.atom.Time64Atom: float,
            numpy.int32: int }

def get_h5file(typename, datapath=None):
    """
    Load or create an HDF5 data file.
    """

    # Where to save the HDF5 data file?
    if datapath is None:
        datapath = tempfile.mkdtemp()
        logger.debug('Generated datapath {0}.'.format(datapath))

    this_uuid = uuid.uuid4()    # Unique identifier for this H5File

    # Load or create HDF5 repository.
    if datapath.split('.')[-1] == 'h5': # Path to file specified.
        path = datapath
    else:   # Generate a new path.
        logger.debug('H5File has UUID {0}.'.format(this_uuid))
        path = '{0}/{1}-{2}.h5'.format(datapath, typename, this_uuid)

    # mode = 'a' will create a new file if no file exists.
    if os.path.exists(path):
        h5file = tables.openFile(path, mode='a')
    else:
        title = '{0}-{1}'.format(typename, this_uuid)
        h5file = tables.openFile(path, mode='a', title=title)

    return h5file, path, uuid

def get_or_create_group(h5file, name, where=None):
    if where is None:
        if '/' + name not in h5file:
            group = h5file.createGroup('/', name)
        else:
            group = h5file.getNode('/' + name)
    else:
        if name not in where:
            group = h5file.createGroup(where, name)
        else:
            group = h5file.getNode(where, name)
    return group

def get_or_create_table(h5file, group, name, model):
    if name not in group:
        table = h5file.createTable(group, name, model)
    else:
        table = h5file.getNode(group, name)
    return table

def get_or_create_array(h5file, group, name, values):
    if name not in group:
        array = h5file.create_array(group, name, values)
    else:
        array = h5file.getNode(group, name)
    return array

class FieldIndex(tables.IsDescription):
    """
    For storing metadata about fields.
    """
    name = tables.StringCol(100)    # name of a field.
    type = tables.StringCol(100)    # should correspond to a Python dtype.

class HDF5Metadata(dict):
    def __init__(self, h5file, metadata=None):
        self.h5file = h5file
        self.name = 'metadata'
        self.group = get_or_create_group(self.h5file, self.name)
        self.fields = get_or_create_table(self.h5file, self.group, 'fields', FieldIndex)
        self.field_values = {}
        
        if len(self.fields) == 0:
            # Get the names and types of metadata fields.
            fieldkeys = {}
            mvalues = { 'index': [] }
            for name, value in metadata.values()[0].iteritems():
                this_type = str(type(value))
                fieldkeys[name] = this_type
                mvalues[name] = []
            
            # Holds paper identifiers.
            indices = sorted(metadata.keys())   # Ensure consistent order.

            # Generate metadata vectors.
            for i in indices:
                for name,value in metadata[i].iteritems():
                    mvalues[name].append(value)

            # Generate a fields table.
            for name,this_type in fieldkeys.iteritems():
                query = 'name == b"{0}"'.format(name)
                matches = [ row for row in self.fields.where(query)]
                if len(matches) == 0:
                    fieldentry = self.fields.row
                    fieldentry['name'] = name
                    fieldentry['type'] = this_type
                    fieldentry.append()
            self.fields.flush()

        else:
            fieldkeys = { row[0]:None for row in self.fields.read() }
            mvalues = { k:[] for k in fieldkeys.keys() }

        # Get or create arrays that hold metadata vectors.
        for name in fieldkeys.keys():
            self.field_values[name] = get_or_create_array(  self.h5file,
                                                            self.group,
                                                            name, mvalues[name])

        # Prime values.
        for i in xrange(self.field_values.values()[0].shape[0]):
            self.__getitem__(i)

    def __setitem__(self, key, value):
        raise AttributeError('Values can only be set on __init__')

    def __getitem__(self, key):
        """
        For each field in `self.fields` table, retrieve the value for `key`
        from the corresponding metadata vector.
        """

        try:
            return dict.__getitem__(self, key)
        except:
            i = int(key)
            fielddata = { row['name']:row['type'] for row in self.fields }
            meta = {}
            for name, type in fielddata.iteritems():
                meta[name] = self._get_meta_entry(name, i, type)
            dict.__setitem__(self, key, meta)
            
        return meta

    def _get_meta_entry(self, name, index, this_type):
        """
        Retrieve value for `index` from the metadata vector `name`, and 
        cast as `type` before returning.
        """
        value = self.field_values[name][index]
        if this_type == str(type('')): return str(value)
        if this_type == str(type(1)): return int(value)
        if this_type == str(type(1.1)): return float(value)
        if this_type == str(type(u'')): return unicode(value)
        return value

    def __len__(self):
        return len(self.field_values.values()[0])

################################################################################
####                    Helper classes and methods.                         ####
################################################################################

class HDF5Paper(tables.IsDescription):
    """
    Provides persistence for :class:`.Paper` within a
    :class:`.HDF5Corpus`\.
    """
    mindex = tables.StringCol(100)
    aulast = tables.StringCol(1000)
    auinit = tables.StringCol(1000)
    atitle = tables.StringCol(200)
    jtitle = tables.StringCol(200)
    volume = tables.StringCol(6)
    issue = tables.StringCol(6)
    spage = tables.StringCol(6)
    epage = tables.StringCol(6)
    ayjid = tables.StringCol(200)
    doi = tables.StringCol(100)
    pmid = tables.StringCol(100)
    wosid = tables.StringCol(100)
    abstract = tables.StringCol(5000)
    accession = tables.StringCol(100)
    date = tables.Int32Col()
    citations = tables.StringCol(5000)  # List of citation keys.
    
class Index(tables.IsDescription):
    """
    For storing int : str pairs.
    """
    i = tables.Int32Col()
    mindex = tables.StringCol(1000)

class IntIndex(tables.IsDescription):    
    """
    For storing int : int pairs.
    """
    i = tables.Int32Col()
    mindex = tables.Int32Col()

class StrIndex(tables.IsDescription):
    """
    For storing str : str pairs.
    """
    i = tables.StringCol(100)
    mindex = tables.StringCol(100000)

class HDF5Axes(dict):
    """
    Organizes axes.
    """

    def __init__(self, h5file):
        logger.debug('Initialize HDF5Axes.')

        self.h5file = h5file
        
        # Load or create axes group.
        if '/axes' not in self.h5file:
            self.group = self.h5file.createGroup('/', 'axes')
        else:
            self.group = self.h5file.getNode('/axes')

    def __setitem__(self, key, value):
        logger.debug('key {0}'.format(key))
        if type(value.values()[0][0]) is str:
            keyatom = tables.StringAtom(200)
        elif type(value.values()[0][0]) is int:
            keyatom = tables.Int32Atom()

        logger.debug('keyatom: {0}'.format(keyatom))
        valuesatom = tables.StringAtom(200)

        dict.__setitem__(self, key,
            vlarray_dict(self.h5file, self.group, key, valuesatom, keyatom) )

#        dict.__setitem__(self, key, HDF5Axis(self.h5file, self.group, key))
        for k,v in value.iteritems():
            self[key][k] = v

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
#            if type(value.values()[0][0]) is str:
#                keyatom = tables.StringAtom(200)
#            elif type(value.values()[0][0]) is int:
#                keyatom = tables.Int32Atom()
#
#            valuesatom = tables.StringAtom(200)

            dict.__setitem__(self, key,
                vlarray_dict(self.h5file, self.group, key))#, valuesatom, keyatom))
#            dict.__setitem__(self, key, HDF5Axis(self.h5file, self.group, key))
            return dict.__getitem__(self, key)

    def __len__(self):
        return len(self.group._f_listNodes())/2
        

class HDF5Axis(dict):
    """
    Organizes a single axis.
    """

    def __init__(self, h5file, fgroup, name):
        self.h5file = h5file
        self.name = name
        
        # Load or create group.
        if name not in fgroup:
            self.group = self.h5file.createGroup(fgroup, name)
        else:
            self.group = self.h5file.getNode(fgroup, name)

    def __setitem__(self, key, value):
        name = '{0}_{1}'.format(self.name, key)
        h5dict = HDF5ArrayDict(self.h5file, self.group, name, value)
        dict.__setitem__(self, key, h5dict)

    def __len__(self):
        return len(self.group._f_listNodes())


class HDF5Features(dict):
    """
    Organizes feature-sets, each as a :class:`.HDF5Feature`\.
    """

    def __init__(self, h5file):
        logger.debug('Initialize HDF5Features.')

        self.h5file = h5file
        
        # Load or create features group.
        self.group = get_or_create_group(self.h5file, 'features')

    def __setitem__(self, key, value):
        logger.debug('HDF5Features.___setitem__ for key {0}.'.format(key))
        
        fset = HDF5FeatureSet(self.h5file, self.group, key)
        dict.__setitem__(self, key, fset)
        
        logger.debug('assign values for key {0}.'.format(key))
        for k,v in value.iteritems():
            self[key][k] = v

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            fset = HDF5FeatureSet(self.h5file, self.group, key)
            dict.__setitem__(self, key, fset)
            return dict.__getitem__(self, key)

            
class HDF5FeatureSet(dict):
    """
    Stores data about the distribution of a specific feature-set, e.g. unigrams,
    across papers in the :class:`.Corpus`\.
    """

    def __init__(self, h5file, fgroup, name):
        logger.debug('Initializing HDF5Feature with name {0}.'.format(name))
        self.h5file = h5file
        
        # Load or create a group.
        self.group = get_or_create_group(self.h5file, name, fgroup)

        self.name = name

        dict.__setitem__(self, 'features', HDF5FeatureValues(h5file, self.group, 'features'))

        logger.debug('...done.')

    def __setitem__(self, key, value):
        logger.debug('HDF5Feature ({0}): __setitem__ for key {1}, length {2}.'
                                            .format(self.name, key, len(value)))

        if key not in self:
            logger.debug('{0} does not exist, creating...'.format(key))
            if key == 'features':
                dict.__setitem__(self, key,
                    HDF5FeatureValues( self.h5file, self.group, key )    )

            elif key == 'papers':
                dict.__setitem__(self, key,
                    HDF5FeatureValues( self.h5file, self.group, key, keyatom=tables.Int32Atom(),
                                                                indexatom=tables.StringAtom(200)) )

                for k,v in value.iteritems():
                    self[key][k] = v
            else:
                values = numpy.array([ value[k] for k in sorted(value.keys()) ])
                dict.__setitem__(self, key,
                    HDF5ArrayDict( self.h5file, self.group, key, values ) )
        else:
            logger.debug('setting values for {0}...'.format(key))
            for k,v in value.iteritems():
                self[key][k] = v
        
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if key == 'features':
                dict.__setitem__(self, key,
                    HDF5FeatureValues( self.h5file, self.group, key )    )

            elif key == 'papers':
                dict.__setitem__(self, key,
                    HDF5FeatureValues( self.h5file, self.group, key, keyatom=tables.Int32Atom(),
                                                                indexatom=tables.StringAtom(200)) )

            else:
                dict.__setitem__(self, key,
                    HDF5ArrayDict( self.h5file, self.group, key, [] )   )

            return dict.__getitem__(self, key)

class HDF5ArrayDict(dict):
    def __init__(self, h5file, group, name, values):
        self.h5file = h5file
        self.group = group
        self.name = name
        
        # Load or create a new array.
        self.array = get_or_create_array(self.h5file, self.group, name, values)
    
        # Prime values.
        for i in xrange(len(self.array)):
            self.__getitem__(i)

    def __setitem__(self, key, value):
        self.array[key] = value
        dict.__setitem__(self, key, value)
    
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            value = self.array[key]
            dict.__setitem__(self, key, value)
        return value
        
    def items(self):
        return { i:self.array[i] for i in xrange(len(self.array)) }.items()
    
    def iteritems(self):
        i = 0
        while i < len(self.array):
            yield i, self.array[i]
            i += 1
    
    def __len__(self):
        return len(self.array)
        
    def values(self):
        return [ self.array[i] for i in xrange(len(self.array)) ]
    
    def keys(self):
        return range(len(self.array))
        
class HDF5SparseValues(dict):
    """
    
    Parameters
    ----------
    h5file
    group
    name
    iatom
    katom
    indexatom
    """
    def __init__(self, h5file, group, name, iatom, katom, indexatom):
        logger.debug('initialize HDF5SparseValues for {0}'.format(name))
        self.h5file = h5file
        self.group = get_or_create_group(self.h5file, name, group)
    
        # For sparse arrays like index:[ (i1,k1), (i2,k2) ... (iN,kN) ], self.I
        #  holds a vlarray index:[ i1,i2,...iN ], and self.K holds a vlarray
        #  index:[ k1,k2,...kN ].
        self.I = vlarray_dict(  h5file, self.group,
                                '{0}_I'.format(name),
                                iatom, indexatom    )
        self.K = vlarray_dict(  h5file, self.group,
                                '{0}_K'.format(name),
                                katom, indexatom    )

    def __setitem__(self, key, value):
        # Split sparse vector [ (i1,k1), (i2,k2) ... (iN,kN) ] into constituents
        # [ i1,i2,...iN ] and [ k1,k2,...kN ].
        try:
            I_values, K_values = zip(*value)
        except:     # OK to store empty vectors.
            I_values = []
            K_values = []
        
        # Store the constituent vectors separately.
        self.I[key] = I_values
        self.K[key] = K_values

    def __getitem__(self, key):
        # Load constituent vectors [ i1,i2,...iN ] and [ k1,k2,...kN ], and
        #  reconstruct sparse vector [ (i1,k1), (i2,k2) ... (iN,kN) ]
        I_values = self.I[key]
        K_values = self.K[key]

        return zip(I_values, K_values)

    def __len__(self):
        return len(self.I)
    
    def iteritems(self):
        i = 0
        keys = self.I.keys()
        while i < len(self.I):
            yield keys[i], self.__getitem__(keys[i])
            i += 1


class HDF5FeatureValues(dict):
    def __init__(self, h5file, group, name, keyatom=tables.StringAtom(200),
                                            indexatom=tables.Int32Atom(),
                                            valueatom=tables.Float64Atom()):
        self.h5file = h5file
        self.group = get_or_create_group(self.h5file, name, group)

        self.indices = vlarray_dict(    self.h5file, self.group,
                                        'indices', indexatom, keyatom   )
        self.values  = vlarray_dict(    self.h5file, self.group,
                                        'values', valueatom, keyatom    )

    def __setitem__(self, key, value):
        i,v = zip(*value)
        self.indices[key] = list(i)
        self.values[key] = list(v)


    def __getitem__(self, key):
        i = self.indices[key]
        v = self.values[key]
        value = zip(i,v)
        return value

    def __len__(self):
        return len(self.indices)

    def iteritems(self):
        N = self.__len__()
        keys = self.indices.keys()
        i = 0
        while i < N:
            yield keys[i], self.__getitem__(keys[i])
            i += 1

class papers_table(dict):
    """
    Mimics the `papers` dict in :class:`.Paper`\, providing HDF5 persistence.

    Values should be set only once for a key.

    Parameters
    ----------
    h5file : tables.file.File
        A :class:`tables.file.File` object.
    index_by : str
        Key in :class:`.Paper` used to index papers in this 
        :class:`.Corpus`\.
    """
    def __init__(self, h5file, index_by, name, citations=None, 
                                               index_citation_by='ayjid'):
        self.h5file = h5file
        self.index_by = index_by
        
        # Load or create group.
        if '/{0}'.format(name) not in self.h5file:
            self.group = self.h5file.createGroup("/", name)
        else:
            self.group = self.h5file.getNode('/{0}'.format(name))

        # Load or create table.
        if 'papers_table' not in self.group:
            self.table = self.h5file.createTable(self.group, 'papers_table',
                                                             HDF5Paper)
            self.indexrows = self.table.cols.mindex.createIndex()
        else:
            self.table = self.h5file.getNode(self.group, 'papers_table')
        
        
        self.citations = citations
        self.index_citation_by = index_citation_by
    
    def _recast_value(self, to, value):
        """
        Recasts values from HDF5 table as Python types.
        """
        
        if to is list and type(value) is not list:  # avoid re-unpickling.
            if value is None or len(value) == 0:
                v = []
            else:   
                v = pickle.loads(str(value))
        else:
            v = to(value)
        
        return v
    
    
    def _to_paper(self, hdf5paper):
        """
        Yields a :class:`.Paper` from an :class:`.HDF5Paper`\.
        """
        paper = Paper()
        keys = self.table.description._v_dtypes.keys()
        for kname in keys:
            if kname == 'mindex': continue    # Not a valid field for Paper.

            if kname in paper.list_fields: to = list
            elif kname in paper.string_fields: to = str
            elif kname in paper.int_fields: to = int
            
            v = self._recast_value(to, hdf5paper[kname])

            if kname == 'citations':  # 'citations' should contain Papers.
                if self.citations is None: continue     # May not have any.
                try:
                    v = [ self._to_paper(self.citations[a]) for a in v ]
                except IndexError:
                    v = []

            paper[kname] = v
        return paper
        
    def __setitem__(self, key, value):
        hpaper = self.table.row
        hpaper['mindex'] = key

        for k, v in value.iteritems():
            if k in self.table.cols.__dict__:
                if v is not None:
                    # Lists will be pickled for storage.
                    if type(v) is list:
                        # Citations will be stored as list of citation indices.                        
                        if k == 'citations':    
                            if self.citations is None: continue
                            try:
                                v = [ a[self.index_citation_by] for a in v ]
                            except IndexError:
                                v = []
                        v = pickle.dumps(v)
                    hpaper[k] = v
        hpaper.append()
        self.table.flush()  # We need table completely up-to-date for subsequent
                            #  operations.
    
    def __getitem__(self, key):
        return [ self._to_paper(x) for x
                    in self.table.where('mindex == b"{0}"'.format(key)) ][0]
    
    def __len__(self):
        return len([ r for r in self.table])
    
    def __contains__(self, key):
        size = len([ self._to_paper(x) for x
                        in self.table.where('mindex == b"{0}"'.format(key)) ])
        return size > 0
    
    def iteritems(self):
        i = 0
        while i < len(self.table):
            x = self.table[i]
            yield x['mindex'],self._to_paper(x)
            i += 1
            
    def values(self):
        return [ self._to_paper(x) for x in self.table ]
    
    def keys(self):
        return [ x['mindex'] for x in self.table ]

class vlarray_dict(dict):
    """
    Provides dict-like access to an HDF5 VLArray.
    """

    def __init__(self, h5file, group, name, atom, keyatom):
        logger.debug('initialize vlarray_dict with name {0}'.format(name))
        
        self.h5file = h5file
        self.group = group
        self.name = name
        self.atom = atom
        self.keyatom = keyatom

        try:
            self.pytype = pytype[type(atom)]
        except KeyError:
            raise NotImplementedError('No equivalent Python type for atom.')

        # Load or create vlarray.
        if self.name not in self.group:
            logger.debug('no node for VLArray {0} in group {1}, creating...'
                                                .format(self.name, self.group))

            self.vlarray = self.h5file.createVLArray(   self.group,
                                                        self.name,
                                                        self.atom   )
            # Pad with dummy data.
            if self.atom.shape == ():
                self.vlarray.append([self.atom.dflt])
            else:
                size = numpy.zeros(shape=self.atom.shape).size
                padding = numpy.array([ self.atom.dflt for d in xrange(size)]) \
                                                       .reshape(self.atom.shape)
                self.vlarray.append(padding)
        else:
            logger.debug('found node for VLArray {0} in group {1}, loading...'
                                                 .format(self.name, self.group))
            self.vlarray = self.h5file.getNode(self.group, self.name)
            self.atom = self.vlarray.atom

        indexname = '{0}_keys'.format(self.name)
        
        # If create, pads with dummy index at 0.
        if indexname not in self.group:
            self.I = self.h5file.createEArray(  self.group,
                                                indexname,
                                                keyatom, (0,)   )
            if keyatom.dflt == 0: dflt = -1
            if keyatom.dflt == 0.0: dflt = -1.
            else: dflt = keyatom.dflt
            self.I.append([dflt])
        else:
            self.I = self.h5file.getNode(self.group, indexname)
            self.keyatom = self.I.atom

    def __setitem__(self, key, value):
        if key not in self:
            self.I.append([key])
            self.vlarray.append([ v for v in  value ])
            dict.__setitem__(self, key, value)

    def __getitem__(self, key):
        try:
            i = list(self.I.read())[1:].index(key)
            data = self.vlarray.read()[1:]
        except ValueError:
            raise KeyError()

        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if self.atom.shape != ():
                value = numpy.array([   [ self.pytype(v) for v in d ]
                                            for d in data[i]    ])
            else:
                value = numpy.array([ self.pytype(v) for v in data[i] ])
            dict.__setitem__(self, key, value)
            return value

    def __contains__(self,key):
        return key in self.keys()
    
    def values(self):
        values = [ self[i] for i in self.I.read()[1:] ]
        return values
    
    def keys(self):
        return self.I.read()[1:]
    
    def __len__(self):
        return len(self.vlarray) -1  # Compensate for padding.

    def __str__(self):
        return str(self.items())

    def items(self):
        return zip(self.keys(), self.values())

    def iteritems(self):
        return iter(zip(self.keys(), self.values()))
