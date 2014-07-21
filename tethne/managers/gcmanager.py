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
        D : :class:`.Corpus`
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
        pass
    
    def build(self):
        """
        Generates a graph for each slice of a :class:`.Corpus`.
        """
        
        self.C = GraphCollection()
        
        self.C.build(self.sourcecollection, self.graph_axis, self.node_type,
                                            self.graph_type, self.method_kwargs)
        return C

    def write(self):
        to_dxgmml(self.C, './testout.xgmml')
