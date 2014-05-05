"""
Classes for handling bibliographic data.

.. autosummary::

   Paper
   DataCollection
   GraphCollection
   LDAModel
   
"""

import networkx as nx
import pickle as pk
from cStringIO import StringIO
from pprint import pprint
import sys
import numpy as np
import scipy as sc

class Paper(object):
    """
    Base class for Papers. 
    
    Behaves just like a dict, but enforces a limited vocabulary of keys, and 
    specific data types.

    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    aulast          list    Authors' last name, as a list.
    auinit          list    Authors' first initial as a list.
    institution     dict    Institutions with which the authors are affiliated.
    atitle          str     Article title.
    jtitle          str     Journal title or abbreviated title.
    volume          str     Journal volume number.
    issue           str     Journal issue number.
    spage           str     Starting page of article in journal.
    epage           str     Ending page of article in journal.
    date            int     Article date of publication.
    country         dict    Author-Country mapping.
    citations       list    A list of :class:`.Paper` instances.
    ayjid           str     First author's name (last fi), pubdate, and journal.
    doi             str     Digital Object Identifier.
    pmid            str     PubMed ID.
    wosid           str     Web of Science UT fieldtag value.
    accession       str     Identifier for data conversion accession.
    ===========     =====   ====================================================

    None values are also allowed for all fields.
    """

    def __init__(self):
        """
        Defines keys, and acceptable data types for values.
        """
        self.internal = {
                            'aulast':None,
                            'auinit':None,
                            'institutions':None,
                            'atitle':None,
                            'jtitle':None,
                            'volume':None,
                            'issue':None,
                            'spage':None,
                            'epage':None,
                            'date':None,
                            'citations':None,
                            'country':None,
                            'ayjid':None,
                            'doi':None,
                            'pmid':None,
                            'wosid':None,
                            'abstract':None,
                            'accession':None,
                            'topics':None    }

        self.list_fields = [ 'aulast',
                             'auinit',
                             'citations' ]

        self.string_fields = [ 'atitle',
                               'jtitle',
                               'volume',
                               'issue',
                               'spage',
                               'epage',
                               'ayjid',
                               'doi',
                               'pmid',
                               'wosid',
                               'abstract',
                               'accession' ]

        self.int_fields = [ 'date' ]

        self.dict_fields = [ 'institutions' ]

    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys, and acceptable data types for
        values.
        """

        vt = type(value)
        ks = str(key)

        if key not in self.internal.keys():
            raise KeyError(ks + " is not a valid key in Paper.")
        elif key in self.list_fields and vt is not list and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a list.")
        elif key in self.string_fields and vt is not str and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a string.")
        elif key in self.int_fields and vt is not int and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be an integer.")
        elif key in self.dict_fields and vt is not dict and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a dictionary.")
        else:
            self.internal[key] = value

    def __getitem__(self, key):
        return self.internal[key]

    def __delitem__(self, key):
        del self.internal[key]

    def __len__(self):
        return len(self.internal)

    def keys(self):
        """Returns the keys of the :class:`.Paper`'s metadata fields."""
        return self.internal.keys()

    def values(self):
        """Returns the values of the :class:`.Paper`'s metadata fields."""
        return self.internal.values()

    def iteritems(self):
        """Returns an iterator for the :class:`.Paper`'s metadata fields"""
        return self.internal.iteritems()
    
    def authors(self):
        """Returns a list of author names (FI LAST)."""
        
        auths = []
        for i in xrange(len(self.internal['aulast'])):
            au = self.internal['auinit'][i] + ' ' +  self.internal['aulast'][i]
            auths.append( au.upper() )
        return auths

