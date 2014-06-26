from settings import *

import unittest

import warnings

from tethne.readers import wos, dfr
from tethne.classes import DataCollection, GraphCollection
from tethne.networks.authors import coauthors
from tethne.persistence.hdf5.graphcollection import HDF5GraphCollection

import cPickle as pickle
with open('{0}/dfr_DataCollection.pickle'.format(picklepath), 'r') as f:
    D = pickle.load(f)

import matplotlib

class TestGraphCollection(unittest.TestCase):
    def setUp(self):
        self.G_ = GraphCollection()

        for k,v in D.get_slices('date', include_papers=True).iteritems():
            self.G_[k] = coauthors(v)

        self.G = HDF5GraphCollection(self.G_)

    def test_nodes(self):
        """
        should return a list of integers
        """
        
        pcgpath = cg_path + 'persistence.hdf5.HDF5GraphCollection.nodes.png'
        with Profile(pcgpath):
            nodes = self.G.nodes()

        self.assertIsInstance(nodes, list)
        self.assertIsInstance(nodes[0], int)

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

    def test_index_graph(self):
        """
        index should be as large as set of unique nodes in all graphs
        """

        unodes = set([ n for g in self.G.graphs.values() for n in g.nodes() ])
        self.assertEqual(len(self.G.node_index), len(unodes))

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



if __name__ == '__main__':
    unittest.main()