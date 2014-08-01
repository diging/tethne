"""
A :class:`.Paper` represents a document in a :class:`.Corpus`\. :class:`.Paper`
objects behave a lot like conventional Python dictionaries, except that they are
picky about the kind of data that you throw into them.

Most operations in Tethne don't require you to interact with :class:`.Paper`\s
directly.
"""

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

class Paper(dict):
    """
    Tethne's representation of a bibliographic record.

    The following fields (and corresponding data types) are permitted.
    
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
        # Default values.
        fields = {
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
            'pmid':None,    # PubMed
            'wosid':None,   # ISI Web of Science
            'eid':None,     # Scopus
            'abstract':None,
            'accession':None,
            'topics':None    }

        for k,v in fields.iteritems():
            dict.__setitem__(self, k, v)

        # Fields that require list values.
        self.list_fields = [ 'aulast',
                             'auinit',
                             'citations' ]

        # Fields that require string values.
        self.string_fields = [ 'atitle',
                               'jtitle',
                               'volume',
                               'issue',
                               'spage',
                               'epage',
                               'ayjid',
                               'doi',
                               'eid',
                               'pmid',
                               'wosid',
                               'abstract',
                               'accession' ]

        # Fields that require int values.
        self.int_fields = [ 'date' ]

        # Fields that require dict values.
        self.dict_fields = [ 'institutions' ]

    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys and corresponding data types for
        values.
        """

        vt = type(value)
        ks = str(key)

        if key not in self.keys():
            raise KeyError(ks + " is not a valid key in Paper.")
        elif key in self.list_fields and vt is not list and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a list.")
        elif key in self.string_fields and vt is not str \
                and vt is not unicode and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a string.")
        elif key in self.int_fields and vt is not int and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be an integer.")
        elif key in self.dict_fields and vt is not dict and value is not None:
            raise ValueError("Value for field '"+ ks +"' must be a dictionary.")
        else:
            dict.__setitem__(self, key, value)

    def authors(self):
        """
        Get the authors of the current :class:`.Paper` instance.
        
        Returns
        -------
        authors : list
            Author names are in the format ``LAST F``. If there are no authors,
            returns an empty list.
        """
        
        auths = []
        if self['aulast'] is not None:
             auths = [ ' '.join([ a,l ]).upper()
                         for a,l in zip (self['aulast'], self['auinit']) ]
        return auths