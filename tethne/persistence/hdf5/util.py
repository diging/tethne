import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

import numpy
import tables
import tempfile
import uuid
import cPickle as pickle
import urllib
from unidecode import unidecode

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

    # Load or create HDF5 repository.
    if datapath.split('.')[-1] == 'h5':
        path = datapath
        title = ''
    else:   # New h5 file.
        this_uuid = uuid.uuid4()    # Unique identifier for this H5File
        logger.debug('H5File has UUID {0}.'.format(this_uuid))
        path = '{0}/{1}-{2}.h5'.format(datapath, typename, this_uuid)
        title = '{0}-{1}'.format(typename, uuid)

    # mode = 'a' will create a new file if no file exists.
    h5file = tables.openFile(path, mode = 'a', title=title)

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

        # Get or create arrays that hold metadata vectors.
        for name in fieldkeys.keys():
            self.field_values[name] = get_or_create_array(self.h5file, self.group, name, mvalues[name])

    def __setitem__(self, key, value):
        raise AttributeError('Values can only be set on __init__')

    def __getitem__(self, key):
        """
        For each field in `self.fields` table, retrieve the value for `key`
        from the corresponding metadata vector.
        """

        i = int(key)
        fielddata = { row['name']:row['type'] for row in self.fields }
        meta = {}
        for name, type in fielddata.iteritems():
            meta[name] = self._get_meta_entry(name, i, type)

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
    :class:`.HDF5DataCollection`\.
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
        logger.debug('HDF5Axes.__setitem__ for key {0}'.format(key))

        dict.__setitem__(self, key, HDF5Axis(self.h5file, self.group, key))
        for k,v in value.iteritems():
            self[key][k] = v

    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            dict.__setitem__(self, key, HDF5Axis(self.h5file, self.group, key))
            return dict.__getitem__(self, key)

    def __len__(self):
        return len(self.group._f_listNodes())
        

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
        if '/features' not in self.h5file:
            self.group = self.h5file.createGroup('/', 'features')
        else:
            self.group = self.h5file.getNode('/features')
        
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
    across papers in the :class:`.DataCollection`\.
    """

    def __init__(self, h5file, fgroup, name):
        logger.debug('Initializing HDF5Feature with name {0}.'.format(name))
        self.h5file = h5file
        
        # Load or create a group.
        if name not in fgroup:
            self.group = self.h5file.createGroup(fgroup, name)
        else:
            self.group = self.h5file.getNode(fgroup, name)
        self.name = name

        dict.__setitem__(self, 'features', HDF5FeatureValues(h5file, self.group))

        logger.debug('...done.')

    def __setitem__(self, key, value):
        logger.debug('HDF5Feature ({0}): __setitem__ for key {1}, and value with length {2}.'.format(self.name, key, len(value)))    

        if key not in self:
            if key == 'features':
                dict.__setitem__(self, 'features', HDF5FeatureValues(self.h5file, self.group, value))
            else:
                values = numpy.array([ value[k] for k in sorted(value.keys()) ])
                dict.__setitem__(self, key, HDF5ArrayDict(self.h5file, self.group, key, values))

        else:
            for k,v in value.iteritems():
                self[key][k] = v
        
    def __getitem__(self, key):
        try:
            return dict.__getitem__(self, key)
        except KeyError:
            if key == 'features':
                dict.__setitem__(self, 'features', HDF5FeatureValues(self.h5file, self.group, []))
            else:
                dict.__setitem__(self, key, HDF5ArrayDict(self.h5file, self.group, key, []))
            return dict.__getitem__(self, key)

class HDF5ArrayDict(dict):
    def __init__(self, h5file, group, name, values):
        self.h5file = h5file
        self.group = group
        self.name = name
        
        # Load or create a new array.
        if name not in self.group:
            self.array = self.h5file.create_array(self.group, self.name, values)
        else:
            self.array = self.h5file.getNode(self.group, name)
        
    def __setitem__(self, key, value):
        self.array[key] = value
    
    def __getitem__(self, key):
        return self.array[key]
        
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
        

class HDF5FeatureValues(dict):
    def __init__(self, h5file, group):
        self.h5file = h5file
        
        # Load or create features group.
        if 'features' not in group:
            self.group = self.h5file.createGroup(group, 'features')
        else:
            self.group = self.h5file.getNode(group, 'features')

        # Load or create documents table.
        if 'documents' not in self.group:
            self.documents = self.h5file.create_table(self.group, 'documents',
                                                                  Index)
            self.documents.cols.i.create_index()
            self.documents.cols.mindex.create_index()
        else:
            self.documents = self.h5file.getNode(self.group, 'documents')

        
        self.d = {}
        
    def _get_or_create(self, key, value):
        # Index the document.
        i = len(self.documents)
        doc = self.documents.row
        doc['i'] = i
        doc['mindex'] = key
        doc.append()
        self.d[i] = key
        self.documents.flush()
    
        indices, values = zip(*value)
        iname = 'indices{0}'.format(i)
        kname = 'values{0}'.format(i)

        # Load or create I array.
        if iname not in self.group:
            I = self.h5file.create_array(self.group, iname,
                                         numpy.array(indices))
        else:
            I = self.h5file.getNode(self.group, iname)

        # Load or create K array.
        if kname not in self.group:
            K = self.h5file.create_array(self.group, kname,
                                         numpy.array(values))
        else:
            K = self.h5file.getNode(self.group, kname)

        return I,K
    
    def __setitem__(self, key, value):
        if key not in self:
            I,K = self._get_or_create(key, value)
            dict.__setitem__(self, key, (I,K))
        
    def __getitem__(self, key):
        try:
            I,K = dict.__getitem__(self, key)
        except KeyError:
            I,K = self._get_or_create(key, [])
        return zip(I,K)

    def __len__(self):
        return len(self.documents)
    
    def iteritems(self):
        i = 0
        while i < len(self.documents):
            yield self.d[i], self.__getitem__(self.d[i])
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
        :class:`.DataCollection`\.
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
        return len(self.table)
    
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

    def __init__(self, h5file, group, name, atom):
        self.h5file = h5file
        self.group = group
        self.name = name
        self.atom = atom
        
        try:
            self.pytype = pytype[type(atom)]
        except KeyError:
            raise NotImplementedError('No equivalent Python type for atom.')
        
        indexname = '{0}_index'.format(self.name)

        # Load or create index.
        if indexname not in self.group:
            self.index = self.h5file.createTable(self.group, indexname, Index)
        else:
            self.index = self.h5file.getNode(self.group, indexname)
        
        # Load or create vlarray.
        if self.name not in self.group:
            self.vlarray = self.h5file.createVLArray(self.group, self.name,
                                                                 self.atom)
        else:
            self.vlarray = self.h5file.getNode(self.group, self.name)
            self.index.cols.mindex.createIndex()

    def __setitem__(self, key, value):
        if key not in self:
            i = len(self.vlarray)
            ind = self.index.row
            ind['i'] = i
            ind['mindex'] = key
            ind.append()
        
        self.vlarray.append(value)

    def __getitem__(self, key):
        rset = [ x['i'] for x
                    in self.index.where('(mindex == b"{0}")'.format(key)) ]

        i = int(rset[0])
        return [ self.pytype(v) for v in self.vlarray[i] ]

    def __contains__(self,key):
        size = len([ self._to_paper(x) for x
                    in self.index.where('mindex == b"{0}"'.format(key)) ])
        return size > 0
    
    def values(self):
        return [ [ self.pytype(v) for v in x ] for x in self.vlarray ]
    
    def keys(self):
        return [ x['mindex'] for x in self.index ]  
    
    def __len__(self):
        return len(self.vlarray)

    def iteritems(self):
        return { x['mindex']:self[x['mindex']] for x in self.keys() }        