import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

import numpy
import tables
from ..classes import Paper, DataCollection
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

class HDF5DataCollection(DataCollection):
    """
    Provides HDF5 persistence for :class:`.DataCollection`\.
    
    The :class:`.HDF5DataCollection` uses a variety of tables and arrays to
    store data. The structure of a typical HDF5 repository for an instance
    of this class is:
    
    * ``/``
    
      * ``arrays``/
      
        * ``authors``: VLArray, :class:`.vlarray_dict`
        * ``authors_index``: table, see :class:`.vlarray_dict`
        * ``papers_citing``: VLArray, :class:`.vlarray_dict`
        * ``papers_citing_index``: table, see :class:`.vlarray_dict`
      
      * ``citations``/
      
        * ``papers_table``: table, :class:`.papers_table`
      
      * ``features``/
      
        * ``[ feature type ]``/

          * ``index``: table, :class:`.Index` -- int(f_i) : str(f)
          * ``features``: table, :class:`.StrIndex` -- str(p) : [ ( f_i, c) ]
          * ``counts``: table, :class:`.IntIndex` --  int(f_i) : int(C)
          * ``documentCounts``: table, :class:`.IntIndex` -- int(f_i) : int(C)
    
    Since some data types (e.g. list, tuple) are not supported in PyTables/HDF5,
    we make use of cPickle serialization. For example, sparse feature vectors
    (lists of tuples) are pickled for storage in a StringCol.
    """
        

    def __init__(self, papers, features=None, index_by='wosid',
                       index_citation_by='ayjid', exclude=set([]),
                       filt=None, datapath=None, index=True):
        """
        
        Parameters
        ----------
        papers : list
            A list of :class:`.Paper`
        features : dict
            Contains dictionary `{ type: { i: [ (f, w) ] } }` where `i` is an 
            index for papers (see kwarg `index_by`), `f` is a feature (e.g. an 
            N-gram), and `w` is a weight on that feature (e.g. a count).
        index_by : str
            A key in :class:`.Paper` for indexing. If `features` is provided, 
            then this must by the field from which indices `i` are drawn. For 
            example, if a dictionary in `features` describes DfR wordcounts for
            the :class:`.Paper`\s in `data`, and is indexed by DOI, then 
            `index_by` should be 'doi'.
        index_citations_by : str
            Just as ``index_by``, except for citations.
        exclude : set
            (optional) Features to ignore, e.g. stopwords.
        datapath : str
            (optional) Target path for HDF5 repository. If not provided, will
            generate a temporary directory in ``/tmp`` (or equivalent). The full
            path to the HDF5 repo can be found in the ``path`` attribute after
            initialization.
        index : bool
            (default: True) If True, runs :func:`.index`\.
        """
        
        logger.debug('Initialize HDF5DataCollection with {0} papers'
                                                           .format(len(papers)))

        # Where to save the HDF5 data file?
        if datapath is None:
            self.datapath = tempfile.mkdtemp()
            logger.debug('Generated datapath {0}.'.format(self.datapath))
        else:
            self.datapath = datapath
            
        self.uuid = uuid.uuid4()    # Unique identifier for this DataCollection.
        logger.debug('Datapath has UUID {0}.'.format(self.uuid))

        self.path = '{0}/DataCollection-{1}.h5'.format(self.datapath, self.uuid)
        self.h5file = tables.openFile(self.path, mode = "w",
                                   title='DataCollection-{0}'.format(self.uuid))
        self.group = self.h5file.createGroup("/", 'arrays')
        
        logger.debug('Initialize features...')
        self.features = HDF5Features(self.h5file)
        logger.debug('Initialize authors...')
        self.authors = vlarray_dict(self.h5file, self.group, 
                                    'authors', tables.StringAtom(100))

        # { str(f) : feature }
        logger.debug('Initialize citations...')
        self.citations = papers_table(self.h5file, index_citation_by,
                                                   'citations')

        logger.debug('Initialize papers...')
        self.papers = papers_table(self.h5file, index_by, 'papers', 
                                        citations=self.citations,
                                        index_citation_by=index_citation_by)

        # { str(f) : [ str(p) ] }
        logger.debug('Initialize papers_citing...')        
        self.papers_citing = vlarray_dict(self.h5file, self.group,
                                        'papers_citing', tables.StringAtom(100))
        
        self.axes = HDF5Axes(self.h5file)
        self.index_by = index_by    # Field in Paper, e.g. 'wosid', 'doi'.
        self.index_citation_by = index_citation_by        
        
        if index:
            logger.debug('Index DataCollection...')
            self.index(papers, features, index_by, index_citation_by,
                                                   exclude, filt)
    
        logger.debug('HDF5DataCollection initialized, flushing to force save.')
        self.h5file.flush()
        
    def abstract_to_features(self, remove_stopwords=True):
        """
        See :func:`.DataCollection.abstract_to_features`\.
        
        Parameters
        ----------
        remove_stopwords : bool
            (default: True) If True, passes tokenizer the NLTK stoplist.        
        """

        super(HDF5DataCollection, self).abstract_to_features(remove_stopwords)
        self.h5file.flush()
        
    def filter_features(self, fold, fnew, filt):
        """
        See :func:`.DataCollection.filter_features`\.
        
        Parameters
        ----------
        fold : str
            Key into ``features`` for existing featureset.
        fnew : str
            Key into ``features`` for resulting featuresset.
        filt : method
            Filter function to apply to the featureset. Should take a feature
            dict as its sole parameter.
        """    

        self.h5file.flush()                
        super(HDF5DataCollection, self).filter_features(fold, fnew, filt)
        self.h5file.flush()        
        
        
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
        if '/axes' not in self.h5file:
            self.group = self.h5file.createGroup('/', 'axes')
        else:
            self.group = self.h5file.getNode('/axes')

    def __setitem__(self, key, value):
        logger.debug('HDF5Axes.__setitem__ for key {0}'.format(key))

        dict.__setitem__(self, key, HDF5Axis(self.h5file, self.group, key))
        for k,v in value.iteritems():
            self[key][k] = v


