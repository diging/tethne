import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

import numpy
import tables
from ...classes import Paper, Corpus
import tempfile
import uuid
import cPickle as pickle
import urllib
from unidecode import unidecode

from util import *

class HDF5Corpus(Corpus):
    """
    Provides HDF5 persistence for :class:`.Corpus`\.
    
    The :class:`.HDF5Corpus` uses a variety of tables and arrays to
    store data. The structure of a typical HDF5 repository for an instance
    of this class is:
    
    # TODO: update this.
    
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
        
        logger.debug('Initialize HDF5Corpus with {0} papers'
                                                           .format(len(papers)))

        # Where to save the HDF5 data file?
        if datapath is None:
            self.datapath = tempfile.mkdtemp()
            logger.debug('Generated datapath {0}.'.format(self.datapath))
        else:
            self.datapath = datapath
        
        # Load or create HDF5 repository.
        if self.datapath.split('.')[-1] == 'h5':
            self.path = self.datapath
            title = ''
        else:   # New h5 file.
            self.uuid = uuid.uuid4()    # Unique identifier for this Corpus.
            logger.debug('Datapath has UUID {0}.'.format(self.uuid))
            self.path = '{0}/Corpus-{1}.h5'.format( self.datapath,
                                                            self.uuid   )
            title = 'Corpus-{0}'.format(self.uuid)

        # mode = 'a' will create a new file if no file exists.
        self.h5file = tables.openFile(self.path, mode = 'a', title=title)
                                   
        # Load or create arrays group.
        if '/arrays' not in self.h5file:
            self.group = self.h5file.createGroup("/", 'arrays')
        else:
            self.group = self.h5file.getNode('/arrays')
        
        logger.debug('Initialize features...')
        self.features = HDF5Features(self.h5file)
        logger.debug('Initialize authors...')
        self.authors = vlarray_dict(self.h5file, self.group, 
                                    'authors', tables.StringAtom(100),
                                               tables.StringAtom(100))

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
                                        'papers_citing',
                                        tables.StringAtom(100),
                                        tables.StringAtom(100))
        
        self.axes = HDF5Axes(self.h5file)
        self.index_by = index_by    # Field in Paper, e.g. 'wosid', 'doi'.
        self.index_citation_by = index_citation_by        
        
        if index:
            logger.debug('Index Corpus...')
            self.index(papers, features, index_by, index_citation_by,
                                                   exclude, filt)
    
        logger.debug('HDF5Corpus initialized, flushing to force save.')
        self.h5file.flush()
        
    def abstract_to_features(self, remove_stopwords=True):
        """
        See :func:`.Corpus.abstract_to_features`\.
        
        Parameters
        ----------
        remove_stopwords : bool
            (default: True) If True, passes tokenizer the NLTK stoplist.        
        """

        super(HDF5Corpus, self).abstract_to_features(remove_stopwords)
        self.h5file.flush()
        
    def filter_features(self, fold, fnew, filt):
        """
        See :func:`.Corpus.filter_features`\.
        
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
        super(HDF5Corpus, self).filter_features(fold, fnew, filt)
        self.h5file.flush()

def to_hdf5(obj, datapath=None):
    """
    Transforms a :class:`.Corpus` into a :class:`.HDF5Corpus`\.
    
    Use this method to store your :class:`.Corpus`\, e.g. to archive data
    associated with your study or project.
    
    Parameters
    ----------
    datapath : str
        If provided, will create the new :class:`.HDF5Corpus` at
        that location.
    
    Returns
    -------
    HD : :class:`.HDF5Corpus`
    
    Examples
    --------
    
    .. code-block:: python
    
       >>> HC = C.to_hdf5(datapath='/path/to/my/archive')
       
    """

    # Initialize, but don't index.
    HD = HDF5Corpus([], index_by=obj.index_by,
                        index_citation_by=obj.index_citation_by,
                        datapath=datapath,
                        index=False )

    HD = _migrate_values(obj, HD)
    return HD

def from_hdf5(HD_or_path):
    """
    Load or transform a :class:`.HDF5Corpus` into a :class:`.Corpus`\.
    
    If `HD_or_path` is a string, will attempt to load the 
    :class:`.HDF5Corpus` from that path.
    
    Parameters
    ----------
    HD_or_path : str or :class:`.HDF5Corpus`
        If str, must be a path to a :class:`.HDF5Corpus` HDF5 repo.
    
    Returns
    -------
    D : :class:`.Corpus`
    
    Examples
    --------

    .. code-block:: python
    
       >>> C = from_hdf5('/path/to/my/archive/MyH5Corpus.h5')
    """

    if HD_or_path is str:
        hd = HDF5Corpus([], index=False, datapath=HD_or_path)
    elif type(HD_or_path) is HDF5Corpus:
        hd = HD_or_path

    D = _migrate_values(hd, Corpus([], index=False))
    return D

def _migrate_values(fromD, toD):
    """
    Transfers properties from one :class:`.Corpus` to another.
    
    `fromD` and `toD` can by anything that behaves like a 
    :class:`.Corpus`\, including a :class:`.HDF5Corpus`\.
    
    Parameters
    ----------
    fromD : :class:`.Corpus`
        Source :class:`.Corpus`
    toD : :class:`.Corpus`
        Target :class:`.Corpus`
        
    Returns
    -------
    toD : :class:`.Corpus`
        Updated target :class:`.Corpus`
    """
    
    logger.debug('migrate values')

    # Transfer papers.
    for k,v in fromD.papers.iteritems():
        toD.papers[k] = v
    logger.debug('papers: {0}->{1}'.format(len(fromD.papers), len(toD.papers)))

    # Transfer citations.
    for k,v in fromD.citations.iteritems():
        toD.citations[k] = v
    logger.debug('citations: {0}->{1}'
                              .format(len(fromD.citations), len(toD.citations)))

    for k,v in fromD.papers_citing.iteritems():
        toD.papers_citing[k] = v
    logger.debug('papers_citing: {0}->{1}'
                      .format(len(fromD.papers_citing), len(toD.papers_citing)))

    # Transfer authors.
    for k,v in fromD.authors.iteritems():
        toD.authors[k] = v
    logger.debug('authors: {0}->{1}'
                                  .format(len(fromD.authors), len(toD.authors)))

    # Transfer features.
    for k, v in fromD.features.iteritems():
        toD._define_features(   k, v['index'], v['features'], v['counts'],
                                   v['documentCounts'], v['papers']    )
    logger.debug('features: {0}->{1}'
                                .format(len(fromD.features), len(toD.features)))

    # Transfer axes.
    for k,v in fromD.axes.iteritems():
        toD.axes[k] = v
    logger.debug('axes: {0}->{1}'.format(len(fromD.axes), len(toD.axes)))

    toD.N_a = len(fromD.authors)
    toD.N_c = len(fromD.citations)
    toD.N_p = len(fromD.papers)
    
    toD.index_by = fromD.index_by
    toD.index_citation_by = fromD.index_citation_by

    return toD


