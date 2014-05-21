"""
Classes for building a :class:`.GraphCollection` . 

.. autosummary::

   builder
   authorCollectionBuilder
   paperCollectionBuilder

"""

import networkx as nx
import tethne.networks as nt
import tethne.readers as rd
from tethne.data import GraphCollection, DataCollection
import types

class DCBuilder(object):
    """
    Base class for DataCollection builders.
    """
    
    def __init__(self, datapath):
        """
        
        Parameters
        ----------
        datapath : str
            Path to data.
        """

        self.datapath = datapath
        
class DFRBuilder(DCBuilder):
    """
    DataCollection builder for JSTOR Data-for-Research datasets.
    """
    
    def build(self, grams=['uni'], slice_by=['date',], **kwargs):
        """
        
        Parameters
        ----------
        grams : list or tuple
            N-grams that should be read from the DfR dataset.
        apply_stoplist : bool
            If True, will exclude all N-grams that contain words in the NLTK
            stoplist.
        slice_by : list or tuple
            Keys in :class:`.Paper` by which to slice data.
        """
            
        # Load papers.
        papers = rd.dfr.read(self.datapath)

        # Load N-grams.
        gram_data = {}
        for gram_type in grams:
            g = rd.dfr.ngrams(self.datapath, 
                                        N=gram_type)
            g_tok, vocab, counts = rd.dfr.tokenize(g)                                        
            gram_data[gram_type] = (g_tok, vocab, counts)
        
        # Create DataCollection.
        D = DataCollection(papers, grams=gram_data, index_by='doi')
        
        # Slice DataCollection.
        kw = { 'method': kwargs.get('method', 'time_window'),
               'window_size': kwargs.get('window_size', 4),
               'step_size': kwargs.get('step_size', 1) }

        for axis in slice_by:
            D.slice(axis, **kw)
        
        return D
        

class GCBuilder(object):
    """
    Base class for GraphCollection builders.
    """

    def __init__(self, D):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        """

        self.D = D

class paperCollectionBuilder(GCBuilder):
    """
    Builds a :class:`.GraphCollection` with method in 
    :mod:`tethne.networks.papers` from a :class:`.DataCollection` .
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
           >>> from tethne.builders import paperCollectionBuilder
           >>> builder = paperCollectionBuilder(D)
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
        
class topicCollectionBuilder(GCBuilder):
    """
    Builds a :class:`.GraphCollection` with method in
    :mod:`tethne.networks.topics` from a :class:`.DataCollection` .
    """
    
#    def __init__(self, D, model=None):
#        super(topicCollectionBuilder, self).__init__(D)
#        self.model = model
    
    def build(self, graph_axis, graph_type, **kwargs):
        """
        Generates a graph for each slice along graph_axis in
        :class:`.DataCollection` D.
        
        Other axes in D are treated as attributes.
        """
        
        if self.D.model is None:
            raise RuntimeError('No corpus model in this DataCollection')
        
        C = GraphCollection()
        
        for key in sorted(self.D.axes[graph_axis].keys()):
            pids = self.D.axes[graph_axis][key]
            data = [ self.D.data[p] for p in pids ]
            papers = [ self.D.model.lookup[p] for p in pids ]
            C[key] = nt.topics.__dict__[graph_type](self.D.model, papers=papers, **kwargs)
            print key, len(papers), len(C[key].edges())
        
        return C

class authorCollectionBuilder(GCBuilder):
    """
    Builds a :class:`.GraphCollection` with method in 
    :mod:`tethne.networks.authors` from a :class:`.DataCollection` .
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
           >>> from tethne.builders import authorCollectionBuilder
           >>> builder = authorCollectionBuilder(D)
           >>> C = builder.build('date', 'coauthors')
           >>> C
           <tethne.data.GraphCollection at 0x104ed3550>
           
           """
        
        # TODO: Check to make sure we have the right stuff.
        
        C = GraphCollection()
        
        # Build a Graph for each slice.
        for key, pids in self.D.axes[graph_axis].iteritems():
            data = [ self.D.data[p] for p in pids ]
            C[key] = nt.authors.__dict__[graph_type](data, **kwargs)

        return C    