import networkx as nx

def to_sif(graph, output_path):
    """
    Generates SIF output file from provided graph. 

    See http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats at
        SIF Format for more details

    Edge attribute files appended with .eda contain the values of any edge
        attributes even though the .sif file does not (edge "weights" are
        not supported by .sif)
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
            edges = graph.edges(data=True)
            for edge in edges:
                node1 = str(edge[0]).replace(" ","_")
                node2 = str(edge[1]).replace(" ","_")
                edge_attribs = edge[2]
                for key, value in edge_attribs.iteritems():
                    # generate an edge attribute file for each edge attribute
                    if edge == edges[0]:
                        # first edge, overwrite file
                        with open(output_path + "_" + key + 
                                  ".eda","w") as f:
                            f.write(node1 + " " +  key + " " + node2 + 
                                    " = " + str(value) + "\n")
                    else:
                        # not first, append file
                         with open(output_path + "_" + key + 
                                  ".eda","a") as f:
                            f.write(node1 + " " +  key + " " + node2 + 
                                    " = " + str(value) + "\n")

                    # generate the .sif file
                    if edge == edges[0]:
                        # first edge, overwrite file
                        with open(output_path + ".sif","w") as f:
                            f.write(node1 + " " + key + " " + node2 + "\n")
                    else:
                        # not first, append file
                        with open(output_path + ".sif","a") as f:
                            f.write(node1 + " " + key + " " + node2 + "\n")
 

def to_gexf(graph, output_path):
    """Writes the provided graph to a GEXF-format network file."""
    nx.write_gexf(graph, output_path + ".gexf")


def to_graphml(graph, output_path):
    """Writes the provided graph to a GraphML-format network file."""
    nx.write_graphml(graph, output_path + ".graphml")


def to_xgmml(graph, name, output_path):
    """
    Generates dynamic XGMML output from provided graph.
    """
    f = open(output_path + ".xgmml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<graph directed="0"  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.cs.rpi.edu/XGMML">\n\t<att name="selected" value="1" type="boolean" />\n\t<att name="name" value="{0}" type="string"/>\n\t<att name="shared name" value="{0}" type="string"/>\n'.format(name))
    
    for node in graph.nodes(data=True):
        id = node[0]
        node_attributes = dict(node[1])
        if 'label' in node_attributes:
            label = node_attributes['label']
            del node_attributes['label']
        else:
            label = id
            
        if 'year' in node_attributes:
            start = node_attributes['year']
        else:
            start = 1900
        
        f.write('\t<node id="{id}" label="{label}" start="{start}">\n'.format(id=id, label=label, start=start).replace('&','&amp;'))
        for key, value in node_attributes.iteritems():
            if (type (value).__name__ == "str"):
                v_type = "string"
            elif (type (value).__name__ == "int"):
                v_type = "integer"
            f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
        f.write('\t</node>\n')
        
    for edge in graph.edges(data=True):
        f.write ('\t<edge source="{}" target="{}">\n'.format(edge[0], edge[1]).replace('&','&amp;'))
        for key, value in edge[2].iteritems():
            if (type (value).__name__ == "str"):
                v_type = "string"
            elif (type (value).__name__ == "int"):
                v_type = "integer"

            f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
        f.write('\t</edge>')
    f.write('</graph>')
    
    f.close()


def to_csv(file, format, delim):
    f = open(file, "w")
    if format is "csv":
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


