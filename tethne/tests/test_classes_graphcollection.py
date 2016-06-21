import sys
sys.path.append('./')

import unittest

import networkx as nx

from tethne.classes.graphcollection import GraphCollection
from tethne.readers.wos import read
from tethne.networks.authors import coauthors


datapath = './tethne/tests/data/wos.txt'
datapath2 = './tethne/tests/data/wos2.txt'

class TestGraphCollectionCreation(unittest.TestCase):
    def test_init(self):
        G = GraphCollection()

        self.assertTrue(hasattr(G, 'master_graph'))
        self.assertTrue(hasattr(G, 'node_index'))
        self.assertTrue(hasattr(G, 'node_lookup'))
        self.assertTrue(hasattr(G, 'graphs_containing'))

    def test_init_directed(self):
        G = GraphCollection(directed=True)
        graph = nx.DiGraph()
        graph.add_edge('A', 'B', c='d')
        graph.add_edge('B', 'C', c='e')
        graph.node['A']['bob'] = 'dole'
        graph_name = 'test'

        graph2 = nx.DiGraph()
        graph2.add_edge('A', 'B', c='d')
        graph2.add_edge('D', 'C', c='f')
        graph2.node['A']['bob'] = 'dole'
        graph2_name = 'test2'

        G.add(graph_name, graph)
        G.add(graph2_name, graph2)

        # The indexed graph is directed-isomorphic to the original graph.
        matcher = nx.isomorphism.DiGraphMatcher(G[graph_name], graph)
        self.assertTrue(matcher.is_isomorphic)
        matcher = nx.isomorphism.DiGraphMatcher(G[graph2_name], graph2)
        self.assertTrue(matcher.is_isomorphic)

    def test_init_build(self):
        """
        Should build `graphs` if passed a corpus and method.
        """
        corpus = read(datapath, index_fields=['ayjid', 'date'])
        G = GraphCollection(corpus, coauthors)
        self.assertEqual(len(G), len(corpus.indices['date']))

    def test_init_build_streaming(self):
        """
        Should build `graphs` if passed a corpus and method.
        """
        corpus = read(datapath, streaming=True)
        G = GraphCollection(corpus, coauthors, slice_kwargs={'feature_name': 'authors'})
        self.assertEqual(len(G), len(corpus.indices['date']))

    def test_build(self):
        """
        """
        corpus = read(datapath)
        G = GraphCollection()
        G.build(corpus, coauthors)
        self.assertEqual(len(G), len(corpus.indices['date']))

    def test_build_streaming(self):
        """
        """
        corpus = read(datapath, streaming=True)
        G = GraphCollection()
        G.build(corpus, coauthors, slice_kwargs={'feature_name': 'authors'})
        self.assertEqual(len(G), len(corpus.indices['date']))

    def test_index(self):
        """
        Index a :ref:`networkx.Graph <networkx:graph>`\, but don't add it to the
        :class:`.GraphCollection`\.
        """
        G = GraphCollection()
        graph = nx.Graph()
        graph.add_edge('A', 'B', c='d')
        graph.add_edge('B', 'C', c='e')
        graph_name = 'test'

        igraph = G.index(graph_name, graph)

        # The number of nodes and edges is unchanged.
        self.assertEqual(len(graph.nodes()), len(igraph.nodes()))
        self.assertEqual(len(graph.edges()), len(igraph.edges()))

        # The indexed graph is isomorphic to the original graph.
        self.assertTrue(nx.isomorphism.is_isomorphic(igraph, graph))

        # Can find original node names in the correct graphs.
        for n in graph.nodes():
            self.assertIn(n, G.node_lookup)
            self.assertIn(graph_name, G.graphs_containing[n])

    def test_add(self):
        """
        Add a :ref:`networkx.Graph <networkx:graph>` to the :class:`.GraphCollection`\.
        """
        G = GraphCollection()
        graph = nx.Graph()
        graph.add_edge('A', 'B', c='d')
        graph.add_edge('B', 'C', c='e')
        graph.node['A']['bob'] = 'dole'
        graph_name = 'test'

        G.add(graph_name, graph)

        # Graph is added to the GraphCollection.
        self.assertIn(graph_name, G)

        # The graph name should be added to edge attributes in the
        #  master_graph.
        for s, t, attrs in G.master_graph.edges(data=True):
            self.assertIn('graph', attrs)
            self.assertEqual(attrs['graph'], graph_name)

        # The number of nodes and edges is unchanged.
        self.assertEqual(len(graph.nodes()), len(G[graph_name].nodes()))
        self.assertEqual(len(graph.edges()), len(G[graph_name].edges()))

        # The indexed graph is isomorphic to the original graph.
        self.assertTrue(nx.isomorphism.is_isomorphic(G[graph_name], graph))

        # Can find original node names in the correct graphs.
        for n, attrs in graph.nodes(data=True):
            self.assertIn(n, G.node_lookup)
            self.assertIn(graph_name, G.graphs_containing[n])

            i = G.node_lookup[n]
            for k, v in attrs.iteritems():
                self.assertIn(k, G.master_graph.node[i])
                self.assertIn(graph_name, G.master_graph.node[i][k])
                self.assertEqual(v, G.master_graph.node[i][k][graph_name])

        # Should raise a ValueError if name has already been used.
        with self.assertRaises(ValueError):
            G.add(graph_name, nx.Graph())


