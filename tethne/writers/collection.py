"""
Write :class:`.GraphCollection` to a structured data format.

.. autosummary::

   to_dxgmml
   
"""

import networkx as nx
import pickle as pk

def to_dxgmml(C, path): # [#61510094]
    """
    Writes a :class:`.GraphCollection` to 
    `dynamic XGMML. <https://code.google.com/p/dynnetwork/wiki/DynamicXGMML>`_.
    
    Dynamic XGMML is a schema for describing dynamic networks in Cytoscape 3.0.
    This method assumes that `Graph` indices are orderable points in time 
    (e.g. years). The "start" and "end" of each node and edge are determined by 
    periods of consecutive appearance in the :class:`.GraphCollection` . Node 
    and edge attributes are defined for each `Graph`. in the 
    :class:`.GraphCollection`.
    
    For example, to build and visualize an evolving co-citation network:
    
    .. code-block:: python

       >>> # Load some data.
       >>> import tethne.readers as rd
       >>> papers = rd.wos.read(datapath)

       >>> # Build a DataCollection, and slice it temporally using a
       >>> #  4-year sliding time-window.
       >>> from tethne.data import DataCollection, GraphCollection
       >>> D = DataCollection(papers)
       >>> D.slice('date', 'time_window', window_size=4)

       >>> # Generate a GraphCollection of co-citation graphs.
       >>> from tethne.builders import paperCollectionBuilder
       >>> builder = paperCollectionBuilder(D)
       >>> C = builder.build('date', 'cocitation', threshold=2)

       >>> # Write the GraphCollection as a dynamic network.
       >>> import tethne.writers as wr
       >>> wr.collection.to_dxgmml(C, "/path/to/network.xgmml")
    
    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to be written to XGMML.
    path : str
        Path to file to be written. Will be created/overwritten.
        
    Raises
    ------
    AttributeError
        C must be a tethne.classes.GraphCollection.

    Notes
    -----
    Period start and end dates in this method are inclusive, whereas XGMML end
    dates are exclusive. Hence +1 is added to all end dates when writing XGMML.
    """
    
    if type(C) is not tethne.classes.GraphCollection:
        raise AttributeError('C must be a tethne.classes.GraphCollection.')

    nodes = {}
    for n in C.nodes():
        nodes[n] = { 'periods' : [] }   # Each period will be a dict with
                                        #  'start' and 'end' values.
    edges = {}
    for e in C.edges():
        edges[e] = { 'periods' : [] }

    # Build node list.
    current = []
    for k in sorted(C.graphs.keys()):
        G = _strip_list_attributes(C[k])
        preceding = current
        current = []
        for n in G.nodes(data=True):
            if n[0] not in preceding:   # Looking for gaps in presence of node.
                nodes[n[0]]['periods'].append( { 'start': k, 'end': k } )
            else:
                if k > nodes[n[0]]['periods'][-1]['end']:
                    nodes[n[0]]['periods'][-1]['end'] = k
            current.append(n[0])

            nodes[n[0]][k] = {}
            for attr, value in n[1].iteritems():
                if type(value) is str:
                    value = value.replace("&", "&amp;").replace('"', '')
                nodes[n[0]][k][attr] = value

    # Build edge list.
    current = []
    for k in sorted(C.graphs.keys()):
        G = _strip_list_attributes(C[k])
        preceding = current
        current = []
        for e in G.edges(data=True):
            e_key = (e[0], e[1])
            if e_key not in preceding:   # Looking for gaps in presence of edge.
                edges[e_key]['periods'].append( { 'start': k, 'end': k } )
            else:
                if k > edges[e_key]['periods'][-1]['end']:
                    edges[e_key]['periods'][-1]['end'] = k
            current.append(e_key)

            edges[e_key][k] = {}
            for attr, value in e[2].iteritems():
                if type(value) is str:
                    value = value.replace("&", "&amp;").replace('"', '')
                edges[e_key][k][attr] = value

    # Write graph to XGMML.
    xst = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'
    
    sg = '<graph>\n'
    eg = '</graph>'
    
    nst = '\t<node label="{0}" id="{0}" start="{1}" end="{2}">\n'
    ast = '\t\t<att name="{0}" type="{1}" value="{2}" start="{3}" end="{4}"/>\n'
    enn = '\t</node>\n'
    
    est = '\t<edge source="{0}" target="{1}" start="{2}" end="{3}">\n'
    eas = '\t\t<att name="{0}" type="{1}" value="{2}" start="{3}" end="{4}"/>\n'
    ene = '\t</edge>\n'
    
    with open(path, "w") as f:
        f.write(xst)    # xml element.
        f.write(sg)     # Graph element.
        for n in nodes.keys():
            for period in nodes[n]['periods']:
                label = str(n).replace("&", "&amp;").replace('"', '')
                
                # Node element.
                f.write(nst.format(label, period['start'], period['end']+1))

                for i in sorted(nodes[n].keys()):
                    if period['start'] <= i <= period['end']:
                        for attr, value in nodes[n][i].iteritems():
                            # Type names are slightly different in XGMML.
                            dtype = _safe_type(value)
                            attr = str(attr).replace("&", "&amp;")

                            # Node attribute element.
                            f.write(ast.format(attr, dtype, value, i, i+1))
            
                f.write(enn)    # End node element.

        for e in edges.keys():
            for period in edges[e]['periods']:
                src = str(e[0]).replace("&", "&amp;").replace('"', '')
                tgt = str(e[1]).replace("&", "&amp;").replace('"', '')
                start = period['start']
                end = period['end'] + 1
                
                # Edge element.
                f.write(est.format(src, tgt, start, end))

                for i in sorted(edges[e].keys()):
                    if period['start'] <= i <= period['end']:
                        for attr, value in edges[e][i].iteritems():
                            # Type names are slightly different in XGMML.
                            dtype = _safe_type(value)
                            
                            # Edge attribute element.
                            f.write(eas.format(attr, dtype, value, i, i+1)
                                       .replace("&", "&amp;"))
            
                f.write(ene)    # End edge element.
        f.write(eg) # End graph element.
        
def _strip_list_attributes(G):
    """Converts lists attributes to strings for all nodes and edges in G."""
    for n in G.nodes(data=True):
        for k,v in n[1].iteritems():
            if type(v) is list:
                G.node[n[0]][k] = str(v)
    for e in G.edges(data=True):
        for k,v in e[2].iteritems():
            if type(v) is list:
                G.edge[e[0]][e[1]][k] = str(v)

    return G        

def _safe_type(value):
    """Converts Python type names to XGMML-safe type names."""
    if type(value) is str: dtype = 'string'
    if type(value) is int: dtype = 'integer'
    if type(value) is float: dtype = 'real'