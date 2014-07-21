import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

from ...classes import GraphCollection
from util import *
from networkx import Graph
import numpy
from scipy.sparse import coo_matrix

import cPickle as pickle

class HDF5GraphCollection(GraphCollection):
    """
    Provides HDF5 persistence for :class:`.GraphCollection`\.
    
    At this time, the :class:`.HDF5GraphCollection` should only be used for
    storing existing :class:`.GraphCollection`\, and NOT for direct 
    manipulation.
    """
    def __init__(self, G, datapath=None):
        """
        Initialize a :class:`.HDF5GraphCollection` with a 
        :class:`.GraphCollection`\.
        """
    
        logger.debug('HDF5GraphCollection: initialize.')

        self.h5file, self.path, self.uuid = get_h5file('GraphCollection', datapath)
        logger.debug('HDF5GraphCollection: got h5file at path {0}'
                                                             .format(self.path))
        
        # Load or create arrays group.
        self.agroup = get_or_create_group(self.h5file, 'arrays')
        logger.debug('HDF5GraphCollection: initialized array group.')
        
        self.group = get_or_create_group(self.h5file, 'graphs')
        
        # Forward and reverse indices for nodes.
        index_values = [ G.node_index[k] for k in sorted(G.node_index.keys()) ]
        self.node_index = HDF5ArrayDict(self.h5file, self.agroup,
                                        'node_index', index_values)
                                        
        # Not stored.
        self.node_lookup = { v:k for k,v in self.node_index.iteritems() }
        
        logger.debug('HDF5GraphCollection: initialized node index and lookup' +\
                     ' for {0} nodes'.format(len(self.node_index)))
    
        self.edge_list = [] # Not stored.
    
        self.graphs = {}
        gchildren = self.group._v_children.keys()
        if len(gchildren) > 0:
            for child in gchildren:
                key = child[6:] # Cut off 'graph_' at start.
                try:    # Keys may be ints, but we can't store them that way.
                    key = int(key)
                except:
                    pass
                self.graphs[key] = HDF5Graph(self.h5file, self.group, child, None)
        else:
            for key, graph in G.graphs.iteritems():
                name = 'graph_' + str(key)
                self.graphs[key] = HDF5Graph(self.h5file, self.group, name, graph)

    def __getitem__(self, key):
        name = 'graph_' + str(key)
        try:
            return self.graphs[key]
        except KeyError:
            if name in self.group:
                self.graphs[key] = HDF5Graph(self.h5file, self.group, name, None)
            else:
                raise KeyError()

    def __setitem__(self, key, value):
        name = 'graph_' + str(key)
        self.graphs[key] = HDF5Graph(self.h5file, self.group, name, value)


class HDF5Graph(Graph):
    def __init__(self, h5file, pgroup, name, graph):
        if type(h5file) is str:
            self.h5file, self.path, self.uuid = get_h5file('HDF5Graph', h5file)
        else:
            self.h5file = h5file
        self.group = get_or_create_group(h5file, name, where=pgroup)
        
        if graph is None:
            edge_values = None
            node_values = None
        else:
            edge_values = graph.edge
            node_values = graph.node

        self.edge = HDF5EdgeAttributes(h5file, self.group, edge_values)
        self.node = HDF5NodeAttributes(h5file, self.group, node_values)
        self.adj = self.edge

    def edges(self, data=False):
        edges = self.edge.get_edges(data=data)
        return edges

    def nodes(self, data=False):
        return self.node.get_nodes(data=data)

