from collectionmanager import CollectionManager
from .. import networks as nt
from ..classes import GraphCollection
from ..writers.collection import to_dxgmml

class GraphCollectionManager(CollectionManager):
    """
    Base class for GraphCollection managers.
    """

    def __init__(self, sourcecollection, **kwargs):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        """
        super(GraphCollectionManager, self).__init__(**kwargs)

        self.sourcecollection = sourcecollection

class GenericGraphCollectionManager(GraphCollectionManager):
    """
    """
    
    def __init__(self, sourcecollection, graph_axis, node_type, graph_type,
                                                    method_kwargs={}, **kwargs):
        super(GenericGraphCollectionManager, self).__init__(sourcecollection,
                                                                       **kwargs)
    
        self.graph_axis = graph_axis
        self.graph_type = graph_type
        self.node_type = node_type
        self.method_kwargs = method_kwargs
    
    def prep(self):
        self.method = nt.__dict__[self.node_type].__dict__[self.graph_type]

    def build(self):
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
           >>> from tethne.builders import paperCollectionBuilder
           >>> builder = paperCollectionBuilder(D)
           >>> C = builder.build('date', 'bibliographic_coupling', threshold=2)
           >>> C
           <tethne.data.GraphCollection at 0x104ed3550>
           
           """
        
        self.C = GraphCollection()
        
        # Build a Graph for each slice.
        for key, pids in self.sourcecollection.axes[self.graph_axis].iteritems():
            data = [ self.sourcecollection.papers[p] for p in pids ]
            self.method_kwargs['node_attribs'] = self.sourcecollection.get_axes()
            self.method_kwargs['node_id'] = self.sourcecollection.index_by
            self.C[key] = self.method(data, **self.method_kwargs)

        return self.C

    def write(self):
        to_dxgmml(self.C, './testout.xgmml')
