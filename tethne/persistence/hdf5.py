import numpy
import tables
from ..classes import Paper, DataCollection
import tempfile
import uuid
import cPickle as pickle

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
            tables.atom.Time64Atom: float }

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
    mindex = tables.StringCol(100)

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
    mindex = tables.StringCol(100)
    
class HDF5Features(dict):
    def __init__(self, h5file):
        self.h5file = h5file
        if '/features' not in self.h5file:
            self.group = self.h5file.createGroup('/', 'features')
        else:
            self.group = self.h5file.getNode('/features')
        
    def __setitem__(self, key, value):
        if '/{0}'.format(key) in self.h5file:
            #raise ValueError('Feature with name {0} already set.'.format(key))
            key = key + 'boodaooaaoaaopaooloobao'

        dict.__setitem__(self, key, HDF5Feature(self.h5file, self.group, key))

        for k,v in value.iteritems():
            self[key][k] = v
            
class HDF5Feature(dict):
    def __init__(self, h5file, fgroup, name):

        self.h5file = h5file
        self.group = self.h5file.createGroup(fgroup, name)

        dict.__setitem__(self, 'index', HDF5Dict(h5file, self.group, 'index', Index))
        dict.__setitem__(self, 'features', HDF5PickleDict(h5file, self.group, 'features', StrIndex))
        dict.__setitem__(self, 'counts', HDF5Dict(h5file, self.group, 'counts', IntIndex))
        dict.__setitem__(self, 'documentCounts', HDF5Dict(h5file, self.group, 'counts', IntIndex))

    def __setitem__(self, key, value):
        if key in self:
            for k,v in value.iteritems():
                self[key][k] = v

class HDF5Dict(dict):
    def __init__(self, h5file, group, name, tabletype):
        self.h5file = h5file
        self.group = group
        if name in self.group:
            self.table = self.group.__dict__['_v_children'][name]
        else:
            self.table = self.h5file.createTable(self.group, name, tabletype)
            self.table.cols.i.createIndex()
    
    def _pack_value(self, value):
        """
        Simply returns value.
        """
        return value
    
    def _unpack_value(self, value):
        """
        Simply returns value.
        """
        return value
        
    def __setitem__(self, key, value):
        if type(key) is int or type(key) is float:
            qstring = 'i == {0}'
        else:
            qstring = 'i == b"{0}"'

        if len( [ i for i in self.table.where(qstring.format(str(key))) ] ) > 0:
            raise ValueError('Value for {0} already set.'.format(str(key)))
        
        row = self.table.row
        row['i'] = key
        row['mindex'] = self._pack_value(value) # TODO: unicode/encoding problems here.
        row.append()
        self.table.flush()
        self.h5file.flush()
    
    def __getitem__(self, key):
        if type(key) is int or type(key) is float:
            qstring = 'i == {0}'
        else:
            qstring = 'i == b"{0}"'
                
        value = [ i['mindex'] for i in self.table.where(qstring.format(str(key))) ][0]
        return self._unpack_value(value)

    def keys(self):
        return [ i['i'] for i in self.table ]

    def values(self):
        return [ self._unpack_value(i['mindex']) for i in self.table ]

    def items(self):
        return { i['i']:self._unpack_value(i['mindex']) for i in self.table }

class HDF5PickleDict(HDF5Dict):
    def _pack_value(self, value):
        return pickle.dumps(value)
    
    def _unpack_value(self, value):
        return pickle.loads(value)                                            

class HDF5DataCollection(DataCollection):
    def __init__(self, papers, features=None, index_by='wosid',
                                              index_citation_by='ayjid',
                                              exclude_features=set([]),
                                              datapath=None):
        # Where to save the HDF5 data file?
        if datapath is None:
            self.datapath = tempfile.mkdtemp()
        else:
            self.datapath = datapath
            
        self.uuid = uuid.uuid4()    # Unique identifier for this DataCollection.
        self.path = '{0}/DataCollection-{1}.h5'.format(self.datapath, self.uuid)
        self.h5file = tables.openFile(self.path, mode = "w",
                                   title='DataCollection-{0}'.format(self.uuid))
        self.group = self.h5file.createGroup("/", 'arrays')
        
        self.features = HDF5Features(self.h5file)
        self.authors = vlarray_dict(self.h5file, self.group, 
                                    'authors', tables.StringAtom(100))

        # { str(f) : feature }
        self.citations = papers_table(self.h5file, index_citation_by,
                                                   'citations')

        self.papers = papers_table(self.h5file, index_by, 'papers', 
                                        citations=self.citations,
                                        index_citation_by=index_citation_by)

        # { str(f) : [ str(p) ] }
        self.papers_citing = vlarray_dict(self.h5file, self.group,
                                        'papers_citing', tables.StringAtom(100))
        
        self.axes = {}
        self.index_by = index_by    # Field in Paper, e.g. 'wosid', 'doi'.
        self.index_citation_by = index_citation_by        
        
        self.index(papers, features, index_by, index_citation_by,
                                               exclude_features)
    

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
        self.group = self.h5file.createGroup("/", name)
        self.table = self.h5file.createTable(self.group, 'papers_table',
                                                               HDF5Paper)
        self.indexrows = self.table.cols.mindex.createIndex()
        
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
        self.table.flush() 
    
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
        
        self.index = self.h5file.createTable(self.group,
                                                '{0}_index'.format(self.name),
                                                Index)
        self.vlarray = self.h5file.createVLArray(self.group, self.name,
                                                             self.atom)

        self.index.cols.mindex.createIndex()        
        
    def __setitem__(self, key, value):
        if key not in self:
            i = len(self.vlarray)
            ind = self.index.row
            ind['i'] = i
            ind['mindex'] = key
            ind.append()
            self.index.flush()
        
        self.vlarray.append(value)
        self.vlarray.flush()

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

