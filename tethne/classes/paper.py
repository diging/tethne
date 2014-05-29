import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

import tables
class Paper(object):
    """
    Base class for Papers. 
    
    Behaves just like a dict, but enforces a limited vocabulary of keys, and 
    specific data types.

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
    accession       str     Identifier for data conversion accession.
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
                            'abstract':None,
                            'accession':None,
                            'topics':None    }

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
                               'abstract',
                               'accession' ]

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
        elif key in self.string_fields and vt is not str and vt is not unicode and value is not None:
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
    
    def authors(self):
        """Returns a list of author names (FI LAST)."""
        
        auths = []
        for i in xrange(len(self.internal['aulast'])):
            au = self.internal['auinit'][i] + ' ' +  self.internal['aulast'][i]
            auths.append( au.upper() )
        return auths

class HDF5Paper(tables.IsDescription):
    mindex = tables.StringCol(100)
    aulast = tables.StringCol(1000)
    auinit = tables.StringCol(1000)
    atitle = tables.StringCol(200)
    jtitle = tables.StringCol(200)
    volume = tables.StringCol(6)
    issue = tables.StringCol(6)
    spage = tables.StringCol(6)
    epage = tables.StringCol(6)
    ayjid = tables.StringCol(200)
    doi = tables.StringCol(100)
    pmid = tables.StringCol(100)
    wosid = tables.StringCol(100)
    abstract = tables.StringCol(5000)
    accession = tables.StringCol(100)
    date = tables.Int32Col()