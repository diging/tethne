"""
Classes for handling bibliographic data.

.. autosummary::

   Paper
   DataCollection
   GraphCollection
   LDAModel
   
"""

# TODO: redefine ModelCollections and Models
# TODO: rename this module?

import networkx as nx
import pickle as pk
from cStringIO import StringIO
from pprint import pprint
import sys
import numpy as np
#import scipy as sc

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

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
       
       
    Parameters
    ----------
    papers : list
        A list of :class:`.Paper`
    features : dict
        Contains dictionary `{ type: { i: [ (f, w) ] } }` where `i` is an index
        for papers (see kwarg `index_by`), `f` is a feature (e.g. an N-gram), 
        and `w` is a weight on that feature (e.g. a count).
    index_by : str
        A key in :class:`.Paper` for indexing. If `features` is provided, then
        this must by the field from which indices `i` are drawn. For example, if
        a dictionary in `features` describes DfR wordcounts for the 
        :class:`.Paper`\s in `data`, and is indexed by DOI, then `index_by`
        should be 'doi'.
    exclude_features : set
        (optional) Features to ignore, e.g. stopwords.
        
    Returns
    -------
    :class:`.DataCollection`
    """
    
    def __init__(self, papers, features=None, index_by='wosid',
                                              index_citation_by='ayjid',
                                              exclude_features=set([])):
        self.axes = {}
        self.index_by = index_by    # Field in Paper, e.g. 'wosid', 'doi'.
        self.index_citation_by = index_citation_by
        
        # Check if data is a list of Papers.
        if type(papers) is not list or type(papers[0]) is not Paper:
            raise(ValueError("papers must be a list of Paper objects."))
        
        # Check if index_by is a valid key.
        self.datakeys = papers[0].keys()
        if index_by not in self.datakeys:
            raise(KeyError(str(index_by) + " not a valid key in data."))
        
        # Index the Papers in data.
        self.papers = { p[index_by]:p for p in papers }
        self.N_p = len(self.papers)
        
        # Index the Papers by author.
        self._index_papers_by_author()

        # Tokenize and index citations (both directions).
        self._index_citations()
        
        # Tokenize and index features.
        if features is not None:
            self._tokenize_features(features, exclude_features=exclude_features)
        else:
            logger.debug('features is None, skipping tokenization.')
            self.features = None

    def _index_papers_by_author(self):
        """
        Generates dict `{ author : [ p ] }` where `p` is an index of a
        :class:`.Paper` .
        """
        
        logger.debug('indexing authors in {0} papers'.format(self.N_p))
        self.authors = {}
        
        for k,p in self.papers.iteritems():
            for author in p.authors():
                if author in self.authors:
                    self.authors[author].append(k)
                else:
                    self.authors[author] = [k]
    
        self.N_a = len(self.authors)
        logger.debug('indexed {0} authors'.format(self.N_a))
    
    def _index_citations(self):
        """
        Generates dict `{ c : citation }` and `{ c : [ p ] }`.
        """
        
        logger.debug('indexing citations in {0} papers'.format(self.N_p))
        
        self.citations = {}         # { c : citation }
        self.papers_citing = {}     # { c : [ p ] }

        for k,p in self.papers.iteritems():
            try:
                for citation in p['citations']:
                    c = citation[self.index_citation_by]

                    if c not in self.citations:
                        self.citations[c] = citation
                    
                    if c not in self.papers_citing:
                        self.papers_citing[c] = [ k ]
                    else:
                        self.papers_citing[c].append(k)
            except TypeError:    # May not have any citations (None).
                pass

        self.N_c = len(self.citations)
        logger.debug('indexed {0} citations'.format(self.N_c))
        
    def _tokenize_features(self, features, exclude_features=set([])):
        """
        
        Parameters
        ----------
        features : dict
            Contains dictionary `{ type: { i: [ (f, w) ] } }` where `i` is an index
            for papers (see kwarg `index_by`), `f` is a feature (e.g. an N-gram), 
            and `w` is a weight on that feature (e.g. a count).
        exclude_features : set
            (optional) Features to ignore, e.g. stopwords.
        """
        logger.debug('tokenizing {0} sets of features'.format(len(features)))
        
        self.features = {}
        
        for ftype, fdict in features.iteritems():   # e.g. unigrams, bigrams
            logger.debug('tokenizing features of type {0}'.format(ftype))

            self.features[ftype] = { 'features': {},
                                     'index': {} }
            
            # List of unique tokens.
            ftokenset = set([f for fval in fdict.values() for f,v in fval])
            ftokens = list(ftokenset - exclude_features)     # e.g. stopwords.
            logger.debug('found {0} unique tokens'.format(len(ftokens)))

            # Create forward and reverse indices.
            findex = { i:ftokens[i] for i in xrange(len(ftokens)) }
            findex_ = { v:k for k,v in findex.iteritems() }     # lookup.
            
            # Tokenize.
            for key, fval in fdict.iteritems(): # fval is a list of tuples.
                if type(fval) is not list or type(fval[0]) is not tuple:
                    raise ValueError('Malformed features data.')

                tokenized = [ (findex_[f],w) for f,w in fval if f in findex_ ]
                self.features[ftype]['features'][key] = tokenized
            
            self.features[ftype]['index'] = findex  # Persist.
            
        logger.debug('done indexing features')
        
        
    def abstract_to_features(self):
        """
        Generates a set of unigram features from the abstracts of Papers.
        """
    
        # TODO: implement this.
        pass
    
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
            
        # TODO: consider removing this, and just focusing on time.
        elif key == 'author':   # Already indexed.
            self.axes[key] = self.authors     # { a : [ p ] }

        # TODO: consider indexing journals in __init__, perhaps optionally.
        elif key in self.datakeys: # e.g. 'jtitle'
            self.axes[key] = {}     # { jtitle : [ p ] }
            for p,paper in self.papers.iteritems():
                try:
                    self.axes[key][paper[key]].append(p)
                except KeyError:
                    self.axes[key][paper[key]] = [p]
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

        # Get parameters from kwargs.
        window_size = kwargs.get('window_size', 1)
        step_size = kwargs.get('step_size', 1)
        start = kwargs.get('start', min([ paper['date']
                                           for paper in self.papers.values() ]))
        end = kwargs.get('start', max([ paper['date']
                                           for paper in self.papers.values() ]))
        cumulative = kwargs.get('cumulative', False)


        slices = {}     # { s : [ p ] }
        last = None
        for s in xrange(start, end-window_size+2, step_size):
            slices[s] = [ p for p,paper in self.papers.iteritems()
                            if s <= paper['date'] < s + window_size ]
            if cumulative and last is not None:
                slices[s] += last
            last = slices[s]
        return slices
        
    def indices(self):
        """
        Yields a list of indices of all papers in this :class:`.DataCollection`
        
        Returns
        -------
        list
            List of indices.
        """
        
        return self.papers.keys()
    
    def papers(self):
        """
        Yield the complete set of :class:`.Paper` instances in this
        :class:`.DataCollection` .
        
        Returns
        -------
        papers : list
            A list of :class:`.Paper`
        """
        
        return self.papers.values()
    
    def get_slices(self, key, include_papers=False):
        """
        Yields slices { k : [ p ] } for key.
        
        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.DataCollection` .
        include_papers : bool
            If True, retrives :class:`.Paper` objects, rather than just indices.
        
        Returns
        -------
        slices : dict
            Keys are slice indices. If `include_papers` is `True`, values are 
            lists of :class:`.Paper` instances; otherwise returns paper indices 
            (e.g. 'wosid' or 'doi').

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

        if include_papers:  # Retrieve Papers.
            return { k:[ self.papers[p] for p in v ] for k,v in slices.iteritems() }
        return slices

    def get_slice(self, key, index, include_papers=False):
        """
        Yields a specific slice.
        
        Parameters
        ----------
        key : str
            Key from :class:`.Paper` that has previously been used to slice data
            in this :class:`.DataCollection` .
        index : str or int
            Slice index for key (e.g. 1999 for 'date').
        include_papers : bool
            If True, retrives :class:`.Paper` objects, rather than just indices.
        
        Returns
        -------
        slice : list
            List of paper indices in this :class:`.DataCollection` , or (if
            `include_papers` is `True`) a list of :class:`.Paper` instances.

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
        
        if include_papers:
            return [ self.papers[p] for p in slice ]
        return slice
    
    def get_by(self, key_indices, include_papers=False):
        """
        Given a set of (key, index) tuples, return the corresponding subset of
        :class:`.Paper` indices (or :class:`.Paper` instances themselves, if 
        papers is True).
        
        Parameters
        ----------
        key_indices : list
            A list of (key, index) tuples.
        include_papers : bool
            If True, retrives :class:`.Paper` objects, rather than just indices.
        
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
            return [ self.papers[s] for s in plist ]
        return plist
    
    def _get_slice_i(self, key, i):
        return self.axes[key].values()[i]
        
    def _get_by_i(self, key_indices):
        slices = []
        for k, i in key_indices:
            slice = set(self._get_slice_i(k, i))
            slices.append(slice)
        
        return list( set.intersection(*slices) )
    
    def _get_slice_keys(self, slice):
        if slice in self.get_axes():
            return self.axes[slice].keys()
    
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
        I = []
        J = []
        K = []
        for i in xrange(x_size):
            if y_axis is None:
                k = len(self._get_by_i([(x_axis, i)]))
                if k > 0:
                    I.append(i)
                    J.append(0)
                    K.append(k)
            else:
                for j in xrange(y_size):
                    k = len(self._get_by_i([(x_axis, i),(y_axis, j)]))
                    if k > 0:
                        I.append(i)
                        J.append(j)
                        K.append(k)

        # TODO: Move away from SciPy, to facilitate PyPy compatibility.
        #dist = sc.sparse.coo_matrix((K, (I,J)), shape=shape)
        #return dist

    def distribution_2d(self, x_axis, y_axis=None):
        """
        Deprecated as of 0.4.3-alpha. Use :func:`.distribution` instead.
        """

        return distribution(self, x_axis, y_axis=y_axis)

    def plot_distribution(self, x_axis=None, y_axis=None, type='bar', fig=None, 
                                                                      **kwargs):
        """
        Plot distribution along slice axes, using MatPlotLib.
        
        Parameters
        ----------
        x_axis : str
        y_axis : str
            (optional)
        type : str
            'plot' or 'bar'
        **kwargs
            Passed to PyPlot method.
        """
        
        import matplotlib.pyplot as plt
        
        if fig is None:
            fig = plt.figure()
        
        if x_axis is None:
            x_axis = self.get_axes()[0]

        xkeys = self._get_slice_keys(x_axis)        
        
        if y_axis is None:
            plt.__dict__[type](xkeys, self.distribution(x_axis).todense(), **kwargs)
            plt.xlim(min(xkeys), max(xkeys))
        else:
            ykeys = self._get_slice_keys(y_axis)    
            ax = fig.add_subplot(111)
            ax.imshow(self.distribution(x_axis, y_axis).todense(), **kwargs)
            ax.set_aspect(0.5)
            plt.yticks(np.arange(len(xkeys)), xkeys)
            plt.xticks(np.arange(len(ykeys)), ykeys)            

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
        
        self.node_index = {}
        self.node_lookup = {}       # Reverse index.

        return

    def __setitem__(self, index, graph, metadata=None):
        """
        Add a :class:`.Graph` to the :class:`.GraphCollection`

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

        self._index_graph(index, graph)

        # TODO: do we need this?
        self.metadata[index] = metadata
        
    def _index_graph(self, index, graph):
        """
        Effectively labels nodes with integer indices used across all graphs.
        """

        graph_ = nx.Graph()
        
        # Index nodes, and add to new graph.
        for node in graph.nodes(data=True):
            if node[0] in self.node_lookup:
                n = self.node_lookup[node[0]]
            else:
                try:
                    n = max(self.node_index.keys()) + 1    # Get an unused key.
                except ValueError:  # node_index is empty.
                    n = 0
                self.node_index[n] = node[0]
                self.node_lookup[node[0]] = n
            
            node[1]['label'] = node[0]  # Keep label.
            graph_.add_node(n, node[1]) # Include node attributes.
        
        for edge in graph.edges(data=True):
            n_i = self.node_lookup[edge[0]] # Already indexed all nodes.
            n_j = self.node_lookup[edge[1]]
        
            graph_.add_edge(n_i, n_j, edge[2])  # Include edge attributes.

        self.graphs[index] = graph_

    def __getitem__(self, key):
        return self.graphs[key]

    def __delitem__(self, key):
        del self.graphs[key]

    def __len__(self):
        return len(self.graphs)

    def nodes(self):
        """
        Return complete set of nodes for this :class:`.GraphCollection` .

        Returns
        -------
        nodes : list
            Complete list of unique node indices for this
            :class:`.GraphCollection` .
        """
        
        return self.node_index.keys()

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
        
        # TODO: is there a way to simplify this?

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

class ModelCollection(object):
    """
    A collection of models.
    
    """

    def __init__(self):
        self.models = {}
        self.metadata = {}
        

    def __setitem__(self, index, model, metadata=None):
        """
        """

        self.models[index] = model
        self.metadata[index] = metadata

    def __getitem__(self, key):
        return self.models[key]

    def __delitem__(self, key):
        del self.models[key]

    def __len__(self):
        return len(self.models)        
