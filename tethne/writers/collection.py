"""
Methods for writing :class:`.GraphCollection` to commonly-used network file 
formats. Many methods simply leverage equivalent methods in NetworkX.
"""

import networkx as nx

def to_dxgmml(C, path, delay):
    """
    Writes a :class:`.GraphCollection` to dynamic XGMML.
    
    Parameters
    ----------
    C : :class:`.GraphCollection`
        The :class:`.GraphCollection` to be written to XGMML.
    path : str
        Path to file to be written. Will be created/overwritten.
    delay : int
        Number of years beyond graph index that nodes & edges should persist.
        
    """

    with open(path, "w") as f:
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n')
        f.write('<graph>\n')

        
    