class HDF5EdgeAttributes(object):
    def __init__(self, h5file, pgroup, edges):
        self.h5file = h5file
        self.group = get_or_create_group(h5file, 'edges', where=pgroup)
        self.fieldgroup = get_or_create_group(h5file, 'fieldgroup', where=self.group)
        self.fields = get_or_create_table(h5file, self.group, 'fields', FieldIndex)
        
        I = []
        J = []
        K = []
        V = []
        self.field_values = {}

        if 'neighbors' in self.group._v_children.keys():  # Data already exists?
            fieldchildren = self.fieldgroup._v_children.keys()
            for child in fieldchildren:
                carray = get_or_create_array(self.h5file, self.fieldgroup,
                                                          child, None)
                self.field_values[child] = carray

        else:   # No data in this group.
            # Get the names and types of attribute fields.
            fieldkeys = {}
            mvalues = { 'index': [] }

            reverse = {}
            k = 1
            for i, neighbors in edges.iteritems():
                if i not in reverse: reverse[i] = []
                for j, attributes in neighbors.iteritems():
                    # Avoid adding the same edge twice.
                    if j not in reverse: reverse[j] = []
                    if j in reverse[i]: continue
                    reverse[j].append(i)

                    I.append(i)
                    J.append(j)
                    K.append(int(k))
                    k += 1
                    V.append(attributes)
                    for name, value in attributes.iteritems():
                        if name not in mvalues:
                            this_type = str(type(value))
                            fieldkeys[name] = this_type

                            mvalues[name] = []
                            # Pad 0th entry will null values.
                            if this_type == str(type('')): mvalues[name].append('')
                            if this_type == str(type(1)): mvalues[name].append(0)
                            if this_type == str(type(1.1)): mvalues[name].append(0.0)
                            if this_type == str(type(u'')): mvalues[name].append(u'')
                            if this_type == str(type([])): mvalues[name].append(pickle.dumps([]))

            # Generate attribute vectors.
            for v in V:
                for name,this_type in fieldkeys.iteritems():
                    if name in v:
                        mvalues[name].append(v[name])
                    else:
                        if this_type == str(type('')): mvalues[name].append('')
                        if this_type == str(type(1)): mvalues[name].append(0)
                        if this_type == str(type(1.1)): mvalues[name].append(0.0)
                        if this_type == str(type(u'')): mvalues[name].append(u'')
                        if this_type == str(type([])): mvalues[name].append(pickle.dumps([]))
                        
            # Get or create arrays that hold attribute vectors.
            for name in fieldkeys.keys():
                if fieldkeys[name] == str(type([])):
                    mvalues[name] = [ pickle.dumps(v) for v in mvalues[name] ]
                self.field_values[name] = get_or_create_array(self.h5file,
                                                              self.fieldgroup,
                                                              name,
                                                              mvalues[name])

            if len([ r for r in self.fields ]) == 0:   # New Graph.
                # Generate a fields table.
                for name,this_type in fieldkeys.iteritems():
                    query = 'name == b"{0}"'.format(name)
                    matches = [ row for row in self.fields.where(query)]
                    if len(matches) == 0:
                        fieldentry = self.fields.row
                        fieldentry['name'] = name
                        fieldentry['type'] = this_type
                        fieldentry.append()
                self.fields.flush()

        self.neighbors = SparseArray(self.h5file, self.group, 'neighbors', I, J, K)

    def __getitem__(self, i):
        neighbors = self.neighbors.get_neighbors(i)
        attributes = {}
        for j in neighbors:
            j_attributes = {}
            k = self.neighbors[(i,j)]
            attributes[j] = self._get_attributes(k)

        return attributes
    

    def _get_attributes(self, k):
        attr_types = { row['name']:row['type'] for row in self.fields }
        attr_names = attr_types.keys()
        attr = {}
        for name in attr_names:
            vals = self.field_values[name].read()
            value = vals[k]
            this_type = attr_types[name]
            if this_type == str(type('')):
                value = str(value)
                if value == '': continue
            if this_type == str(type(1)):
                value = int(value)
                if value == 0: continue
            if this_type == str(type(1.1)):
                value = float(value)
                if value == 0.0: continue
            if this_type == str(type(u'')):
                value = unicode(value)
                if value == u'': continue
            if this_type == str(type([])):
                value = pickle.loads(value)
                if value == []: continue
            attr[name] = value
        return attr

    def items(self):
        return { i:self[i] for i in xrange(len(self.neighbors)) }

    def __len__(self):
        return self.neighbors.num_edges()

    def get_edges(self, data=False):
        edges = self.neighbors.get_edges(data=data)
        if data:
            edges_with_data = []
            attr_types = { row['name']:row['type'] for row in self.fields }
            attr_names = attr_types.keys()
            for edge in edges:
                k = edge[2]
                attrs = self._get_attributes(k)
                edges_with_data.append((edge[0], edge[1], attrs))
            
            return edges_with_data
        return edges

class SparseArray(object):
    def __init__(self, h5file, pgroup, name, I, J, K):
        self.h5file = h5file
        self.pgroup = pgroup
        self.name = name
        self.group = get_or_create_group(h5file, name, where=pgroup)

        self.I = get_or_create_array(h5file, self.group, 'I', I)
        self.J = get_or_create_array(h5file, self.group, 'J', J)
        self.K = get_or_create_array(h5file, self.group, 'K', K)
    
        self.h5file.flush()
    
    def __getitem__(self, indices):
        I = numpy.array(self.I.read())
        J = numpy.array(self.J.read())
        K = numpy.array(self.K.read())
        i, j = indices
        for x in xrange(len(I)):
            if (I[x] == i and J[x] == j) or (I[x] == j and J[x] == i):
                return K[x]
        raise KeyError()

    def get_neighbors(self, i):
        I = numpy.array(self.I.read())
        J = numpy.array(self.J.read())
        
        neighbors = []
        for x in xrange(len(I)):
            if I[x] == i:
                neighbors.append(J[x])
            if J[x] == i:
                neighbors.append(I[x])

        return neighbors

    def __len__(self):
        A = coo_matrix(self.K.read(), (self.I.read(), self.J.read())).tocsr()
        return(A.shape[0])
        
    def num_edges(self):
        A = coo_matrix(self.K.read(), (self.I.read(), self.J.read()))
        return len(A.nonzero()[0])

    def get_edges(self, data=False):
        I = self.I.read()
        J = self.J.read()
        K = self.K.read()
        if data:
            return zip(I,J,K)
        return zip(I,J)

