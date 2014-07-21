"""
A :class:`.GraphCollection` is a set of graphs generated from a 
:class:`.Corpus` or model.
"""

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

import networkx
import numpy as np
import matplotlib.pyplot as plt

import warnings

from .. import networks as nt

class GraphCollection(object):
    """
    A :class:`.GraphCollection` is an indexed set of :class:`networkx.Graph`
    objects generated from a :class:`.Corpus` or model.

    A :class:`.GraphCollection` can be instantiated without any data.
    
    .. code-block:: python
    
       >>> from tethne import GraphCollection
       >>> G = GraphCollection()
    
    When you add a :class:`networkx.Graph` to the :class:`.GraphCollection`\, 
    all of the nodes are indexed and the graph is recast using integer IDs. 
    This means that node IDs are consistent among all of the graphs in the 
    collection.
    
    .. code-block:: python
    
       >>> import networkx
       >>> g = networkx.Graph()
       >>> g.add_edge('Bob', 'Joe')
       >>> g.add_edge('Bob', 'Jane')

       >>> from tethne import GraphCollection
       >>> G = GraphCollection()
       >>> G[1950] = g
       
       >>> print G[1950].nodes(data=True)
       [(0, {'label': 'Jane'}), (1, {'label': 'Bob'}), (2, {'label': 'Joe'})]
       
    Note that the original node names have been retained in the `label`
    attribute.
    
    You can also generate a :class:`.GraphCollection` directly from a 
    :class:`.Corpus` using the :func:`GraphCollection.build` method.
    """

    def __init__(self):
        self.graphs = {}
        self.edge_list = []
        
        self.node_index = {}
        self.node_lookup = {}       # Reverse index.

        return

    def __setitem__(self, index, graph):
        """
        Add a :class:`.Graph` to the :class:`.GraphCollection`

        Parameters
        ----------
        index
            This can be anything used to refer to the graph.
        graph : :class:`.networkx.classes.graph.Graph`

        Raises
        ------
        ValueError : Graph must be of type networkx.classes.graph.Graph
            If value is not a Graph.
        """

        self._index_graph(index, graph)
        
    def _index_graph(self, index, graph):
        """
        Effectively labels nodes with integer indices used across all graphs.
        """

        graph_ = networkx.Graph()
        
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
    
    def build(self, D, axis, node_type, graph_type, method_kwargs={}, **kwargs):
        """
        Generates a graphs directly from data in a :class:`.Corpus`.
        
        The :mod:`.networks` module contains graph-building methods for
        :mod:`.authors`, :mod:`.papers`, :mod:`.features`, and :mod:`.topics`\.
        Choose a method from one of these modules by specifying the module name
        in `node_type` and the method name in `graph_type`. That method will
        be applied to each slice in the :class:`.Corpus`\, `C`, along the 
        specified `axis`.
        
        To build a coauthorship network from a :class:`.Corpus`
        (already sliced by 'date'):
        
        .. code-block:: python
        
           >>> G = GraphCollection().build(C, 'date', 'authors', 'coauthors')
           >>> G.graphs
           {1921: <networkx.classes.graph.Graph at 0x10b2692d0>,
            1926: <networkx.classes.graph.Graph at 0x10b269c50>,
            1931: <networkx.classes.graph.Graph at 0x10b269c10>,
            1936: <networkx.classes.graph.Graph at 0x10b2695d0>,
            1941: <networkx.classes.graph.Graph at 0x10b269dd0>,
            1946: <networkx.classes.graph.Graph at 0x10a88bb90>,
            1951: <networkx.classes.graph.Graph at 0x10a88b0d0>,
            1956: <networkx.classes.graph.Graph at 0x10b269a50>,
            1961: <networkx.classes.graph.Graph at 0x10b269b50>,
            1966: <networkx.classes.graph.Graph at 0x10b269790>,
            1971: <networkx.classes.graph.Graph at 0x10b269d50>,
            1976: <networkx.classes.graph.Graph at 0x10a88bed0>}

        Parameters
        ----------
        D : :class:`.Corpus`
            Must already be sliced by `axis`.
        axis : str
            Name of slice axis to use in generating graphs.
        node_type : str
            Name of a graph-building module in :mod:`.networks`\.
        graph_type : str
            Name of a method in the module indicated by `node_type`.
        method_kwargs : dict
            Kwargs to pass to `graph_type` method.
        
        Returns
        -------
        self : :class:`.GraphCollection`
        """
        method = nt.__dict__[node_type].__dict__[graph_type]
        for key, data in D.get_slices('date', papers=True).iteritems():
            # Include sliced fields as node attributes.
            method_kwargs['node_attribs'] = D.get_axes()
            method_kwargs['node_id'] = D.index_by
            self[key] = method(data, **method_kwargs)

        return self

    def nodes(self):
        """
        Get the complete set of nodes for this :class:`.GraphCollection`\.
        
        .. code-block:: python
        
           >>> G.nodes()
           [0,
            1,
            2,
            3,
            4,
            .
            .
            233]

        Returns
        -------
        nodes : list
            Complete list of unique node indices for this
            :class:`.GraphCollection` .
        """
        
        return self.node_index.keys()

    def edges(self, overwrite=False):   # [#61512528]
        """
        Get the complete set of edges for this :class:`.GraphCollection` .

        .. code-block:: python
        
           >>> G.edges()
           [(131, 143),
            (183, 222),
            (54, 55),
            (64, 51),
            (54, 58),
            .
            .
            (53, 56)]
            
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
        
    def _plot(self, data, ylabel, type='bar', fig=None, plotargs={}, **kwargs):
        """
        
        Parameters
        ----------
        data : tuple
            ( xvalues, yvalues )
        type : str
            'plot' or 'bar'
        fig : :class:`matplotlib.figure.figure`
            If provided, will use this as the basis for the plot. Otherwise,
            will generate a new :class:`matplotlib.figure.Figure`\.
        plotargs
            Passed to PyPlot method.
            
        Returns
        -------
        fig : :class:`matplotlib.figure.Figure`
        """

        xvalues, yvalues = data

        if fig is None:
            fig = plt.figure(figsize=(10,5))

        plt.__dict__[type](xvalues, yvalues, **plotargs)
        plt.xlim(np.min(xvalues), np.max(xvalues))
        plt.ylabel(ylabel)
        
        return fig
        
    def node_distribution(self):
        """
        Get the number of nodes for each :class:`networkx.Graph` in the
        :class:`.GraphCollection`\.
        
        .. code-block:: python
        
           >>> keys, nodes = G.node_distribution()
           >>> print keys
           [1921, 1926, 1931, 1936, 1941, 1946, 1951, 1956, 1961, 1966, 1971, 1976]
           >>> print nodes
           [0, 2, 16, 8, 2, 5, 14, 16, 33, 60, 44, 52]

        Returns
        -------
        keys : list
            Graph indices.
        values  : list
            Number of nodes in each graph.
        """

        keys = sorted(self.graphs.keys())
        values = [ len(self[k].nodes()) for k in keys ]

        return keys, values
    
    def plot_node_distribution(self, type='bar', fig=None, plotargs={},
                                                              **kwargs):
        """
        Plot :func:`GraphCollection.node_distribution` using MatPlotLib.
        
        .. code-block:: python
        
           >>> fig = G.plot_node_distribution()
           
        ...should generate a plot that looks like:
        
        .. figure:: _static/images/graph_plot_distribution.png
           :width: 400
           :align: center
        
        Parameters
        ----------
        type : str
            'plot' or 'bar'
        plotargs
            Passed to PyPlot method.
            
        Returns
        -------
        fig : :class:`matplotlib.figure.figure`
        """
        
        data = self.node_distribution()
        fig = self._plot(data, 'Nodes', type, fig, plotargs, **kwargs)

        return fig
    
    def edge_distribution(self):
        """
        Get the number of edges in each :class:`networkx.Graph` in the
        :class:`.GraphCollection`\.
        
        .. code-block:: python
   
           >>> keys, edges = G.edge_distribution()
           >>> print keys
           [1921, 1926, 1931, 1936, 1941, 1946, 1951, 1956, 1961, 1966, 1971, 1976]
           >>> print edges
           [0, 1, 108, 7, 1, 4, 16, 17, 29, 42, 112, 45]
        
        Returns
        -------
        keys : list
            Graph indices.
        values  : list
            Number of nodes in each :class:`.Graph`
        """

        keys = sorted(self.graphs.keys())
        values = [ len(self[k].edges()) for k in keys ]

        return keys, values

    def plot_edge_distribution(self, type='bar', fig=None, plotargs={},
                                                              **kwargs):
        """
        Plot :func:`GraphCollection.edge_distribution` using MatPlotLib.
        
        .. code-block:: python
        
           >>> fig = G.plot_edge_distribution()
           
        ...should generate a plot that looks like:
        
        .. figure:: _static/images/graph_plot_edge_distribution.png
           :width: 400
           :align: center
        
        Parameters
        ----------
        type : str
            'plot' or 'bar'
        plotargs
            Passed to PyPlot method.
            
        Returns
        -------
        fig : :class:`matplotlib.figure.figure`
        """

        data = self.edge_distribution()
        fig = self._plot(data, 'Edges', type, fig, plotargs, **kwargs)

        return fig
    
    def attr_distribution(self, attr='weight', etype='edge', stat=np.mean):
        """
        Generate summary statistics for a node or edge attribute across all
        of the :class:`networkx.Graph`\s in the :class:`.GraphCollection`\.
        
        For example, to get the mean edge weight for each graph:
        
        .. code-block:: python
        
           >>> import numpy
           >>> keys, means = G.attr_distribution('weight', 'edge', numpy.mean)
           >>> print keys
           [1921, 1926, 1931, 1936, 1941, 1946, 1951, 1956, 1961, 1966, 1971, 1976]
           >>> print means
           [0.0, 1.0, 1.1388888888888888, 1.1428571428571428, 4.0, 1.25, 1.0, 1.0, 1.0344827586206897, 1.2142857142857142, 1.0089285714285714, 1.2]

        Parameters
        ----------
        attr : str
            Attribute name.
        etype : str
            'node' or 'edge'
        stat : method
            Method to apply to the values in each :class:`.Graph`
        
        Return
        -------
        keys : list
            Graph indices.
        values  : list
            Statistic values for each :class:`.Graph`
        """
    
        keys = sorted(self.graphs.keys())
        values = []
        for k in keys:
            A = networkx.__dict__['get_{0}_attributes'.format(etype)](self[k], attr).values()
            
            # Ignore warnings; will handle NaNs below.
            with warnings.catch_warnings():
                warnings.simplefilter('ignore')
                v = stat(A)

            if np.isnan(v):
                v = 0.
            values.append(v)

        return keys, values
        
    def plot_attr_distribution(self, attr='weight', etype='edge', stat=np.mean,
                                type='bar', fig=None, plotargs={}, **kwargs):
        """
        Plot :func:`GraphCollection.attr_distribution` using MatPlotLib.
        
        .. code-block:: python

           >>> import numpy
           >>> G.plot_attr_distribution('weight', 'edge', numpy.mean, fig=fig)
           
        ...should generate a plot that looks something like:
        
        .. figure:: _static/images/graph_plot_attr_distribution.png
           :width: 400
           :align: center
        
        Parameters
        ----------
        attr : str
            Attribute name.
        etype : str
            'node' or 'edge'
        stat : method
            Method to apply to the values in each :class:`.Graph`
        type : str
            'plot' or 'bar'
        plotargs
            Passed to PyPlot method.
            
        Returns
        -------
        fig : :class:`matplotlib.figure.figure`
        """
                                
        data = self.attr_distribution(attr, etype, stat)
        ylabel = ' '.join([stat.__name__, etype, attr])
        fig = self._plot(data, ylabel, type, fig, plotargs, **kwargs)

        return fig
    
    def save(self, filepath):   #[61512528]
        """
        Pickles (serializes) the :class:`.GraphCollection`\.
        
        .. code-block:: python
        
           >>> G.save('/path/to/archive.pickle')
        
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
        
        .. code-block:: python
        
           >>> G = GraphCollection().load('/path/to/archive.pickle')

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
        :class:`.GraphCollection`\.
        
        .. code-block:: python
        
           >>> g = G.compose()
           >>> g
           <networkx.classes.graph.Graph at 0x10bfac710>
        
        Returns
        -------
        composed : :class:`.Graph`
            Simple union of all :class:`.Graph` in the 
            :class:`.GraphCollection` .
            
        Notes
        -----
        
        Node or edge attributes that vary over slices should be ignored.
        
        """
        
        composed = networkx.Graph()
        for k, G in self.graphs.iteritems():
            composed = networkx.compose(composed, G)
        
        return composed

    def node_history(self, node, attribute, verbose=False):
        """
        Returns a dictionary of attribute values for each Graph in C for a single
        node.

        Parameters
        ----------
        C : :class:`.GraphCollection`
        node : str
            The node of interest.
        attribute : str
            The attribute of interest; e.g. 'betweenness_centrality'
        verbose : bool
            If True, prints status and debug messages.

        Returns
        -------
        history : dict
            Keys are Graph keys in C; values are attribute values for node.
        """

        history = {}

        keys = sorted(self.graphs.keys())
        for k in keys:
            G = self.graphs[k]
            asdict = { v[0]:v[1] for v in G.nodes(data=True) }
            try:
                history[k] = asdict[node][attribute]
            except KeyError:
                if verbose: print "No such node or attribute in Graph " + str(k)

        return history

    def edge_history(self, source, target, attribute, verbose=False):
        """
        Returns a dictionary of attribute vales for each Graph in C for a single
        edge.

        Parameters
        ----------
        C : :class:`.GraphCollection`
        source : str
            Identifier for source node.
        target : str
            Identifier for target node.
        attribute : str
            The attribute of interest; e.g. 'betweenness_centrality'
        verbose : bool
            If True, prints status and debug messages.

        Returns
        -------
        history : dict
            Keys are Graph keys in C; values are attribute values for edge.
        """

        history = {}

        keys = sorted(self.graphs.keys())
        for k in keys:
            G = self.graphs[k]
            try:
                attributes = G[source][target]
                try:
                    history[k] = attributes[attribute]
                except KeyError:
                    if verbose: print "No such attribute for edge in Graph " \
                                        + str(k)
            except KeyError:
                if verbose: print "No such edge in Graph " + str(k)

        return history