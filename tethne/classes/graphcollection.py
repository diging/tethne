"""
A :class:`.GraphCollection` is a set of graphs generated from a
:class:`.Corpus` or model.
"""

import networkx as nx
from collections import defaultdict
import warnings
from tethne import networks
from tethne.utilities import _iterable

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str
    xrange = range
    str = bytes


class GraphCollection(dict):
    """
    A :class:`.GraphCollection` is an indexed set of
    :class:`.networkx.Graph`\s.

    When you add a :class:`networx.Graph`\, the nodes are indexed and
    relabeled.

    .. code-block:: python

       >>> from tethne import GraphCollection
       >>> import networkx as nx

       >>> G = GraphCollection()
       >>> g = nx.Graph()
       >>> g.add_node('A', yes='no')
       >>> g.add_edge('A', 'B', c='d')

       >>> G['graph1'] = g    # You can also use G.add('graph1', g)

       >>> G.graph1.nodes(data=True)
       [(0, {}), (1, {'yes': 'no'})]

       >>> G.node_index, G.node_lookup
       ({0: 'B', 1: 'A', -1: None}, {'A': 1, None: -1, 'B': 0})

    To build a :class:`.GraphCollection` from a :class:`.Corpus`, pass it and
    a method to the constructor, or use :meth:`.GraphCollection.build`\.

    .. code-block:: python

       >>> corpus = read(datapath)
       >>> G = GraphCollection(corpus, coauthors)

       >>> G.build(corpus, authors)

    """

    def __init__(self, corpus=None, method=None, slice_kwargs={},
                 method_kwargs={}, directed=False):
        """

        Parameters
        ----------
        corpus : :class:`.Corpus`
        method : str or func
            If str, looks for ``method`` in the ``tethne`` namespace.
        slice_kwargs : dict
            Keyword arguments to pass to ``corpus``' ``slice`` method.
        method_kwargs : dict
            Keyword arguments to pass to ``method`` along with ``corpus``.
        directed : bool
            If True, graphs will be treated as directed during indexing.
        """
        self.directed = directed
        if directed:
            self.master_graph = nx.MultiDiGraph()
        else:
            self.master_graph = nx.MultiGraph()
        self.node_index = {-1: None}
        self.node_lookup = {None: -1}
        self.graphs_containing = defaultdict(list)

        if corpus and method:
            self.build(corpus, method, slice_kwargs, method_kwargs)

    def __setitem__(self, name, graph):
        self.add(name, graph)

    def __getattr__(self, name):
        if name in self:
            return self[name]
        try:    # hasttr() causes endless recursion in Python 3.x
            return object.__getattr__(self, name)
        except AttributeError:
            pass
        raise AttributeError('GraphCollection has no such attribute or graph.')

    def build(self, corpus, method, slice_kwargs={}, method_kwargs={}):
        """
        Generate a set of :class:`networkx.Graph`\s using ``method`` on the
        slices in ``corpus``\.

        Parameters
        ----------
        corpus : :class:`.Corpus`
        method : str or func
            If str, looks for ``method`` in the ``tethne`` namespace.
        slice_kwargs : dict
            Keyword arguments to pass to ``corpus``' ``slice`` method.
        method_kwargs : dict
            Keyword arguments to pass to ``method`` along with ``corpus``.
        """
        if not hasattr(method, '__call__'):
            if not hasattr(networks, method):
                raise NameError('No such method')
            method = getattr(networks, method)
        for key, subcorpus in corpus.slice(**slice_kwargs):
            graph = method(subcorpus, **method_kwargs)
            self.add(key, graph)

    def add(self, name, graph):
        """
        Index and add a :class:`networkx.Graph` to the
        :class:`.GraphCollection`.

        Parameters
        ----------
        name : hashable
            Unique name used to identify the `graph`.
        graph : networkx.Graph

        Raises
        ------
        ValueError
            If `name` has already been used in this :class:`.GraphCollection`\.
        """
        if name in self:
            raise ValueError("{0} exists in this GraphCollection".format(name))
        elif hasattr(self, unicode(name)):
            raise ValueError("Name conflicts with an existing attribute")

        indexed_graph = self.index(name, graph)

        # Add all edges to the `master_graph`.
        for s, t, attrs in indexed_graph.edges(data=True):
            attrs.update({'graph': name})
            self.master_graph.add_edge(s, t, **attrs)

        # Add all node attributes to the `master_graph`.
        for n, attrs in indexed_graph.nodes(data=True):
            for k,v in attrs.iteritems():
                if k not in self.master_graph.node[n]:
                    self.master_graph.node[n][k] = {}
                self.master_graph.node[n][k][name] = v

        dict.__setitem__(self, name, indexed_graph)


    def index(self, name, graph):
        """
        Index any new nodes in `graph`, and relabel the nodes in `graph` using
        the index.

        Parameters
        ----------
        name : hashable
            Unique name used to identify the `graph`.
        graph : networkx.Graph

        Returns
        -------
        indexed_graph : networkx.Graph
        """
        nodes = graph.nodes()

        # Index new nodes.
        new_nodes = list(set(nodes) - set(self.node_index.values()))
        start = max(len(self.node_index) - 1, max(self.node_index.keys()))
        for i in xrange(start, start + len(new_nodes)):
            n = new_nodes.pop()
            self.node_index[i], self.node_lookup[n] = n, i
            self.graphs_containing[n].append(name)

        # Relabel nodes in `graph`.
        new_labels = {n: self.node_lookup[n] for n in nodes}
        indexed_graph = nx.relabel.relabel_nodes(graph, new_labels, copy=True)

        return indexed_graph

    def nodes(self, data=False, native=True):
        """
        Returns a list of all nodes in the :class:`.GraphCollection`\.

        Parameters
        ----------
        data : bool
            (default: False) If True, returns a list of 2-tuples containing
            node labels and attributes.

        Returns
        -------
        nodes : list
        """

        nodes = self.master_graph.nodes(data=data)
        if native:
            if data:
                nodes = [(self.node_index[n], attrs) for n, attrs in nodes]
            else:
                nodes = [self.node_index[n] for n in nodes]
        return nodes

    def edges(self, data=False, native=True):
        """
        Returns a list of all edges in the :class:`.GraphCollection`\.

        Parameters
        ----------
        data : bool
            (default: False) If True, returns a list of 3-tuples containing
            source and target node labels, and attributes.

        Returns
        -------
        edges : list
        """
        edges = self.master_graph.edges(data=data)
        if native:
            if data:
                edges = [(self.node_index[s], self.node_index[t], attrs)
                         for s, t, attrs in edges]
            else:
                edges = [(self.node_index[s], self.node_index[t])
                         for s, t in edges]
        return edges

    def order(self, piecewise=False):
        """
        Returns the total number of nodes in the :class:`.GraphCollection`\.
        """
        if piecewise:
            return {k: v.order() for k, v in self.items()}
        return self.master_graph.order()

    def node_distribution(self):
        warnings.warn("node_distribution will be removed in v0.8. Use" +
                      " order(piecewise=True) instead.", DeprecationWarning)
        return self.order(piecewise=True)

    def size(self, piecewise=False):
        """
        Returns the total number of edges in the :class:`.GraphCollection`\.
        """
        if piecewise:
            return {k: v.size() for k, v in self.items()}
        return self.master_graph.size()

    def edge_distribution(self):
        warnings.warn("edge_distribution will be removed in v0.8. Use" +
                      " size(piecewise=True) instead.", DeprecationWarning)
        return self.order(piecewise=True)

    def collapse(self, weight_attr='weight'):
        """
        Returns a :class:`networkx.Graph` or :class:`networkx.DiGraph` in which
        the edges between each pair of nodes are collapsed into a single
        weighted edge.
        """

        if self.directed:
            graph = nx.DiGraph()
        else:
            graph = nx.Graph()

        # Transfer all nodes and attributes.
        for n, attrs in self.master_graph.nodes(data=True):
            graph.add_node(n, attrs)

        for s, t, attrs in self.master_graph.edges(data=True):
            if not graph.has_edge(s, t):
                graph.add_edge(s, t)

            if 'weight' not in graph[s][t]:
                graph[s][t]['weight'] = 0.
            if weight_attr in attrs:
                graph[s][t]['weight'] += attrs[weight_attr]
            else:
                graph[s][t]['weight'] += 1.

            gname = attrs['graph']
            for k, v in attrs.iteritems():
                if k in [weight_attr, 'graph']:
                    continue
                if k not in graph[s][t]:
                    graph[s][t][k] = {}
                graph[s][t][k][gname] = v
        return graph

    def analyze(self, method_name, mapper=map, invert=False, **kwargs):
        """
        Apply a method from NetworkX to each of the graphs in the
        :class:`.GraphCollection`\.

        Example
        -------
        .. code-block:: python

           >>> G.analyze('betweenness_centrality')
           {'test': {0: 1.0, 1: 0.0, 2: 0.0},
            'test2': {0: 0.0, 1: 0.0, 2: 0.0, 3: 0.0}}
           >>> G.analyze('betweenness_centrality', results_by='node')
           {0: {'test': 1.0, 'test2': 0.0},
            1: {'test': 0.0, 'test2': 0.0},
            2: {'test': 0.0, 'test2': 0.0},
            3: {'test2': 0.0}}

        Parameters
        ----------
        method : str or iterable
            Must be the name of a method accessible directly from the
            `networkx` namespace. If an iterable, should be the complete
            dot-path to the method, e.g. ``nx.connected.is_connected`` would be
            written as ``['connected', 'is_connected']``.
        mapper : func
            A mapping function. Be default uses Python's builtin ``map``
            function. MUST return results in order.
        results_by : str
            (default: 'graph'). By default, the top-level key in the results
            are graph names. If results_by='node', node labels are used as
            top-level keys.
        kwargs : kwargs
            Any additional kwargs are passed to the NetworkX method.

        Returns
        -------
        dict

        """

        # Find the analysis method, if possible.
        if hasattr(method_name, '__iter__'):
            mpath = method_name
            if type(mpath) in [str, unicode]:
                mpath = [mpath]

            root = nx
            while len(mpath) > 0:
                head = getattr(root, mpath.pop(0))
            if hasattr(head, '__call__'):
                method = head
            else:
                raise NameError("No matching method in NetworkX")

        elif hasattr(nx, method_name):
            method = getattr(nx, method_name)
        else:
            raise AttributeError('No such method in NetworkX')

        # Farm out the analysis using ``mapper``. This allows us to use
        #  multiprocessing in the future, or to add pre- or post-processing
        #  routines.
        keys, graphs = zip(*self.items())
        results = mapper(method, graphs, **kwargs)

        # Group the results by graph.
        by_graph = dict(zip(keys, results))

        # Invert results.
        inverse = defaultdict(dict)
        for gname, result in by_graph.iteritems():
            if hasattr(result, '__iter__'):
                for n, val in result.iteritems():
                    inverse[n].update({gname: val})

        if type(list(by_graph.values())[0]) is dict:
            # Look for a result set that we can inspect.
            i = 0
            while True:
                if len(by_graph.values()[i]) > 0:
                    inspect = by_graph.values()[i]
                    break
                i += 1

            if type(list(inspect.keys())[0]) is tuple:
                # Results correspond to edges.
                by_edge = dict(inverse)

                # Set edge attributes in each graph.
                for graph, attrs in by_graph.iteritems():
                    nx.set_edge_attributes(self[graph], method_name, attrs)

                # Set edge attributes in the master graph.
                for (s, t), v in by_edge.iteritems():
                    for i, attrs in self.master_graph.edge[s][t].iteritems():
                        val = v[attrs['graph']]
                        self.master_graph.edge[s][t][i][method_name] = val

                if invert:
                    return by_edge
            else:
                # Results correspond to nodes.
                by_node = dict(inverse)

                # Set node attributes for each graph.
                for graph, attrs in by_graph.iteritems():
                    nx.set_node_attributes(self[graph], method_name, attrs)

                # Store node attributes in the master graph.
                nx.set_node_attributes(self.master_graph, method_name, by_node)

                if invert:
                    return by_node
        return by_graph

    def node_history(self, node, attribute):
        """
        Returns a dictionary of attribute values for each ``networkx.Graph`` in
        the :class:`.GraphCollection` for a single node.

        Parameters
        ----------
        node : str
            The node of interest.
        attribute : str
            The attribute of interest; e.g. 'betweenness_centrality'

        Returns
        -------
        history : dict
        """
        return self.master_graph.node[node][attribute]

    def edge_history(self, source, target, attribute):
        """
        Returns a dictionary of attribute vales for each Graph in the
        :class:`.GraphCollection` for a single edge.

        Parameters
        ----------
        source : str
            Identifier for source node.
        target : str
            Identifier for target node.
        attribute : str
            The attribute of interest; e.g. 'betweenness_centrality'

        Returns
        -------
        history : dict
        """

        return {attr['graph']: attr[attribute] for i, attr
                in self.master_graph.edge[source][target].items()}

    def union(self, weight_attr='_weight'):
        """
        Returns the union of all graphs in this :class:`.GraphCollection`\.

        The number of graphs in which an edge exists between each node pair `u` and `v`
        is stored in the edge attribute given be `weight_attr` (default: `_weight`).

        Parameters
        ----------
        weight_attr : str
            (default: '_weight') Name of the edge attribute used to store the number of
            graphs in which an edge exists between node pairs.

        Returns
        -------
        graph : :class:`networkx.Graph`
        """

        if type(self.master_graph) is nx.MultiDiGraph:
            graph = nx.DiGraph()
        else:
            graph = nx.Graph()

        edge_attrs = defaultdict(list)

        for u, v, a in self.master_graph.edges(data=True):
            if not graph.has_edge(u, v):
                graph.add_edge(u, v)
                graph[u][v]['graphs'] = []
                graph[u][v][weight_attr] = 0.

            for key, value in a.iteritems():
                if key not in graph[u][v]:
                    graph[u][v][key] = []
                graph[u][v][key].append(value)
            graph[u][v]['graphs'].append(a['graph'])
            graph[u][v][weight_attr] += 1.

        for u, a in self.master_graph.nodes(data=True):
            for key, value in a.iteritems():
                graph.node[u][key] = value

        return graph
