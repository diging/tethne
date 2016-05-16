"""
Write NetworkX graphs to structured and unstructured network file formats.

.. autosummary::

   write_csv
   write_graphml

"""

import networkx as nx
from networkx.readwrite.graphml import GraphMLWriter
import csv
import warnings
from itertools import repeat

from xml.etree.cElementTree import Element, ElementTree, tostring

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


def write_csv(graph, prefix):
    """
    Write ``graph`` as tables of nodes (``prefix-nodes.csv``) and edges
    (``prefix-edges.csv``).

    Parameters
    ----------
    graph : :class:`networkx.Graph`
    prefix : str
    """
    node_headers = list(set([a for n, attrs in graph.nodes(data=True)
                             for a in attrs.keys()]))
    edge_headers = list(set([a for s, t, attrs in graph.edges(data=True)
                             for a in attrs.keys()]))

    value = lambda attrs, h: _recast_value(attrs[h]) if h in attrs else ''
    with open(prefix + '_nodes.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['node'] + node_headers)
        for n, attrs in graph.nodes(data=True):
            values = map(value, repeat(attrs, len(node_headers)), node_headers)
            writer.writerow([_recast_value(n)] + list(values))

    with open(prefix + '_edges.csv', 'w') as f:
        writer = csv.writer(f)
        writer.writerow(['source', 'target'] + edge_headers)
        for s, t, attrs in graph.edges(data=True):
            values = map(value, repeat(attrs, len(edge_headers)), edge_headers)
            writer.writerow([_recast_value(s), _recast_value(t)] + list(values))


def to_sif(graph, output_path):
    """
    Generates Simple Interaction Format output file from provided graph.

    The SIF specification is described
    `here <http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats>`_.

    :func:`.to_sif` will generate a .sif file describing the network, and a few
    .eda and .noa files containing edge and node attributes, respectively. These
    are equivalent to tab-delimited tables, and can be imported as such in
    Cytoscape 3.0.

    Parameters
    ----------
    graph : networkx.Graph
        The Graph to be exported to SIF.
    output_path : str
        Full path, including filename (without suffix).
        e.g. using "./graphFolder/graphFile" will result in a SIF file at
        ./graphFolder/graphFile.sif, and corresponding .eda and .noa files.

    """

    warnings.warn("Removed in 0.8. Use write_csv instead.", DeprecationWarning)

    graph = _strip_list_attributes(graph)

    if output_path[-4:] == ".sif":
        output_path = output_path[:-4]

    if nx.number_of_nodes(graph) == 0:
        # write an empty file (for a non-existant graph)
        f = open(output_path + ".sif","w")
        f.write("")
        f.close()

    else:
        # write node files
        nodes = graph.nodes(data=True)
        for node in nodes:
            node_name = node[0]
            node_attribs = node[1]
            for key, value in node_attribs.iteritems():
                # generate a node attribute file for each node attribute
                if node == nodes[0]:
                    # first node, overwrite file
                    with open(output_path + "_" + key + ".noa",
                              "w") as f:
                        f.write(unicode(key) + '\n')
                        f.write(unicode(node_name).replace(" ","_") + " = " +
                                unicode(value) + "\n")
                else:
                    # not first, append file
                    with open(output_path + "_" + key + ".noa",
                              "a") as f:
                        f.write(unicode(node_name).replace(" ","_") + " = " +
                                unicode(value) + "\n")

        if nx.number_of_edges(graph) == 0:
            # write an empty graph to a .sif file (just its nodes)
            for node in nodes:
                node_name = node[0]
                if node == nodes[0]:
                    # first node, overwrite file
                    with open(output_path + ".sif","w") as f:
                        f.write(unicode(node_name).replace(" ","_") + "\n")
                else:
                    # not first, append file
                    with open(output_path + ".sif","a") as f:
                        f.write(unicode(node_name).replace(" ","_") + "\n")

        else:
            # write the graph to a .sif file as well as other edge
            # attribute files

            if graph.is_multigraph():
                # then the NetworkX graph supports multiple interaction
                # types just like the .sif format
                edges = graph.edges(data=True, keys=True)
                edge_attribs = set()
                for edge in edges:
                    for key in edge[3].iterkeys():
                        edge_attribs.add(key)

                # create edge attribute files
                for attrib in edge_attribs:
                    str_attrib = unicode(attrib)
                    with open(output_path + '_' + str_attrib + ".eda","w") as f:
                        f.write(unicode(attrib) + "\n")

                # add data to eda files and write sif file
                with open(output_path + '.sif', 'w') as f:
                    for edge in edges:
                        node1 = unicode(edge[0]).replace(" ", "_")
                        node2 = unicode(edge[1]).replace(" ", "_")
                        intr_type = unicode(edge[2]).replace(" ", "_")
                        sif_line = node1 + ' ' + intr_type + ' ' + node2 + '\n'
                        f.write(sif_line)

                        for attrib, value in edge[3].iteritems():
                            eda_line = (node1 + ' (' + intr_type + ') ' +
                                        node2 + ' = ' + unicode(value) + '\n')
                            with open(output_path + '_' + unicode(attrib) + '.eda',
                                      'a') as g:
                                g.write(eda_line)

            else:
                # then we support only one interaction type 'rel'
                edges = graph.edges(data=True)
                edge_attribs = set()
                for edge in edges:
                    for key in edge[2].iterkeys():
                        edge_attribs.add(key)

                # create edge attribute files
                for attrib in edge_attribs:
                    str_attrib = unicode(attrib)
                    with open(output_path + '_' + str_attrib + ".eda","w") as f:
                        f.write(unicode(attrib) + "\n")

                # add data to eda files and write sif file
                with open(output_path + '.sif', 'w') as f:
                    for edge in edges:
                        node1 = unicode(edge[0]).replace(" ", "_")
                        node2 = unicode(edge[1]).replace(" ", "_")
                        intr_type = 'rel'
                        sif_line = node1 + ' ' + intr_type + ' ' + node2 + '\n'
                        f.write(sif_line)

                        for attrib, value in edge[2].iteritems():
                            eda_line = (node1 + ' (' + intr_type + ') ' +
                                        node2 + ' = ' + unicode(value) + '\n')
                            with open(output_path + '_' + unicode(attrib) +
                                      '.eda', 'a') as g:
                                g.write(eda_line)


def to_gexf(graph, output_path):
    """Writes graph to `GEXF <http://gexf.net>`_.

    Uses the NetworkX method
    `write_gexf <http://networkx.lanl.gov/reference/generated/networkx.readwrite.gexf.write_gexf.html>`_.

    Parameters
    ----------
    graph : networkx.Graph
        The Graph to be exported to GEXF.
    output_path : str
        Full path, including filename (without suffix).
        e.g. using "./graphFolder/graphFile" will result in a GEXF file at
        ./graphFolder/graphFile.gexf.
    """
    warnings.warn("Removed in 0.8.", DeprecationWarning)

    graph = _strip_list_attributes(graph)

    nx.write_gexf(graph, output_path + ".gexf")


def write_graphml(graph, path, encoding='utf-8', prettyprint=True):
    """Writes graph to `GraphML <http://graphml.graphdrawing.org/>`_.

    Uses the NetworkX method
    `write_graphml <http://networkx.lanl.gov/reference/generated/networkx.readwrite.graphml.write_graphml.html>`_.

    Parameters
    ----------
    graph : networkx.Graph
        The Graph to be exported to GraphML.
    output_path : str
        Full path, including filename (without suffix).
        e.g. using "./graphFolder/graphFile" will result in a GraphML file at
        ./graphFolder/graphFile.graphml.
    """
    graph = _strip_list_attributes(graph)

    writer = TethneGraphMLWriter(encoding=encoding, prettyprint=prettyprint)
    writer.add_graph_element(graph)
    writer.dump(open(path, 'wb'))


def to_graphml(graph, path, encoding='utf-8', prettyprint=True):
    warnings.warn("Removed in 0.8. Use write_graphml instead.",
                  DeprecationWarning)

    write_graphml(graph, path, encoding=encoding, prettyprint=prettyprint)


class TethneGraphMLWriter(GraphMLWriter):
    def get_key(self, name, attr_type, scope, default):
        # Modified to use attribute name as key, rather than numeric ID.
        keys_key = (name, attr_type, scope)
        try:
            return self.keys[keys_key]
        except KeyError:
            new_id = name
            self.keys[keys_key] = new_id
            key_kwargs = {"id": new_id,
                          "for": scope,
                          "attr.name": name,
                          "attr.type": attr_type}
            key_element = Element("key", **key_kwargs)
            # add subelement for data default value if present
            if default is not None:
                default_element = Element("default")
                default_element.text = _recast_value(default)
                key_element.append(default_element)
            self.xml.insert(0, key_element)
        return new_id

    def add_data(self, name, e_type, value, scope="all", default=None):
        if e_type not in self.xml_type:
            raise nx.NetworkXError('GraphML writer does not support '
                                   '%s as data values.'%e_type)
        key_id = self.get_key(name, self.xml_type[e_type], scope, default)
        data_element = Element("data", key=key_id)
        data_element.text = _recast_value(value)
        return data_element

    def add_nodes(self, G, graph_element):
        for node,data in G.nodes_iter(data=True):
            node_element = Element("node", id=_recast_value(node))
            default = G.graph.get('node_default', {})
            self.add_attributes("node", node_element, data, default)
            graph_element.append(node_element)

    def add_edges(self, G, graph_element):
        if G.is_multigraph():
            for u,v,key,data in G.edges_iter(data=True, keys=True):
                edge_element = Element("edge",source=_recast_value(u),
                                       target=_recast_value(v))
                default = G.graph.get('edge_default',{})
                self.add_attributes("edge", edge_element, data, default)
                self.add_attributes("edge", edge_element, {'key': key},
                                    default)
                graph_element.append(edge_element)
        else:
            for u,v,data in G.edges_iter(data=True):
                edge_element = Element("edge", source=_recast_value(u),
                                       target=_recast_value(v))
                default = G.graph.get('edge_default', {})
                self.add_attributes("edge", edge_element, data, default)
                graph_element.append(edge_element)


def to_table(graph, path):
    warnings.warn("Removed in 0.8. Use write_csv instead.",
                  DeprecationWarning)

    graph = _strip_list_attributes(graph)

    # Edge list.
    with open(path + "_edges.csv", "wb") as f:
        edges = graph.edges(data=True)
        writer = csv.writer(f, delimiter='\t')

        # Header.
        writer.writerow(['source','target'] + [ k for k in edges[0][2].keys()])

        # Values.
        for e in edges:
            writer.writerow([ e[0], e[1]] + [ v for v in e[2].values() ] )

    # Node attributes.
    with open(path + "_nodes.csv", "wb") as f:
        nodes = graph.nodes(data=True)
        writer = csv.writer(f, delimiter='\t')

        # Header.
        writer.writerow(['node'] + [ k for k in nodes[0][1].keys() ])

        # Values.
        for n in nodes:
            writer.writerow([ n[0] ] + [ v for v in n[1].values() ])


def _strip_list_attributes(G):
    for n in G.nodes(data=True):
        for k,v in n[1].iteritems():
            if type(v) is list:
                G.node[n[0]][k] = unicode(v)
    for e in G.edges(data=True):
        for k,v in e[2].iteritems():
            if type(v) is list:
                G.edge[e[0]][e[1]][k] = unicode(v)

    return G


def _recast_value(value):
    if type(value) in [str, int, unicode, float]:
        return unicode(value)
    if hasattr(value, '__iter__'):
        return ', '.join(list(value))
