import networkx as nx

def to_sif(graph, output_path):
    """
    Generates SIF output file from provided graph. 

    See http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats at
    SIF Format for more details

    Edge attribute files appended with .eda contain the values of any edge
    attributes even though the .sif file does not (edge "weights" are
    not supported by .sif)

    Interaction types in the .sif format allow for edge attributes
    that belong to that interaction type. Simple graphs in 
    networkx do not support this kind of edge nesting, but multigraphs do.

    If the graph is a simple graph, it is assumed to have only one interaction
    type named 'rel' short for 'related to' or 'relation'. If the graph is a
    multigraph, each edge has a key which is used as the interaction type
    and has an attribute dictionary associated to that key which is used
    as the interaction type's edge attributes.
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
    """Writes the provided graph to a GEXF-format network file."""
    nx.write_gexf(graph, output_path + ".gexf")


def to_graphml(graph, output_path):
    """Writes the provided graph to a GraphML-format network file."""
    nx.write_graphml(graph, output_path + ".graphml")


def to_xgmml(graph, name, output_path, dynamic=True, nodeattack=0, nodedecay=0, edgeattack=0, edgedecay=0):
    """
    Generates dynamic XGMML output from provided graph.
    
    Parameters
    ----------
    graph : Networkx Graph
    name : string
        Name of the graph.
    output_path : string
        Path to output file, including name ('.xgmml' will be appended).
    dynamic : bool
        If True, will try to include start and end date for nodes and edges.
    nodeattack : int
        For dynamic networks, number of years to prepend to display start.
    nodedecay : int
        For dynamic networks, additional number of years to display node.
    edgeattack : int
        For dynamic networks, number of years to prepend to display start.
    edgedecay : int
        For dynamic networks, additional number of years to display edge.
    
    Raises
    ------
    ValueError
        Raised when dynamic=True and 'date' is not a valid edge attribute in
        graph.

        
    """
    f = open(output_path + ".xgmml", "w")
    f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<graph directed="0"  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.cs.rpi.edu/XGMML">\n\t<att name="selected" value="1" type="boolean" />\n\t<att name="name" value="{0}" type="string"/>\n\t<att name="shared name" value="{0}" type="string"/>\n'.format(name))

    if dynamic:
        node_dates = {}
        date = None
    
    for edge in graph.edges(data=True):
        if dynamic:
            # Update node start/end values.
            if edge[0] not in node_dates.keys():
                node_dates[edge[0]] = { 'start': 3000, 'end': 0 }
            if edge[1] not in node_dates.keys():
                node_dates[edge[1]] = { 'start': 3000, 'end': 0 }


            try:    # First look for explicit start and end dates.
                start = edge[2]['start']
                end = edge[2]['end']
            except KeyError:
                try:
                    start = edge[2]['date']
                    end = edge[2]['date']
                except KeyError:
                    raise ValueError("Missing 'date' in graph edge attributes. Required when dynamic=True.")
                
            if date < node_dates[edge[0]]['start']:
                node_dates[edge[0]]['start'] = start
            if date > node_dates[edge[0]]['end']:
                node_dates[edge[0]]['end'] = end


            if date < node_dates[edge[1]]['start']:
                node_dates[edge[1]]['start'] = start
            if date > node_dates[edge[1]]['end']:
                node_dates[edge[1]]['end'] = end

        try:
            f.write ('\t<edge source="{src}" target="{tgt}" start="{start}" end="{end}">\n'.format(src=edge[0], tgt=edge[1], start=start-edgeattack, end=end+edgedecay).replace('&','&amp;'))
            for key, value in edge[2].iteritems():
                if (type (value).__name__ == "str"):
                    v_type = "string"
                elif (type (value).__name__ == "int"):
                    v_type = "integer"

                f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
            f.write('\t</edge>\n')
        except:
            print edge
    
    for node in graph.nodes(data=True):
        id = node[0]
        node_attributes = dict(node[1])
        if 'label' in node_attributes:
            label = node_attributes['label']
            del node_attributes['label']
        else:
            label = id
        
        if dynamic:
            try:
                start = node_dates[id]['start']
                end = node_dates[id]['end']
            except:
                start = end = 0
        else:
            start = end = 0
#        try:
        f.write('\t<node id="{id}" label="{label}" start="{start}" end="{end}">\n'.format(id=id, label=label, start=start-nodeattack, end=end+nodedecay).replace('&','&amp;'))
        for key, value in node_attributes.iteritems():
            if (type (value).__name__ == "str"):
                v_type = "string"
            elif (type (value).__name__ == "int"):
                v_type = "integer"
            f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
        f.write('\t</node>\n')
#        except:
#            print node
        
    f.write('</graph>')
    
    f.close()


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


