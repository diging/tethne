import tethne.writers as wr
import tethne.utilities as util
import unittest
import networkx as nx
import os

class TestSifWriter(unittest.TestCase):
    def setUp(self):
        self.simple_graph = nx.Graph() 
        self.simple_graph.add_path(range(5))

        self.multi_graph = nx.MultiGraph()
        self.multi_graph.add_path(range(5))
        self.multi_graph.add_path(range(5))

        # can a path be a person?
        self.attribs = {'brown_eyes':2,
                        'loves_travel':1,
                        'brown_hair':'lots'}
        # wat
        self.simple_attribs = nx.Graph()
        self.simple_attribs.add_path(range(5), **self.attribs)

        self.multi_attribs = nx.MultiGraph()
        self.multi_attribs.add_path(range(5), **self.attribs)
        self.multi_attribs.add_path(range(5), **self.attribs)

    def test_simple_graph(self):
        filepath = os.path.join(os.path.dirname(__file__), 'testout',
                                'simple_graph')
        wr.graph.to_sif(self.simple_graph, filepath)
        expected = ('0 rel 1\n' +
                    '1 rel 2\n' +
                    '2 rel 3\n' +
                    '3 rel 4\n')
        obtained = open(filepath + '.sif', 'r').read()
        self.assertEqual(expected, obtained)
        os.remove(filepath + '.sif')

    def test_multi_graph(self):
        filepath = os.path.join(os.path.dirname(__file__), 'testout',
                                'multi_graph')
        wr.graph.to_sif(self.multi_graph, filepath)
        expected = ('0 0 1\n' +
                    '0 1 1\n' +
                    '1 0 2\n' +
                    '1 1 2\n' +
                    '2 0 3\n' +
                    '2 1 3\n' +
                    '3 0 4\n' +
                    '3 1 4\n')
        obtained = open(filepath + '.sif', 'r').read()
        self.assertEqual(expected, obtained)
        os.remove(filepath + '.sif')

    def test_simple_attribs(self):
        filepath = os.path.join(os.path.dirname(__file__), 'testout',
                                'simple_attribs')
        wr.graph.to_sif(self.simple_attribs, filepath)

        # test sif
        expected = ('0 rel 1\n' +
                    '1 rel 2\n' +
                    '2 rel 3\n' +
                    '3 rel 4\n')
        obtained = open(filepath + '.sif', 'r').read()
        self.assertEqual(expected, obtained)
        os.remove(filepath + '.sif')

        # test eda
        for key, value in self.attribs.iteritems():
            expected = (key + '\n' +
                        '0 (rel) 1 = ' + str(value) + '\n' +
                        '1 (rel) 2 = ' + str(value) + '\n' +
                        '2 (rel) 3 = ' + str(value) + '\n' +
                        '3 (rel) 4 = ' + str(value) + '\n')
            obtained = open(filepath + '_' + key + '.eda', 'r').read()
            self.assertEqual(expected, obtained)
            os.remove(filepath + '_' + key + '.eda')

    def test_multi_attribs(self):
        filepath = os.path.join(os.path.dirname(__file__), 'testout',
                                'multi_attribs')
        wr.graph.to_sif(self.multi_attribs, filepath)

        # test sif
        obtained = open(filepath + '.sif', 'r').read()
        expected = ('0 0 1\n' +
                    '0 1 1\n' +
                    '1 0 2\n' +
                    '1 1 2\n' +
                    '2 0 3\n' +
                    '2 1 3\n' +
                    '3 0 4\n' +
                    '3 1 4\n')
        self.assertEqual(expected, obtained)
        os.remove(filepath + '.sif')

        # test eda
        for key, value in self.attribs.iteritems():
            expected = (key + '\n' +
                        '0 (0) 1 = ' + str(value) + '\n' +
                        '0 (1) 1 = ' + str(value) + '\n' +
                        '1 (0) 2 = ' + str(value) + '\n' +
                        '1 (1) 2 = ' + str(value) + '\n' +
                        '2 (0) 3 = ' + str(value) + '\n' +
                        '2 (1) 3 = ' + str(value) + '\n' +
                        '3 (0) 4 = ' + str(value) + '\n' +
                        '3 (1) 4 = ' + str(value) + '\n')
            obtained = open(filepath + '_' + key + '.eda', 'r').read()
            self.assertEqual(expected, obtained)
            os.remove(filepath + '_' + key + '.eda')

    def tearDown(self):
        pass

if __name__ == '__main__':
    unittest.main()
