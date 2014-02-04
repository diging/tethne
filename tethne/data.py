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

    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    aulast          list    Authors' last name, as a list.
    auinit          list    Authors' first initial as a list.
    institution     dict    Institutions with which the authors are affiliated.
    atitle          str     Article title.
    jtitle          str     Journal title or abbreviated title.
    volume          str     Journal volume number.
    issue           str     Journal issue number.
    spage           str     Starting page of article in journal.
    epage           str     Ending page of article in journal.
    date            int     Article date of publication.
    country         dict    Author-Country mapping.
    citations       list    A list of :class:`.Paper` instances.
    ayjid           str     First author's name (last fi), pubdate, and journal.
    doi             str     Digital Object Identifier.
    pmid            str     PubMed ID.
    wosid           str     Web of Science UT fieldtag value.
    ===========     =====   ====================================================

    None values are also allowed for all fields.
    """

    def __init__(self):
        """
        Defines keys, and acceptable data types for values.
        """
        self.internal = {
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
                            'wosid':None,
                            'abstract':None    }

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
                               'wosid',
                               'abstract' ]

        self.int_fields = [ 'date' ]

        self.dict_fields = [ 'institutions' ]

    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys, and acceptable data types for
        values.
        """

        vt = type(value)
        ks = str(key)

        if key not in self.internal.keys():
            raise KeyError(ks + " is not a valid key in Paper.")
        elif key in self.list_fields and vt is not list and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a list.")
        elif key in self.string_fields and vt is not str and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a string.")
        elif key in self.int_fields and vt is not int and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be an integer.")
        elif key in self.dict_fields and vt is not dict and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a dictionary.")
        else:
            self.internal[key] = value

    def __getitem__(self, key):
        return self.internal[key]

    def __delitem__(self, key):
        del self.internal[key]

    def __len__(self):
        return len(self.internal)

    def keys(self):
        """Returns the keys of the :class:`.Paper`'s metadata fields."""
        return self.internal.keys()

    def values(self):
        """Returns the values of the :class:`.Paper`'s metadata fields."""
        return self.internal.values()

    def iteritems(self):
        """Returns an iterator for the :class:`.Paper`'s metadata fields"""
        return self.internal.iteritems()


class GraphCollection(object):
    """
    Collection of NetworkX :class:`nx.classes.graph.Graph` objects, 
    organized by some index (e.g. time). Provides analysis functions in NetworkX
    for entire collection of Graphs.
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
        Return complete set of nodes for this :class:`.GraphCollection` . 

        If this method has been called previously for this
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

        if len(self.node_list) == 0 or overwrite:
            nodes = set([])
            for G in self.graphs.values():
                nodes = nodes | set(G.nodes())
            self.node_list = list(nodes)
        return self.node_list

    def edges(self, overwrite=False):   # [#61512528]
        """
        Return complete set of edges for this :class:`.GraphCollection` . 

        If this method has been called previously for this
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

        if len(self.edge_list) == 0 or overwrite :
            edges = set([])
            for G in self.graphs.values():
                edges = edges | set(G.edges())
            self.edge_list = list(edges)
        return self.edge_list

    def save(self,filepath):   #[61512528]
        """
        Pickles (serializes) the :class:`.GraphCollection` .
        
        Parameters
        ----------
        filepath :
            Full path of output file.

        Raises
        -------
        PicklingError : Raised when unpicklable objects are Pickled.
        IOError : File does not exist, or cannot be opened.
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
            raise IOError("File does not exist, or cannot be opened.")


    def load(self, filepath):    #[61512528]
        """
        Loads a pickled (serialized) :class:`.GraphCollection` from filepath.

        Parameters
        ----------
        filepath : string
            Full path to pickled :class:`.GraphCollection` .

        Raises
        -------
        UnpicklingError : Raised when there is some issue in unpickling.
        IOError : File does not exist, or cannot be read.
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

        return obj_read