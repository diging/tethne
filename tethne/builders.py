import networkx as nx
import tethne.networks as nt
import tethne.data as dt
import types

class builder(object):
    """Base class for builders."""
    
    def __init__(self, data):
        self.data = data
        
class graphCollectionBuilder(builder):
    """
    Builds a :class:`.GraphCollection` from a list of :class:`.Paper`
    instances.
    """
    
    def build(self, method, graph_type, graph_args={}, **kwargs):
        """
        Yields a :class:`.GraphCollection` .
        
        Parameters
        ----------
        method : string
            See table below for available methods (to be extended).
        graph_type : string
            The name of a method from :mod:`tethne.networks.papers`
        graph_args : dict
            Arguments passed to graph_type method as kwargs.
        kwargs : kwargs
            See methods table, below.

        Returns
        -------
        C : :class:`.GraphCollection`
        
        Notes
        -----

        Methods available for building GraphCollections:
        
        ===========    ========================================    =============
        Method         Description                                 kwargs
        ===========    ========================================    =============
        time_window    Slices data using a sliding time-window,    window_size
                       and builds a 
                       :class:`.nx.classes.graph.Graph` from 
                       each slice. Graphs are indexed using the 
                       start of the time-window.
        time_period    Slices data into time periods of equal      window_size
                       length, and builds a                        step_size
                       :class:`.nx.classes.graph.Graph` from 
                       each slice. Graphs are indexed using the 
                       start of the time period. 
        ===========    ========================================    =============
        
        Avilable kwargs:
        
        ===========    ======   ================================================
        Argument       Type     Description
        ===========    ======   ================================================
        window_size    int      Size of time-window or period, in years 
                                (default = 1).
        step_size      int      Amount to advance time-window or period in each
                                step (ignored for time_period).
        ===========    ======   ================================================
        """
        
        # Does the graph method exist?
        if type(nt.papers.__dict__[graph_type]) is not types.FunctionType:
            raise ValueError("No such function in tethne.networks.papers")
            
        C = dt.GraphCollection()
        
        # Slice the data using specified method.
        if method == 'time_window':
            kw = {  'window_size': kwargs.get('window_size', 1),
                    'step_size': 1 }
            
            self._time_slice(**kw)
            
        elif method == 'time_period':
            kw = {  'window_size': kwargs.get('window_size', 1),
                    'step_size': kwargs.get('window_size', 1) }
            
            self._time_slice(**kw)
            
        # Build a Graph for each slice.
        for key, data in self.slices.iteritems():
            C[key] = nt.papers.__dict__[graph_type](data, **graph_args)
        
        return C
    
    def _time_slice(self, **kwargs):
        """
        Slices data into subsets by date. 
        
        If step_size = 1, this is a sliding time-window. If step_size = 
        window_size, this is a time period slice.
        """
        
        window_size = kwargs.get('window_size', 1)
        step_size = kwargs.get('step_size', 1)
        start = kwargs.get('start', min([ p['date'] for p in self.data ]))
        end = kwargs.get('start', max([ p['date'] for p in self.data ]))
        
        self.slices = {}
        for i in xrange(start, end-window_size+2, step_size):
            self.slices[i] = [ p for p in self.data 
                                if i <= p['date'] < i + window_size ]
                                
if __name__ == '__main__':
    import tethne.readers as rd
    papers = rd.wos.read("/Users/erickpeirson/Dropbox/DigitalHPS/Davidson Collaborators/Web of Science/A.E. MIrsky/savedrecs.txt")
    
    b = graphCollectionBuilder(papers)
    C = b.build('time_window', 'bibliographic_coupling', window_size=5) # 'cocitation', { 'threshold': 2 },
    print [len(G) for G in  C.graphs.values() ]
    
    print len(nt.papers.bibliographic_coupling(papers))