class TestGraphCollectionMethods(unittest.TestCase):
    def setUp(self):
        self.G = GraphCollection()
        self.graph = nx.Graph()
        self.graph.add_edge('A', 'B', c='d')
        self.graph.add_edge('B', 'C', c='e')
        self.graph.node['A']['bob'] = 'dole'
        graph_name = 'test'

        self.graph2 = nx.Graph()
        self.graph2.add_edge('A', 'B', c='d')
        self.graph2.add_edge('D', 'C', c='f')
        self.graph2.node['A']['bob'] = 'dole'
        graph2_name = 'test2'

        self.G.add(graph_name, self.graph)
        self.G.add(graph2_name, self.graph2)

    def test_nodes(self):
        """
        :meth:`.GraphCollection.nodes` should behave like
        :meth:`networkx.Graph.nodes`\, but return values for all of the
        :ref:`networkx.Graph <networkx:graph>`\s in the :class:`.GraphCollection`\.
        """

        joint_nodes = set(self.graph.nodes()) | set(self.graph2.nodes())
        self.assertEqual(len(self.G.nodes(data=True)), len(joint_nodes))
        self.assertTrue(hasattr(self.G.nodes(), '__iter__'),
                        "GraphCollection.nodes() should be iterable.")

        self.assertIsInstance(self.G.nodes(data=True)[0], tuple,
                              "Should return a 2-tuple when data=True")
        self.assertEqual(len(self.G.nodes(data=True)[0]), 2,
                         "Should return a 2-tuple when data=True")

    def test_edges(self):
        """
        :meth:`.GraphCollection.edges` should behave like
        :meth:`networkx.Graph.edges`\, but return values for all of the
        :ref:`networkx.Graph <networkx:graph>`\s in the :class:`.GraphCollection`\.
        """

        self.assertIsInstance(self.G.edges()[0], tuple,
                              "Should return a 2-tuple when data=False")
        self.assertEqual(len(self.G.edges()[0]), 2,
                         "Should return a 3-tuple when data=False")

        self.assertIsInstance(self.G.edges(data=True)[0], tuple,
                              "Should return a 3-tuple when data=True")
        self.assertEqual(len(self.G.edges(data=True)[0]), 3,
                         "Should return a 3-tuple when data=True")

    def test_order(self):
        """
        :meth:`.GraphCollection.order` should return the number of nodes in
        the :class:`.GraphCollection`\. If `piecewise` is True, should return a
        dict containing the order of each :ref:`networkx.Graph <networkx:graph>` in the
        :class:`.GraphCollection`\.
        """

        joint_nodes = set(self.graph.nodes()) | set(self.graph2.nodes())
        self.assertEqual(self.G.order(), len(joint_nodes))

        self.assertIsInstance(self.G.order(piecewise=True), dict,
                              "order() should return a dict if piecewise=True")
        self.assertIn('test', self.G.order(piecewise=True),
                      ''.join(["order(piecewise=True) should return a dict",
                               " with graph names as keys"]))
        self.assertIn('test2', self.G.order(piecewise=True),
                      ''.join(["order(piecewise=True) should return a dict",
                               " with graph names as keys"]))

    def test_size(self):
        """
        :meth:`.GraphCollection.size` should return the number of nodes in the
        :class:`.GraphCollection`\. If `piecewise` is True, should return a
        dict containing the size of each :ref:`networkx.Graph <networkx:graph>` in the
        :class:`.GraphCollection`\.
        """

        N_edges = len(self.graph.edges()) + len(self.graph2.edges())
        self.assertEqual(self.G.size(), N_edges)

        self.assertIsInstance(self.G.size(piecewise=True), dict,
                              "size() should return a dict if piecewise=True")
        self.assertIn('test', self.G.size(piecewise=True),
                      ''.join(["size(piecewise=True) should return a dict",
                               " with graph names as keys"]))
        self.assertIn('test2', self.G.size(piecewise=True),
                      ''.join(["size(piecewise=True) should return a dict",
                               " with graph names as keys"]))

    def test_getattr(self):
        """
        Can retrieve a graph as an attribute of the :class:`.GraphCollection`\.
        """

        self.assertIsInstance(self.G.test, nx.Graph)
        self.assertIsInstance(self.G.test2, nx.Graph)
        with self.assertRaises(AttributeError):
            self.G.nosuchgraph

    def test_collapse(self):
        cgraph = self.G.collapse()

        joint_nodes = set(self.graph.nodes()) | set(self.graph2.nodes())
        self.assertIsInstance(cgraph, nx.Graph)
        self.assertEqual(cgraph.order(), len(joint_nodes))

        # All Node attributes should be retained.
        for n, attrs in cgraph.nodes(data=True):
            self.assertDictEqual(attrs, self.G.master_graph.node[n])

        # Edge attributes should be retained, keyed on the graph associated
        #  with the edge from which each value was obtained.
        for s, t, attrs in cgraph.edges(data=True):
            for k, v in attrs.iteritems():
                if k != 'weight':
                    for v_ in v.keys():
                        self.assertIn(v_, ['test', 'test2'])

    def test_analyze(self):
        # By default, graph names are the top-level keys.
        results = self.G.analyze('betweenness_centrality')
        self.assertIsInstance(results, dict)
        for gname in self.G.keys():
            self.assertIn(gname, results)

        # Passing results_by='node' re-organizes the results so that node
        #  labels are the top-level key.
        results_n = self.G.analyze('betweenness_centrality', invert=True)
        for n in self.G.nodes(native=False):
            self.assertIn(n, results_n)

        # Asking for a non-existent method results in an AttributeError.
        with self.assertRaises(AttributeError):
            self.G.analyze('nosuch_method')

        # Can use a custom `map` function (e.g. to support parallelism in the
        #  future).
        def mymapper(func, iterable, **kwargs):
            r = map(func, iterable, **kwargs)
            return [{k: v+5. for k, v in values.items()} for values in r]

        results_m = self.G.analyze('betweenness_centrality', mapper=mymapper)
        for key, value in results.iteritems():
            for k in value.keys():
                self.assertEqual(results[key][k] + 5., results_m[key][k])

    def test_analyze_edge(self):
        results = self.G.analyze('edge_betweenness_centrality', invert=True)
        for e in self.G.edges(native=False):
            self.assertIn(e, results)

    def test_analyze_graph(self):
        results = self.G.analyze('is_connected')
        for gname in self.G.keys():
            self.assertIn(gname, results)

    def test_analyze_path(self):
        results = self.G.analyze(['connected', 'is_connected'])
        for gname in self.G.keys():
            self.assertIn(gname, results)

    def test_node_history(self):
        results = self.G.analyze('betweenness_centrality', invert=True)
        hist = self.G.node_history(0, 'betweenness_centrality')

        self.assertDictEqual(results[0], hist)

    def test_edge_history(self):
        results = self.G.analyze('edge_betweenness_centrality', invert=True)
        hist = self.G.edge_history(0, 1, 'edge_betweenness_centrality')

        self.assertDictEqual(results[0, 1], hist)

    def test_union(self):
        weight_attr = 'test_weight'
        graph = self.G.union(weight_attr=weight_attr)

        self.assertIsInstance(graph, nx.Graph)
        self.assertGreater(self.G.size(), graph.size())
        self.assertEqual(graph.order(), self.G.order())
        self.assertIn(weight_attr, graph.edges(data=True)[0][2])

        # Node attributes present.
        for u, a in self.G.master_graph.nodes(data=True):
            for key, value in a.iteritems():
                self.assertIn(key, graph.node[u])

        # Edge attributes present.
        for u, v, a in self.G.master_graph.edges(data=True):
            for key, value in a.iteritems():
                self.assertIn(key, graph[u][v])
                if key == weight_attr:
                    self.assertIsInstance(value, float)
                else:
                    self.assertIsInstance(graph[u][v][key], list)

if __name__ == '__main__':
    unittest.main()
