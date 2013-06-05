import networkx as nx

def to_sif(graph, output_path, output_name):
    """
    Generates SIF output file from provided graph. 

    See http://wiki.cytoscape.org/Cytoscape_User_Manual/Network_Formats at
        SIF Format for more details

    Edge attribute files appended with .eda contain the values of any edge
        attributes even though the .sif file does not (edge "weights" are
        not supported by .sif)

    Test cases:
    No nodes
    Nodes but no edges (n nodes)
    Nodes and edges (n nodes)
    """
    if nx.number_of_nodes(graph) == 0:
        # write an empty file (for a non-existant graph)
        f = open(output_path + output_name + ".sif","w")
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
                    with open(output_path + output_name + "_" + key + ".noa",
                              "w") as f:
                        f.write(str(node_name).replace(" ","_") + " = " + 
                                str(value) + "\n")
                else:
                    # not first, append file
                    with open(output_path + output_name + "_" + key + ".noa",
                              "a") as f:
                        f.write(str(node_name).replace(" ","_") + " = " + 
                                str(value) + "\n")

        if nx.number_of_edges(graph) == 0:
            # write an empty graph to a .sif file (just its nodes) 
            for node in nodes:
                node_name = node[0]
                if node == nodes[0]:
                    # first node, overwrite file
                    with open(output_path + output_name + ".sif","w") as f:
                        f.write(str(node_name).replace(" ","_") + "\n")
                else:
                    # not first, append file
                    with open(output_path + output_name + ".sif","a") as f:
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
                        with open(output_path + output_name + "_" + key + 
                                  ".eda","w") as f:
                            f.write(node1 + " " +  key + " " + node2 + 
                                    " = " + str(value) + "\n")
                    else:
                        # not first, append file
                         with open(output_path + output_name + "_" + key + 
                                  ".eda","a") as f:
                            f.write(node1 + " " +  key + " " + node2 + 
                                    " = " + str(value) + "\n")

                    # generate the .sif file
                    if edge == edges[0]:
                        # first edge, overwrite file
                        with open(output_path + output_name + ".sif","w") as f:
                            f.write(node1 + " " + key + " " + node2 + "\n")
                    else:
                        # not first, append file
                        with open(output_path + output_name + ".sif","a") as f:
                            f.write(node1 + " " + key + " " + node2 + "\n")
 

