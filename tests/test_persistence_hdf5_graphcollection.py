from settings import *

import unittest

import warnings

from tethne.readers import wos, dfr
from tethne.classes import Corpus, GraphCollection
from tethne.networks.authors import coauthors
from tethne.persistence.hdf5.graphcollection import HDF5Graph, HDF5GraphCollection
from tethne.persistence.hdf5.util import get_h5file, get_or_create_group

import os

import networkx as nx

dfrdatapath = '{0}/dfr'.format(datapath)
ngrams = dfr.ngrams(dfrdatapath, 'uni')
papers = dfr.read(dfrdatapath)

D = Corpus(papers, index_by='doi')
D.slice('date', method='time_period', window_size=1)

class TestHDF5Graph(unittest.TestCase):
    def setUp(self):
        self.h5name = 'HDF5Graph_test.h5'
        self.h5path = temppath + '/' + self.h5name
        self.h5file,a,b = get_h5file('HDF5Graph', self.h5path)
        self.group = get_or_create_group(self.h5file, 'testgroup')

        g = nx.Graph()
        g.add_edge(0,1)
        g.add_edge(1,2, weight=5)
        g.add_edge(5,0, {'weight':3, 'girth':'wtf'})
        g.add_node(0, {'size':0.5, 'label':'bob'})
        self.g = g
    
        self.hg = HDF5Graph(self.h5file, self.group, 'testGraph', g)
    
    def test_edges(self):
        self.assertEqual(self.hg.edges(), self.g.edges())
    
    def test_nodes(self):
        self.assertEqual(self.hg.nodes(), self.g.nodes())
    
    def test_edges_data(self):
        self.assertEqual(self.hg.edges(data=True), self.g.edges(data=True))
    
    def test_nodes_data(self):
        self.assertEqual(self.hg.nodes(data=True), self.g.nodes(data=True))
    
    def test_len(self):
        self.assertEqual(len(self.hg), len(self.g))
    
    def test_getitem(self):
        self.assertEqual(self.hg[0], self.g[0])
    
    def test_node(self):
        self.assertEqual(self.hg.node[0], self.g.node[0])
    
    def test_edge(self):
        self.assertEqual(self.hg.edge[0], self.g.edge[0])
    
    def test_betweenness(self):
        hg_bc = nx.betweenness_centrality(self.hg)
        g_bc = nx.betweenness_centrality(self.g)
        self.assertEqual(hg_bc, g_bc)
    
    def test_closeness(self):
        hg_bc = nx.closeness_centrality(self.hg)
        g_bc = nx.closeness_centrality(self.g)
        self.assertEqual(hg_bc, g_bc)
    
    def test_edge_betweenness(self):
        hg_bc = nx.edge_betweenness(self.hg)
        g_bc = nx.edge_betweenness(self.g)
        self.assertEqual(hg_bc, g_bc)

    def tearDown(self):
        os.remove(self.h5path)