class HDF5NodeAttributes(object):
    def __init__(self, h5file, pgroup, attributes=None):
        self.h5file = h5file
        self.group = get_or_create_group(h5file, 'nodes', where=pgroup)
        self.fieldgroup = get_or_create_group(h5file, 'fieldgroup', where=self.group)
        self.fields = get_or_create_table(self.h5file, self.group, 'fields',
                                                                    FieldIndex)
        self.field_values = {}

        if 'I' in self.group._v_children.keys():    # Data already exists?
            fieldchildren = self.fieldgroup._v_children.keys()
            for child in fieldchildren:
                carray = get_or_create_array(self.h5file, self.fieldgroup,
                                                          child, None)
                self.field_values[child] = carray
            self.I = get_or_create_array(h5file, self.group, 'I', [])
        else:   # No data in this group.
            # Get the names and types of attribute fields.
            fieldkeys = {}
            mvalues = { 'index': [] }
            for node, attribs in attributes.iteritems():
                for name, value in attribs.iteritems():
                    if name not in mvalues:
                        this_type = str(type(value))
                        fieldkeys[name] = this_type
                        mvalues[name] = []

            # Holds node identifiers.
            indices = sorted(attributes.keys())   # Ensure consistent order.
            self.I = get_or_create_array(h5file, self.group, 'I', indices)

            # Generate attribute vectors.
            for i in indices:
                for name,this_type in fieldkeys.iteritems():
                    if name in attributes[i]:
                        mvalues[name].append(attributes[i][name])
                    else:
                        if this_type == str(type('')): mvalues[name].append('')
                        if this_type == str(type(1)): mvalues[name].append(0)
                        if this_type == str(type(1.1)): mvalues[name].append(0.0)
                        if this_type == str(type(u'')): mvalues[name].append(u'')
                        if this_type == str(type([])): mvalues[name].append(pickle.dumps([]))

            # Generate a fields table.
            for name,this_type in fieldkeys.iteritems():
                query = 'name == b"{0}"'.format(name)
                matches = [ row for row in self.fields.where(query)]
                if len(matches) == 0:
                    fieldentry = self.fields.row
                    fieldentry['name'] = name
                    fieldentry['type'] = this_type
                    fieldentry.append()
            self.fields.flush()

            # Get or create arrays that hold metadata vectors.
            for name in fieldkeys.keys():
                if fieldkeys[name] == str(type([])):
                    mvalues[name] = [ pickle.dumps(v) for v in mvalues[name] ]
                self.field_values[name] = get_or_create_array(self.h5file,
                                                              self.fieldgroup, name,
                                                              mvalues[name])

    def __iter__(self):
        return iter(self.get_nodes())

    def get_nodes(self, data=False):
        nodes = self.I.read()
        if data:
            nodelist = []
            for n in nodes:
                k = list(nodes).index(n)
                attribs = self._get_attributes(k)
                nodelist.append((n,attribs))
            return nodelist
        return nodes
    
    def __len__(self):
        return len(self.I.read())
    
    def _get_attributes(self, k):
        attr_types = { row['name']:row['type'] for row in self.fields }
        attr_names = attr_types.keys()
        attr = {}
        for name in attr_names:
            vals = self.field_values[name].read()
            value = vals[k]
            this_type = attr_types[name]
            if this_type == str(type('')):
                value = str(value)
                if value == '': continue
            if this_type == str(type(1)):
                value = int(value)
                if value == 0: continue
            if this_type == str(type(1.1)):
                value = float(value)
                if value == 0.0: continue
            if this_type == str(type(u'')):
                value = unicode(value)
                if value == u'': continue
            if this_type == str(type([])):
                value = pickle.loads(value)
                if value == []: continue
            attr[name] = value
        return attr

    def __setitem__(self, key, value):
        raise AttributeError('Values can only be set on __init__')

    def __getitem__(self, key):
        """
        For each field in `self.fields` table, retrieve the value for `key`
        from the corresponding attribute vector.
        """

        i = list(self.I.read()).index(key)  # Get the metadata array index.
        fielddata = { row['name']:row['type'] for row in self.fields }
        meta = {}
        for name, type in fielddata.iteritems():
            meta[name] = self._get_meta_entry(name, i, type)

        return meta

    def _get_meta_entry(self, name, index, this_type):
        """
        Retrieve value for `index` from the attribute vector `name`, and
        cast as `type` before returning.
        """
        vals = self.field_values[name].read()
        value = vals[index]
        if this_type == str(type('')): return str(value)
        if this_type == str(type(1)): return int(value)
        if this_type == str(type(1.1)): return float(value)
        if this_type == str(type(u'')): return unicode(value)
        if this_type == str(type([])): return pickle.loads(value)
        return value