class DataCollection(object):
    """
    A :class:`.DataCollection` organizes :class:`.Paper`\s for analysis.
    
    The :class:`.DataCollection` is initialized with some data, which is indexed
    by a key in :class:`.Paper` (default is wosid). The :class:`.DataCollection`
    can then be sliced ( :func:`DataCollection.slice` ) by other keys in
    :class:`.Paper` .
    
    **Usage**
    
    .. code-block:: python

       >>> import tethne.readers as rd
       >>> data = rd.wos.read("/Path/to/wos/data.txt")
       >>> data += rd.wos.read("/Path/to/wos/data2.txt")    # Two accessions.
       >>> from tethne.data import DataCollection
       >>> D = DataCollection(data) # Indexed by wosid, by default.
       >>> D.slice('date', 'time_window', window_size=4)
       >>> D.slice('accession')
       >>> D
       <tethne.data.DataCollection at 0x10af0ef50>
        
    """
    
    def __init__(self, data, model=None, grams=None, index_by='wosid'):
        self.axes = {}
        self.index_by = index_by
        self.datakeys = data[0].keys()
        
        if type(data[0]) is not Paper:
            raise(ValueError("Data must contain tethne.data.Paper objects."))

        if index_by not in self.datakeys:
            raise(KeyError(str(index_by) + " not a valid key in data."))
        
        self.data = { p[index_by]:p for p in data }
        
        self.model = model
    
    def slice(self, key, method=None, **kwargs):
        """
        Slices data by key, using method (if applicable).

        Methods available for slicing a :class:`.DataCollection`\:

        ===========    =============================    =======    =============
        Method         Description                      Key        kwargs
        ===========    =============================    =======    =============
        time_window    Slices data using a sliding      date       window_size
                       time-window. Dataslices are                 step_size
                       indexed by the start of the 
                       time-window.
        time_period    Slices data into time periods    date       window_size
                       of equal length. Dataslices
                       are indexed by the start of
                       the time period.
        ===========    =============================    =======    =============


        The main difference between the sliding time-window (``time_window``) 
        and the time-period (``time_period``) slicing methods are whether the
        resulting periods can overlap. Whereas time-period slicing divides data
        into subsets by sequential non-overlapping time periods, subsets 
        generated by time-window slicing can overlap.

        .. figure:: _static/images/bibliocoupling/timeline.timeslice.png
           :width: 400
           :align: center
           
           **Time-period** slicing, with a window-size of 4 years.
           
        .. figure:: _static/images/bibliocoupling/timeline.timewindow.png
           :width: 400
           :align: center
           
           **Time-window** slicing, with a window-size of 4 years and a 
           step-size of 1 year.

        Avilable kwargs:

        ===========    ======   ================================================
        Argument       Type     Description
        ===========    ======   ================================================
        window_size    int      Size of time-window or period, in years
                                (default = 1).
        step_size      int      Amount to advance time-window or period in each
                                step (ignored for time_period).
        cumulative     bool     If True, the data from each successive slice 
                                includes the data from all preceding slices.
                                Only applies if key is 'date' (default = False).
        ===========    ======   ================================================ 
        
        Parameters
        ----------
        key : str
            key in :class:`.Paper` by which to slice data.
        method : str (optional)
            Dictates how data should be sliced. See table for available methods.
            If key is 'date', default method is time_period with window_size and
            step_size of 1.
        kwargs : kwargs
            See methods table, above.

        """
        
        if key == 'date':
            if method == 'time_window':
                kw = {  'window_size': kwargs.get('window_size', 1),
                        'step_size': kwargs.get('step_size', 1) }
                self.axes[key] = self._time_slice(**kw)

            elif method == 'time_period' or method is None:
                kw = {  'window_size': kwargs.get('window_size', 1),
                        'step_size': kwargs.get('window_size', 1),
                        'cumulative': kwargs.get('cumulative', False) }

                self.axes[key] = self._time_slice(**kw)
            else:
                raise(ValueError(str(method) + " not a valid slicing method."))
            
        elif key == 'author':
            self.axes[key] = {}
            for i,p in self.data.iteritems():
                for a in p.authors():
                    try:
                        self.axes[key][a].append(i)
                    except KeyError:
                        self.axes[key][a] = [i]
        elif key in self.datakeys: # e.g. 'jtitle'
            self.axes[key] = {}
            for i,p in self.data.iteritems():
                try:
                    self.axes[key][p[key]].append(i)
                except KeyError:
                    self.axes[key][p[key]] = [i]
        else:
            raise(KeyError(str(key) + " not a valid key in data."))
        
    def _time_slice(self, **kwargs):
        """
        Slices data by date.

        If step_size = 1, this is a sliding time-window. If step_size =
        window_size, this is a time period slice.
        
        Parameters
        ----------
        kwargs : kwargs
            See table, below.
            
        Returns
        -------
        slices : dict
            Keys are start date of time slice, values are :class:`.Paper`
            indices (controlled by index_by argument in 
            :func:`.DataCollection.__init__` )
        
        Notes
        -----
        
        Avilable kwargs:

        ===========    ======   ================================================
        Argument       Type     Description
        ===========    ======   ================================================
        window_size    int      Size of time-window or period, in years
                                (default = 1).
        step_size      int      Amount to advance time-window or period in each
                                step (ignored for time_period).
        cumulative     bool     If True, the data from each successive slice 
                                includes the data from all preceding slices.
                                Only applies if key is 'date' (default = False).                                
        ===========    ======   ================================================           
        
        """

        window_size = kwargs.get('window_size', 1)
        step_size = kwargs.get('step_size', 1)
        start = kwargs.get('start', min([ p['date'] 
                                                 for p in self.data.values() ]))
        end = kwargs.get('start', max([ p['date'] 
                                                 for p in self.data.values() ]))
        cumulative = kwargs.get('cumulative', False)

        slices = {}
        last = None
        for i in xrange(start, end-window_size+2, step_size):
            slices[i] = [ k for k,p in self.data.iteritems() 
                           if i <= p['date'] < i + window_size ]
            if cumulative and last is not None:
                slices[i] += last
            last = slices[i]
        return slices
        
    def indices(self):
        """
        Yields a list of indices of all papers in this :class:`.DataCollection`
        
        Returns
        -------
        list
            List of indices.
        """
        
        return self.data.keys()
    
    def papers(self):
        """
        Yield the complete set of :class:`.Paper` instances in this
        :class:`.DataCollection` .
        
        Returns
        -------
        papers : list
            A list of :class:`.Paper`
        """
        
        return self.data.values()
    
    def get_slices(self, key, papers=False):
        """
        Yields slices for key.
        
        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.DataCollection` .
        
        Returns
        -------
        slices : dict
            Keys are slice indices. If papers is True, values are lists of
            :class:`.Paper` instances; otherwise returns paper indices (e.g.
            'wosid').

        Raises
        ------
        RuntimeError : DataCollection has not been sliced.
        KeyError : Data has not been sliced by [key] 
                    
        """

        if len(self.axes) == 0:
            raise(RuntimeError("DataCollection has not been sliced."))        
        if key not in self.axes.keys():
            raise(KeyError("Data has not been sliced by " + str(key)))
        
        slices = self.axes[key]
         
        if papers:  # Retrieve Papers.
            for k,v in slices.iteritems():
                slices[k] = [ self.data[i] for i in v ]
        
        return slices

    def get_slice(self, key, index, papers=False):
        """
        Yields a specific slice.
        
        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.DataCollection` .
        index : str or int
            Slice index for key (e.g. 1999 for 'date').
        
        Returns
        -------
        slice : list
            List of paper indices in this :class:`.DataCollection` , or (if
            papers is True) a list of :class:`.Paper` instances.

        Raises
        ------
        RuntimeError : DataCollection has not been sliced.
        KeyError : Data has not been sliced by [key] 
        KeyError : [index] not a valid index for [key]
        
        """

        if len(self.axes) == 0:
            raise(RuntimeError("DataCollection has not been sliced."))        
        if key not in self.axes.keys():
            raise(KeyError("Data has not been sliced by " + str(key)))
        if index not in self.axes[key].keys():
            raise(KeyError(str(index) + " not a valid index for " + str(key)))
        
        slice = self.axes[key][index]
        
        if papers:
            return [ self.data[s] for s in slice ]
        return slice
    
    def get_by(self, key_indices, papers=False):
        """
        Given a set of (key, index) tuples, return the corresponding subset of
        :class:`.Paper` indices (or :class:`.Paper` instances themselves, if 
        papers is True).
        
        Parameters
        ----------
        key_indices : list
            A list of (key, index) tuples.
        
        Returns
        -------
        plist : list
            A list of paper indices, or :class:`.Paper` instances.
        
        Raises
        ------
        RuntimeError : DataCollection has not been sliced.

        """

        if len(self.axes) == 0:
            raise(RuntimeError("DataCollection has not been sliced."))
        
        slices = []
        for k,i in key_indices:
            slice = set(self.get_slice(k,i))
            slices.append(slice)

        plist = list( set.intersection(*slices) )
        
        if papers:
            return [ self.data[s] for s in plist ]
        return plist
    
    def _get_slice_i(self, key, i):
        return self.axes[key].values()[i]
        
    def _get_by_i(self, key_indices):
        slices = []
        for k, i in key_indices:
            slice = set(self._get_slice_i(k, i))
            slices.append(slice)
        
        return list( set.intersection(*slices) )
    
    def get_axes(self):
        """
        Returns a list of all slice axes for this :class:`.DataCollection` .
        """
        
        return self.axes.keys()
    
    def N_axes(self):
        """
        Returns the number of slice axes for this :class:`.DataCollection` .
        """
        
        return len(self.axes.keys())
    
