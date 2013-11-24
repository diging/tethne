import types
import networkx as nx

class Paper():
    """
    Base class for Papers. Behaves just like a dict, but enforces a limited 
    vocabulary of keys, and specific data types.
    
    Notes
    -----
    The following fields (and corresponding data types) are allowed:
    
    * aulast (list) -- Authors' last name, as a list.
    * auinit (list) -- Authors' first initial as a list.
    * institution (dict) -- Institutions with which the authors are affiliated.
    * atitle (str) -- Article title.
    * jtitle (str) -- Journal title or abbreviated title.
    * volume (str) -- Journal volume number.
    * issue (str) -- Journal issue number.
    * spage (str) -- Starting page of article in journal.
    * epage (str) -- Ending page of article in journal.
    * date (int) -- Article date of publication.
    * country (dict) -- Author-Country mapping.
    * citations (list) -- A list of :class:`.Paper` instances.
    * ayjid (str) -- First author's name (last, fi), pub year, and journal.
    * doi (str) -- Digital Object Identifier.
    * pmid (str) -- PubMed ID.
    * wosid (str) -- Web of Science UT fieldtag value.
    
    None values are also allowed for all fields.
    """
    
    def __init__(self):
        """
        Defines keys, and acceptable data types for values.
        """
        self.meta_dict = {
                            'aulast':None,
                            'auinit':None,
                            'institutions':None,
                            'atitle':None,
                            'jtitle':None,
                            'volume':None,
                            'issue':None,
                            'spage':None,
                            'epage':None,
                            'date':None,
                            'citations':None,
                            'country':None,
                            'ayjid':None,
                            'doi':None,
                            'pmid':None,
                            'wosid':None    }
    
        self.list_fields = [ 'aulast', 
                             'auinit', 
                             'citations' ]
        
        self.string_fields = [ 'atitle', 
                               'jtitle', 
                               'volume', 
                               'issue', 
                               'spage', 
                               'epage', 
                               'ayjid', 
                               'doi', 
                               'pmid', 
                               'wosid' ]
        
        self.int_fields = [ 'date' ]
        
        self.dict_fields = [ 'institutions' ]
    
    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys, and acceptable data types for
        values.
        """
        
        if key not in self.meta_dict.keys():
            raise KeyError(str(key) + " is not a valid key in Paper meta_dict.")
        elif key in self.list_fields and type(value) is not list and value is not None:
                raise ValueError("Value for field '"+str(key)+"' must be a list.")
        elif key in self.string_fields and type(value) is not str and value is not None:
                raise ValueError("Value for field '"+str(key)+"' must be a string.")
        elif key in self.int_fields and type(value) is not int and value is not None:
                raise ValueError("Value for field '"+str(key)+"' must be an integer.")   
        elif key in self.dict_fields and type(value) is not dict and value is not None:
                raise ValueError("Value for field '"+str(key)+"' must be a dictionary.")              
        else:
            self.meta_dict[key] = value
        
    def __getitem__(self, key):
        return self.meta_dict[key]
    
    def __delitem__(self, key):
        del self.meta_dict[key]
    
    def __len__(self):
        return len(self.meta_dict)
    
    def keys(self):
        return self.meta_dict.keys()
    
    def values(self):
        return self.meta_dict.values()
    
    def iteritems(self):
        return self.meta_dict.iteritems()


class GraphCollection():
    """
    Collection of NetworkX Graph objects, organized by some index (e.g. time).
    Provides analysis functions in NetworkX for entire collection of Graphs.
    """

    def __init__(self):
        self.graphs = {}
        self.metadata = {}
        return

    def __setitem__(self, index, value):
        """
        The value param can be either a Graph, or a (Graph, metadata) tuple.
        Metadata can be anything, but is probably most profitably a dictionary.
        
        Parameters
        ----------
        index
            This can be anything used to refer to the graph.
        value : :class:`.nx.classes.graph.Graph` or :type:`tuple`
            If a tuple, value[0] must be of type :class:`.nx.classes.graph.Graph`.
            tuple[1] should contain metadata.
            
        Raises
        ------
        ValueError : Graph must be of type networkx.classes.graph.Graph
            Provided value (or value[0]) is not a Graph.
        """
        
        if type(value) is tuple:
            g, metadata = value
            self.metadata[index] = metadata
        else:
            g = value

        if type(g) is not nx.classes.graph.Graph:
            raise(ValueError("Graph must be of type networkx.classes.graph.Graph"))

        self.graphs[index] = value

    def __getitem__(self, key):
        return self.graphs[key]

    def analyze(self, method, **kwargs):
        """
        Passes kwargs to specified NetworkX method for each Graph, and returns
        a dictionary of results as:
        
        results
            | elem (node or edge)
                | graph index (e.g. year)
        
        For example:

        ::
        import tethne.data as dt
        import numpy as np
        collection = dt.GraphCollection()
        N = 100
        for graph_index in xrange(1999, 2004):
            d = np.random.random((N, N))
            g = nx.Graph()
            for i in xrange(N):
                for j in xrange(i+1, N):
                    if d[i, j] > 0.8:
                        g.add_edge(i, j)
            collection.graphs[graph_index] = g
        
        results = collection.analyze('betweenness_centrality', k=None)
        print results[0]
        ::
        
        {1999: 0.010101651117889644,
        2000: 0.0008689093723107329,
        2001: 0.010504898852426189,
        2002: 0.009338654511194512,
        2003: 0.007519105636349891}        
        
        Parameters
        ----------
        method : string
            Name of a method in NetworkX to execute on graph collection.
        **kwargs
            A list of keyword arguments that should correspond to the parameters
            of the specified method.
        
        Returns
        -------
        results : dictionary
            A nested dictionary of results: results/elem(node or edge)/graph 
            index.
        """
        
        results = {}
        
        if not method in nx.__dict__:
            raise(ValueError("No such name in networkx."))
        else:
            if type(nx.__dict__[method]) is not types.FunctionType:
                raise(ValueError("No such method in networkx."))
            else:
                for k,G in self.graphs.iteritems():
                    r = nx.__dict__[method](G, **kwargs)
                    for elem, value in r.iteritems():
                        try:
                            results[elem][k] = value
                        except KeyError:
                            results[elem] = { k: value }
        return results

    def connected(self, method, **kwargs):
        """
        Performs analysis methods from networkx.connected on each graph in the
        collection.
        
        Parameters
        ----------
        method : string
            Name of method in networkx.connected.
        **kwargs : kwargs
            Keyword arguments, passed directly to method.
            
        Returns
        -------
        results : dictionary
            Keys are graph indices, values are output of method for that graph.
        """

        results = {}
        
        if not method in nx.connected.__dict__:
            raise(ValueError("No such name in networkx.connected."))
        else:
            if type(nx.connected.__dict__[method]) is not types.FunctionType:
                raise(ValueError("No such method in networkx.connected."))
            else:
                for k,G in self.graphs.iteritems():
                    r = nx.connected.__dict__[method](G, **kwargs)
                    results[k] = value
        return results
        

def new_query_dict():
    """
    Declares only those keys of meta_dict that are query-able through CrossRef.
    """
    q_dict = {
                'aulast':None,
                'auinit':None,
                'atitle':None,
                'address':None, 
                'jtitle':None,
                'volume':None,
                'issue':None,
                'spage':None,
                'epage':None,
                'date':None     }

    return q_dict


def new_wos_dict():
    """
    Defines the set of field tags that will try to be converted into a meta_dict
    and intializes them to 'None'.
   
    Returns
    -------
    wos_dict : dict
        A wos_list dictionary with 'None' as default values for all keys.
        
    """
    wos_dict = {
                    'DI':None,
                    'AU':None,
                    'C1':None, 
                    'TI':None,
                    'SO':None,
                    'VL':None,
                    'IS':None,
                    'BP':None,
                    'EP':None,
                    'PY':None,
                    'UT':None,
                    'CR':None   }

    return wos_dict

def wos2meta_map():
    """
    Defines the direct relationships between the wos_dict and the meta_dict.
    
    Returns
    -------
    translator : dict
        A 'translator' dictionary.
        
    """
    translator = {
                    'DI':'doi',
                    'TI':'atitle',
                    'SO':'jtitle',
                    'VL':'volume',
                    'IS':'issue',
                    'BP':'spage',
                    'EP':'epage',
                    'PY':'date',
                    'UT':'wosid'    }

    return translator