class HDF5Axis(dict):
    def __init__(self, h5file, fgroup, name):
        self.h5file = h5file
        self.group = self.h5file.createGroup(fgroup, name)
        self.name = name

    def __setitem__(self, key, value):
        name = '{0}_{1}'.format(self.name, key)
        dict.__setitem__(self, key, HDF5ArrayDict(self.h5file, self.group, name, value))

class HDF5Features(dict):
    """
    Organizes feature-sets, each as a :class:`.HDF5Feature`\.
    """

    def __init__(self, h5file):
        logger.debug('Initialize HDF5Features.')

        self.h5file = h5file
        if '/features' not in self.h5file:
            self.group = self.h5file.createGroup('/', 'features')
        else:
            self.group = self.h5file.getNode('/features')
        
    def __setitem__(self, key, value):
        logger.debug('HDF5Features.___setitem__ for key {0}.'.format(key))

        dict.__setitem__(self, key, HDF5FeatureSet(self.h5file, 
                                                   self.group, key))
        
        logger.debug('assign values for key {0}.'.format(key))
        for k,v in value.iteritems():
            self[key][k] = v

            
class HDF5FeatureSet(dict):
    """
    Stores data about the distribution of a specific feature-set, e.g. unigrams,
    across papers in the :class:`.DataCollection`\.
    """

    def __init__(self, h5file, fgroup, name):
        logger.debug('Initializing HDF5Feature with name {0}.'.format(name))
        self.h5file = h5file
        self.group = self.h5file.createGroup(fgroup, name)
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
#        print key, type(dict.__getitem__(self, key))
        return dict.__getitem__(self, key)

class HDF5ArrayDict(dict):
    def __init__(self, h5file, group, name, values):
        self.h5file = h5file
        self.group = group
        self.name = name
        
        self.array = self.h5file.create_array(self.group, self.name, values)
        
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
        self.group = self.h5file.createGroup(group, 'features')

        self.documents = self.h5file.create_table(self.group, 'documents', 
                                                              Index)
        self.documents.cols.i.create_index()
        self.documents.cols.mindex.create_index()
        
        self.d = {}
    
    def __setitem__(self, key, value):
        if key not in self:
            # Index the document.
            i = len(self.documents)
            doc = self.documents.row
            doc['i'] = i
            doc['mindex'] = key
            doc.append()
            self.d[i] = key
            self.documents.flush()
        
            indices, values = zip(*value)
            I = self.h5file.create_array(self.group, 'indices{0}'.format(i), 
                                                     numpy.array(indices))
            K = self.h5file.create_array(self.group, 'values{0}'.format(i), 
                                                     numpy.array(values))
            dict.__setitem__(self, key, (I,K))
        
    def __getitem__(self, key):
        I,K = dict.__getitem__(self, key)
        return zip(I,K)
    
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