#    def distribution(self):
#        """
#        Returns a Numpy array describing the number of :class:`.Paper`
#        associated with each slice-coordinate.
#        
#        WARNING: expensive for a :class:`.DataCollection` with many axes or
#        long axes. Consider using :func:`.distribution_2d` .
#        
#        Returns
#        -------
#        dist : Numpy array
#            An N-dimensional array. Axes are given by 
#            :func:`DataCollection.get_axes` and values are the number of
#            :class:`.Paper` at that slice-coordinate.
#            
#        Raises
#        ------
#        RuntimeError : DataCollection has not been sliced.
#        """
#        
#        if len(self.axes) == 0:
#            raise(RuntimeError("DataCollection has not been sliced."))
#        
#        shape = tuple( len(v) for v in self.axes.values() )
#        dist = np.zeros(shape)
#        axes = self.get_axes()
#
#        for indices in np.ndindex(shape):
#            dist[indices] = len( self._get_by_i(zip(axes, indices)))
#            
#        return dist
            
    def distribution(self, x_axis, y_axis=None):
        """
        Returns a Numpy array describing the number of :class:`.Paper`
        associated with each slice-coordinate, for x and y axes spcified.

        Returns
        -------
        dist : Numpy array
            A 2-dimensional array. Values are the number of
            :class:`.Paper` at that slice-coordinate.
            
        Raises
        ------
        RuntimeError : DataCollection has not been sliced.
        KeyError: Invalid slice axes for this DataCollection.
        """
        
        if len(self.axes) == 0:
            raise(RuntimeError("DataCollection has not been sliced."))
        if x_axis not in self.get_axes():
            raise(KeyError("X axis invalid for this DataCollection."))
        
        x_size = len(self.axes[x_axis])
        
        if y_axis is not None:
            if y_axis not in self.get_axes():
                raise(KeyError("Y axis invalid for this DataCollection."))     

            y_size = len(self.axes[y_axis])
        else:   # Only 1 slice axis.
            y_size = 1

        shape = (x_size, y_size)
        dist = sc.sparse.coo_matrix(shape)
        
        for i in xrange(x_size):
            if y_axis is None:
                dist[i, 0] = len(self._get_by_i([(x_axis, i)])
            else:
                for j in xrange(y_size):
                    dist[i, j] = len(self._get_by_i([(x_axis, i),(y_axis, j)]))
        
        return dist

    def distribution_2d(self, x_axis, y_axis=None):
        """
        Deprecated as of 0.4.3-alpha. Use :func:`.distribution` instead.
        """

        return distribution(self, x_axis, y_axis=y_axis):

class GraphCollection(object):
    """
    Collection of NetworkX :class:`nx.classes.graph.Graph` objects, 
    organized by some index (e.g. time). 
    
    A :class:`.GraphCollection` can be generated using classes in the
    :mod:`tethne.builders` module. See 
    :ref:`generate-graphcollection` for details.
    
    """

    def __init__(self):
        self.graphs = {}
        self.metadata = {}
        self.edge_list = []
        self.node_list = []

        return

    def __setitem__(self, index, graph, metadata=None):
        """
        The value param can be either a Graph, or a (Graph, metadata) tuple.
        Metadata can be anything, but is probably most profitably a dictionary.

        Parameters
        ----------
        index
            This can be anything used to refer to the graph.
        graph : :class:`.nx.classes.graph.Graph`

        Raises
        ------
        ValueError : Graph must be of type networkx.classes.graph.Graph
            If value is not a Graph.
        """

        if type(graph) is not nx.classes.graph.Graph:
            raise(ValueError("Graph must be type networkx.classes.graph.Graph"))

        self.graphs[index] = graph
        self.metadata[index] = metadata

    def __getitem__(self, key):
        return self.graphs[key]

    def __delitem__(self, key):
        del self.graphs[key]

    def __len__(self):
        return len(self.graphs)

    def nodes(self, overwrite=False):
        """
        Return complete set of nodes for this :class:`.GraphCollection` . 

        If this method has been called previously for this
        :class:`.GraphCollection` then will not recompute unless overwrite =
        True.

        Parameters
        ----------
        overwrite : bool
            If True, will generate new node list, even if one already exists.

        Returns
        -------
        nodes : list
            List (complete set) of node identifiers for this
            :class:`.GraphCollection` .
        """

        if len(self.node_list) == 0 or overwrite:
            nodes = set([])
            for G in self.graphs.values():
                nodes = nodes | set(G.nodes())
            self.node_list = list(nodes)
        return self.node_list

    def edges(self, overwrite=False):   # [#61512528]
        """
        Return complete set of edges for this :class:`.GraphCollection` . 

        If this method has been called previously for this
        :class:`.GraphCollection` then will not recompute unless overwrite =
        True.

        Parameters
        ----------
        overwrite : bool
            If True, will generate new node list, even if one already exists.

        Returns
        -------
        edges : list
            List (complete set) of edges for this :class:`.GraphCollection` .
        """

        if len(self.edge_list) == 0 or overwrite :
            edges = set([])
            for G in self.graphs.values():
                edges = edges | set(G.edges())
            self.edge_list = list(edges)
        return self.edge_list

    def save(self,filepath):   #[61512528]
        """
        Pickles (serializes) the :class:`.GraphCollection` .
        
        Parameters
        ----------
        filepath :
            Full path of output file.

        Raises
        -------
        PicklingError : Raised when unpicklable objects are Pickled.
        IOError : File does not exist, or cannot be opened.
        """


        # Try block if the filename is present or not.
        try:
            with open(filepath,'wb') as output:
                try:
                    pk.dump(self, output)
                except PicklingError:     # Handle the Prickling error.
                    raise PicklingError \
                            ("Pickling error: The object cannot be pickled")
        except IOError: # File does not exist, or couldn't be read.
            raise IOError("File does not exist, or cannot be opened.")


    def load(self, filepath):    #[61512528]
        """
        Loads a pickled (serialized) :class:`.GraphCollection` from filepath.

        Parameters
        ----------
        filepath : string
            Full path to pickled :class:`.GraphCollection` .

        Raises
        -------
        UnpicklingError : Raised when there is some issue in unpickling.
        IOError : File does not exist, or cannot be read.
        """

         # Handle NameError File not found.
        try:
            with open(filepath,'rb') as input: #reading in binary mode
                try:
                     obj_read = pk.load(input)
                except UnpicklingError:  # Handle unprickling error.
                    raise UnpicklingError \
                        ("UnPickling error: The object cannot be found")


        except IOError: # File does not exist, or couldn't be read.
            raise IOError("File does not exist, or cannot be read.")
        
        # Preserving the object with unpickled data
        if(obj_read):
            self.__dict__ = obj_read.__dict__

        return obj_read
        
    def compose(self):
        """
        Returns the simple union of all :class:`.Graph` in the 
        :class:`.GraphCollection` .
        
        Returns
        -------
        composed : :class:`.Graph`
            Simple union of all :class:`.Graph` in the 
            :class:`.GraphCollection` .
            
        Notes
        -----
        
        Node or edge attributes that vary over slices should be ignored.
        
        """
        
        composed = nx.Graph()
        for k, G in self.graphs.iteritems():
            composed = nx.compose(composed, G)
        
        return composed

class BaseModel(object):
    """
    Base class for corpus models.
    
    """
    pass

class LDAModel(BaseModel):
    """
    Organizes parsed output from MALLET's LDA modeling algorithm.
    
    Used by :mod:`.readers.mallet`\.
    """
    
    def __init__(self, doc_topic, top_word, top_keys, metadata, vocabulary):
        """
        Initialize the :class:`.LDAModel`\.
        
        Parameters
        ----------
        doc_top : Numpy matrix
            Rows are documents, columns are topics. Values indicate the 
            contribution of a topic to a document, such that all rows sum to 
            1.0.
        top_word : Numpy matrix
            Rows are topics, columns are words. Values indicate the normalized
            contribution of each word to a topic, such that rows sum to 1.0.
        top_keys : dict
            Maps matrix indices for topics onto the top words in that topic.
        metadata : dict
            Maps matrix indices for documents onto a :class:`.Paper` key.
        """
        
        self.doc_topic = doc_topic
        self.top_word = top_word
        self.top_keys = top_keys
        self.metadata = metadata
        self.vocabulary = vocabulary
        
        self.lookup = { v:k for k,v in metadata.iteritems() }
        
    def topics_in_doc(self, d, topZ=None):
        """
        Returns a list of the topZ most prominent topics in a document.
        
        Parameters
        ----------
        d : str or int
            An identifier from a :class:`.Paper` key.
        topZ : int or float
            Number of prominent topics to return (int), or threshold (float).
            
        Returns
        -------
        topics : list
            List of (topic, proportion) tuples.
        """
        
        index = self.lookup[d]
        td = self.doc_topic[index, :]
        
        if topZ is None:
            topZ = td.shape[0]
            
        if type(topZ) is int:   # Return a set number of topics.
            top_indices = np.argsort(td)[0:topZ]
        elif type(topZ) is float:   # Return topics above a threshold.
            top_indices = [ z for z in np.argsort(td) if td[z] > topZ ]

        top_values = [ td[z] for z in top_indices ]
        
        topics = zip(top_indices, top_values)
        
        return topics
        
    def docs_in_topic(self, z, topD=None):
        """
        Returns a list of the topD documents most representative of topic z.
        
        Parameters
        ----------
        z : int
            A topic index.
        topD : int or float
            Number of prominent topics to return (int), or threshold (float).
            
        Returns
        -------
        documents : list
            List of (document, proportion) tuples.
        """    
        td = self.doc_topic[:, z]
        
        if topD is None:
            topD = td.shape[0]
        
        if type(topD) is int:   # Return a set number of documents.
            top_indices = np.argsort(td)[topD]
        elif type(topD) is float:   # Return documents above a threshold.
            top_indices = [ d for d in np.argsort(td) if td[d] > topD ]
        
        top_values = [ td[d] for d in top_indices ]
        top_idents = [ self.metadata[d] for d in top_indices ]
        
        documents = zip(top_idents, top_values)
        
        return documents
