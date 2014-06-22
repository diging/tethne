# TODO: distribution, plot_distribution, etc

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

import networkx as nx
import numpy as np
import matplotlib.pyplot as plt

import tethne.networks as nt

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
    
    def build(self, D, axis, node_type, graph_type, method_kwargs={}, **kwargs):
        """
        Generates a graph for each slice of a :class:`.DataCollection`.
        
        Parameters
        ----------
        D : :class:`.DataCollection`
            Must already be sliced by `axis`.
        axis : str
            Name of slice axis to use in generating graphs.
        node_type : str
            'authors', 'papers', or 'institutions'
        graph_type : str
            __name__ of a method in :mod:`tethne.networks`
        method_kwargs : dict
            Kwargs to pass to `graph_type` method.
        
        Returns
        -------
        self : :class:`.GraphCollection`
        """
        method = nt.__dict__[node_type].__dict__[graph_type]
        for key, data in D.get_slices('date', include_papers=True).iteritems():
            # Include sliced fields as node attributes.
            method_kwargs['node_attribs'] = D.get_axes()
            method_kwargs['node_id'] = D.index_by
            self[key] = method(data, **method_kwargs)

        return self

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
            fig = plt.figure()

        plt.__dict__[type](xvalues, yvalues, **plotargs)
        plt.xlim(np.min(xvalues), np.max(yvalues))
        plt.ylabel(ylabel)
        
        return fig
        
    def node_distribution(self):
        """
        Returns keys and graph sizes (nodes), sorted by key.
        
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
        Plot :func:`.node_distribution` using MatPlotLib.
        
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
        Returns keys and graph sizes (edges), sorted by key.
        
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
        Plot :func:`.edge_distribution` using MatPlotLib.
        
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
        Generate summary statistics for a node or edge attribute.
        
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
            A = nx.__dict__['get_{0}_attributes'.format(etype)](self[k], attr).values()
            values.append(stat(A))

        return keys, values
        
    def plot_attr_distribution(self, attr='weight', etype='edge', stat=np.mean,
                                type='bar', fig=None, plotargs={}, **kwargs):
        """
        Plot :func:`.attr_distribution` using MatPlotLib.
        
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