class TestGraphCollection(unittest.TestCase):
    def setUp(self):
        self.h5name = 'HDF5GraphCollection_test.h5'
        self.h5path = temppath + '/' + self.h5name
        self.h5file,a,b = get_h5file('HD5GraphCollection', self.h5path)
    
        self.G_ = GraphCollection()

        for k,v in D.get_slices('date', papers=True).iteritems():
            self.G_[k] = coauthors(v)

        self.G = HDF5GraphCollection(self.G_, datapath=self.h5path)

    def test_open(self):
        dpath = self.G.path

        G2 = HDF5GraphCollection(GraphCollection(), dpath)

        self.assertEqual(set(G2.nodes()), set(self.G.nodes()))
        self.assertEqual(set(G2.edges()), set(self.G.edges()))
        self.assertEqual(len(G2.node_index), len(self.G.node_index))
        self.assertEqual(G2.node_distribution(), self.G.node_distribution())
        self.assertEqual(G2.edge_distribution(), self.G.edge_distribution())
        self.assertEqual(   G2.attr_distribution()[0],
                            self.G.attr_distribution()[0]  )
        self.assertEqual(   G2.attr_distribution()[1],
                            self.G.attr_distribution()[1]  )


    def test_nodes(self):
        """
        should return a list of integers
        """
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.nodes.png'
        with Profile(pcgpath):
            nodes = self.G.nodes()

        self.assertIsInstance(nodes, list)
        self.assertIsInstance(nodes[0], int)
        self.assertEqual(set(self.G.nodes()), set(self.G_.nodes()))

    def test_edges(self):
        """
        should return a list of (int,int) tuples.
        """
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.edges.png'
        with Profile(pcgpath):
            edges = self.G.edges()

        self.assertIsInstance(edges, list)
        self.assertIsInstance(edges[0], tuple)
        self.assertIsInstance(edges[0][0], int)
        self.assertIsInstance(edges[0][1], int)
        self.assertEqual(set(self.G.edges()), set(self.G_.edges()))

    def test_index_graph(self):
        """
        index should be as large as set of unique nodes in all graphs
        """

        unodes = set([ n for g in self.G.graphs.values() for n in g.nodes() ])
        self.assertEqual(len(self.G.node_index), len(unodes))
        self.assertEqual(len(self.G.node_index), len(self.G_.node_index))

    def test__plot(self):
        """
        :func:`._plot` should return a :class:`matplotlib.figure.Figure`
        """

        xvalues = range(0, 10)
        yvalues = range(0, 10)
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection._plot.png'
        with Profile(pcgpath):
            fig = self.G._plot((xvalues, yvalues), 'test')

#        self.assertIsInstance(fig, matplotlib.figure.Figure)

    def test_node_distribution(self):
        """
        :func:`.node_distribution` should return a tuple of ([keys],[values]).
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.node_distribution.png'
        with Profile(pcgpath):
            data = self.G.node_distribution()

        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)
        self.assertEqual(len(data[0]), len(data[1]))
        self.assertEqual(data, self.G_.node_distribution())

    def test_plot_node_distribution(self):
        """
        :func:`.plot_node_distribution` should return a
        :class:`matplotlib.figure.Figure`
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.plot_node_distribution.png'
        with Profile(pcgpath):
            fig = self.G.plot_node_distribution()

#        self.assertIsInstance(fig, matplotlib.figure.Figure)

    def test_edge_distribution(self):
        """
        :func:`.edge_distribution` should return a tuple of ([keys],[values]).
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.edge_distribution.png'
        with Profile(pcgpath):
            data = self.G.edge_distribution()

        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)
        self.assertEqual(len(data[0]), len(data[1]))
        self.assertEqual(data, self.G_.edge_distribution())

    def test_plot_edge_distribution(self):
        """
        :func:`.plot_edge_distribution` should return a
        :class:`matplotlib.figure.Figure`
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.plot_edge_distribution.png'
        with Profile(pcgpath):
            fig = self.G.plot_edge_distribution()

#        self.assertIsInstance(fig, matplotlib.figure.Figure)

    def test_attr_distribution(self):
        """
        :func:`.attr_distribution` should return a tuple of ([keys],[values]).
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.attr_distribution.png'
        with warnings.catch_warnings(record=False) as w:
            warnings.simplefilter('ignore') # Some slices have no values.
            with Profile(pcgpath):
                data = self.G.attr_distribution()

        self.assertIsInstance(data, tuple)
        self.assertIsInstance(data[0], list)
        self.assertIsInstance(data[1], list)
        self.assertEqual(len(data[0]), len(data[1]))
        self.assertEqual(data[0], self.G_.attr_distribution()[0])
        self.assertEqual(data[1], self.G_.attr_distribution()[1])

    def test_plot_attr_distribution(self):
        """
        :func:`.plot_attr_distribution` should return a
        :class:`matplotlib.figure.Figure`
        """

        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.plot_attr_distribution.png'
        with warnings.catch_warnings(record=False) as w:
            warnings.simplefilter('ignore') # Some slices have no values.
            with Profile(pcgpath):
                fig = self.G.plot_attr_distribution()

    def tearDown(self):
        os.remove(self.h5path)



if __name__ == '__main__':
    unittest.main()