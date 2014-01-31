"""
Tethne uses a small number of special classes for handling data.
"""

import networkx as nx
import pickle as pk
from cStringIO import StringIO
from pprint import pprint
import sys

class Paper(object):
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

        vt = type(value)
        ks = str(key)

        if key not in self.meta_dict.keys():
            raise KeyError(ks + " is not a valid key in Paper meta_dict.")
        elif key in self.list_fields and vt is not list and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a list.")
        elif key in self.string_fields and vt is not str and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a string.")
        elif key in self.int_fields and vt is not int and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be an integer.")
        elif key in self.dict_fields and vt is not dict and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a dictionary.")
        else:
            self.meta_dict[key] = value

    def __getitem__(self, key):
        return self.meta_dict[key]

    def __delitem__(self, key):
        del self.meta_dict[key]

    def __len__(self):
        return len(self.meta_dict)

    def keys(self):
        """Returns the keys of the internal meta_dict."""
        return self.meta_dict.keys()

    def values(self):
        """Returns the values of the internal meta_dict."""
        return self.meta_dict.values()

    def iteritems(self):
        """Returns an iterator for the internal meta_dict."""
        return self.meta_dict.iteritems()


class GraphCollection(object):
    """
    Collection of NetworkX Graph objects, organized by some index (e.g. time).
    Provides analysis functions in NetworkX for entire collection of Graphs.
    """

    def __init__(self):
        self.graphs = {}
        self.metadata = {}
        self.edge_list = []
        self.node_list = []

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
            If a tuple, value[0] must be of type
            :class:`.nx.classes.graph.Graph`. tuple[1] should contain metadata.

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
            raise(ValueError("Graph must be type networkx.classes.graph.Graph"))

        self.graphs[index] = value

    def __getitem__(self, key):
        return self.graphs[key]

    def __delitem__(self, key):
        del self.graphs[key]

    def __len__(self):
        return len(self.graphs)

    def nodes(self, overwrite=False):
        """
        Return complete set of nodes for this :class:`.GraphCollection` . If
        this method has been called previously for this
        :class:`.GraphCollection` then will not recompute unless overwrite =
        True.

        Parameters
        ----------
        overwrite : bool
            If True, will generate new node list, even if one already exists.

        Returns
        -------
        nodes : list
            List (complete set) of node identifiers for this
            :class:`.GraphCollection` .
        """

        if not hasattr(self, 'node_list') or overwrite:
            nodes = set([])
            for G in self.graphs.values():
                nodes = nodes | set(G.nodes())
            self.node_list = list(nodes)
        return self.node_list

    def edges(self, overwrite=False):   # [#61512528]
        """
        Return complete set of edges for this :class:`.GraphCollection` . If
        this method has been called previously for this
        :class:`.GraphCollection` then will not recompute unless overwrite =
        True.

        Parameters
        ----------
        overwrite : bool
            If True, will generate new node list, even if one already exists.

        Returns
        -------
        edges : list
            List (complete set) of edges for this :class:`.GraphCollection` .
        """

        if not hasattr(self, 'edge_list') or not overwrite :
            edges = set([])
            for G in self.graphs.values():
                edges = edges | set(G.edges())
            self.edge_list = list(edges)
        return self.edge_list
    
    def save(self,filepath):   #[61512528]
        """
        This method is used to pickle(save) the objects to a particular file 
        thereby serializing them.
        
        Parameters
        ----------
        filepath : path and name of the file the user wants to
        save the GraphCollection objects. 
        
        Raises
        -------
        PicklingError : Raised when unpicklable objects are Pickled.
        
        Returns
        -------
        None
        """
    
            
        # Try block if the filename is present or not.
        try:
            with open(filepath,'wb') as output:
                try:
                    pk.dump(self, output)
                except PicklingError:     # Handle the Prickling error.
                    raise PicklingError \
                            ("Pickling error: The object cannot be pickled")
        except IOError: # File does not exist, or couldn't be read.
            raise IOError("File does not exist, or cannot be read.")
     

    def load(self, filepath):    #[61512528]
        """
        This method is used to unpickle(load) the objects from the file
        where it was serialized, and o restore the object hierarchy.
        
        Parameters
        ----------
                
        Filename : path and name of the file the user wishes to
        retrieve the objects. This is a mandatory parameter.
        
        Raises
        -------
        UnpicklingError : Raised when there is some issue in unpickling.
        
        Returns
        -------
        None
        
        """
         # Handle NameError File not found.
        
        try:
            with open(filepath,'rb') as input: #reading in binary mode
                try:
                     obj_read = pk.load(input)
                except UnpicklingError:  # Handle unprickling error.
                    raise UnpicklingError \
                        ("UnPickling error: The object cannot be found")
                    
    
        except IOError: # File does not exist, or couldn't be read.
            raise IOError("File does not exist, or cannot be read.")

        if type(obj_read):
            pprint(obj_read)

        return obj_read

                                      

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


