import networkx as nx
import tethne.networks as nt
from tethne.data import GraphCollection
import types

class builder(object):
    """Base class for builders."""

    def __init__(self, D):
        self.D = D

class graphCollectionBuilder(builder):
    """
    Builds a :class:`.GraphCollection` from a :class:`.DataCollection` .
    """

    def build(self, graph_axis, graph_type, **kwargs):
        """
        Generates graphs for each slice along graph_axis in
        :class:`.DataCollection` D.
        
        Other axes in D are treated as attributes.
        
        **Usage**
    
        .. code-block:: python

           >>> import tethne.readers as rd
           >>> data = rd.wos.read("/Path/to/wos/data.txt")
           >>> from tethne.data import DataCollection
           >>> D = DataCollection(data) # Indexed by wosid, by default.
           >>> D.slice('date', 'time_window', window_size=4)
           >>> from tethne.builders import graphCollectionBuilder
           >>> builder = graphCollectionBuilder(D)
           >>> C = builder.build('date', 'bibliographic_coupling', threshold=2)
           >>> C
           <tethne.data.GraphCollection at 0x104ed3550>
           
           """
        
        # TODO: Check to make sure we have the right stuff.
        
        C = GraphCollection()
        
        # Build a Graph for each slice.
        for key, pids in self.D.axes[graph_axis].iteritems():
            data = [ self.D.data[p] for p in pids ]
            kwargs['node_attribs'] = self.D.get_axes()
            kwargs['node_id'] = self.D.index_by
            C[key] = nt.papers.__dict__[graph_type](data, **kwargs)

        return C
