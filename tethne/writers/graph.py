"""
Write NetworkX graphs to structured and unstructured network file formats.

Many methods simply invoke equivalent methods in NetworkX.

.. autosummary::

   to_gexf
   to_graphml
   to_sif

"""

import networkx as nx

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
                        f.write(str(key) + '\n')
                        f.write(str(node_name).replace(" ","_") + " = " +
                                str(value) + "\n")
                else:
                    # not first, append file
                    with open(output_path + "_" + key + ".noa",
                              "a") as f:
                        f.write(str(node_name).replace(" ","_") + " = " +
                                str(value) + "\n")

        if nx.number_of_edges(graph) == 0:
            # write an empty graph to a .sif file (just its nodes)
            for node in nodes:
                node_name = node[0]
                if node == nodes[0]:
                    # first node, overwrite file
                    with open(output_path + ".sif","w") as f:
                        f.write(str(node_name).replace(" ","_") + "\n")
                else:
                    # not first, append file
                    with open(output_path + ".sif","a") as f:
                        f.write(str(node_name).replace(" ","_") + "\n")

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
                    str_attrib = str(attrib)
                    with open(output_path + '_' + str_attrib + ".eda","w") as f:
                        f.write(str(attrib) + "\n")

                # add data to eda files and write sif file
                with open(output_path + '.sif', 'w') as f:
                    for edge in edges:
                        node1 = str(edge[0]).replace(" ", "_")
                        node2 = str(edge[1]).replace(" ", "_")
                        intr_type = str(edge[2]).replace(" ", "_")
                        sif_line = node1 + ' ' + intr_type + ' ' + node2 + '\n'
                        f.write(sif_line)

                        for attrib, value in edge[3].iteritems():
                            eda_line = (node1 + ' (' + intr_type + ') ' +
                                        node2 + ' = ' + str(value) + '\n')
                            with open(output_path + '_' + str(attrib) + '.eda',
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
                    str_attrib = str(attrib)
                    with open(output_path + '_' + str_attrib + ".eda","w") as f:
                        f.write(str(attrib) + "\n")

                # add data to eda files and write sif file
                with open(output_path + '.sif', 'w') as f:
                    for edge in edges:
                        node1 = str(edge[0]).replace(" ", "_")
                        node2 = str(edge[1]).replace(" ", "_")
                        intr_type = 'rel'
                        sif_line = node1 + ' ' + intr_type + ' ' + node2 + '\n'
                        f.write(sif_line)

                        for attrib, value in edge[2].iteritems():
                            eda_line = (node1 + ' (' + intr_type + ') ' +
                                        node2 + ' = ' + str(value) + '\n')
                            with open(output_path + '_' + str(attrib) +
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
    nx.write_gexf(graph, output_path + ".gexf")


def to_graphml(graph, output_path):
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
    nx.write_graphml(graph, output_path + ".graphml")

def to_csv(file, delim=","):
    '''
    Parameters
    ----------
    file : string
        Path to output file (will be created).
    delim : string
        String to use as field delimiter (default is ',').

    Notes
    -----
    TODO: should operate on a (provided) graph. Still uses old library approach.
    '''
    f = open(file, "w")

    # Headers
    f.write("Identifier" + delim + "Title" + delim + "Authors" +
            delim + "WoS Identifier" + delim + "Journal" + delim +
            "Volume" + delim + "Page" + delim + "DOI" + delim +
            "Num Authors\n")
    for entry in self.library:
        # Authors are separated by a colon -> : <-
        authors = ""
        for author in entry.meta['AU']:
            authors += ":" + author
        authors = authors[1:]
        datum = (entry.identifier + delim + entry.meta['TI'][0] +
                 delim + authors + delim + entry.wosid + delim +
                 entry.meta['SO'][0])
        if 'VL' in entry.meta:
            datum += delim + entry.meta['VL'][0]
            if 'BP' in entry.meta:
                datum += delim + entry.meta['BP'][0]
            else:
                datum += delim
        else:
            datum += delim + delim
        if 'DI' in entry.meta:
            datum += delim + entry.meta['DI'][0]
        else:
            datum += delim
        datum += delim + str(entry.meta['num_authors'])
        f.write(datum + "\n")
    f.close()


