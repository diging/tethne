"""
A :class:`.Paper` represents a single document. :class:`.Paper` objects behave
much like conventional Python dictionaries, except that they are picky about
the kind of data that you throw into them.
"""


class Paper(dict):
    """
    Tethne's representation of a bibliographic record.

    The following fields (and corresponding data types) are permitted.

    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    aulast          list    Authors' last name, as a list.
    auinit          list    Authors' first initial as a list.
    aufull          list    Authors' full names.
    institution     dict    Institutions with which the authors are affiliated.
    atitle          str     Article title.
    jtitle          str     Journal title or abbreviated title.
    volume          str     Journal volume number.
    issue           str     Journal issue number.
    spage           str     Starting page of article in journal.
    epage           str     Ending page of article in journal.
    date            int     Article date of publication.
    citations       list    A list of :class:`.Paper` instances.
    ayjid           str     First author's name (last fi), pubdate, and journal.
    doi             str     Digital Object Identifier.
    pmid            str     PubMed ID.
    wosid           str     Web of Science UT fieldtag value.
    accession       str     Identifier for data conversion accession.
    ===========     =====   ====================================================

    None values are also allowed for all fields.
    """

    fields = ['aulast', 'auinit', 'aufull', 'auuri', 'institutions', 'atitle',
              'jtitle', 'volume', 'issue', 'spage', 'epage', 'date',
              'citations', 'ayjid', 'doi', 'pmid', 'wosid', 'eid', 'uri',
              'abstract', 'contents', 'accession', 'topics']

    # Fields that require list values.
    list_fields = ['aulast', 'auinit', 'aufull', 'auuri', 'citations',
                   'institutions']

    # Fields that require string values.
    string_fields = ['atitle', 'jtitle', 'volume', 'issue', 'spage',
                     'epage', 'ayjid', 'doi', 'eid', 'pmid', 'wosid',
                     'abstract', 'contents', 'accession']

    # Fields that require int values.
    int_fields = [ 'date' ]

    # Fields that require dict values.
    dict_fields = []

    def __init__(self):
        for field in self.fields:
            dict.__setitem__(self, field, None)

    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys and corresponding data types for
        values.
        """

        if key not in self.keys():
            err, msg = KeyError, "{0} is not a valid key in Paper.".format(key)

        if self._valid(key, value):
            dict.__setitem__(self, key, value)

    def __getattr__(self, key):
        return self.__getitem__(key)

    def _valid(self, key, value):
        err, vmsg = None, "Value for field '{0}' must be a {1}."

        if value is None:
            pass
        elif key in self.list_fields and type(value) is not list:
            err, msg = ValueError, vmsg.format(key, 'list')
        elif key in self.string_fields and type(value) not in [str, unicode]:
            err, msg = ValueError, vmsg.format(key, 'string or unicode')
        elif key in self.int_fields and type(value) is not int:
            err, msg = ValueError, vmsg.format(key, 'integer')
        elif key in self.dict_fields and type(value) is not dict:
            err, msg = ValueError, vmsg.format(key, 'dict')
        if err is not None:
            raise err(msg)
        return True

    def authors(self):
        """
        Get the authors of the current :class:`.Paper` instance.

        Returns
        -------
        authors : list
            Author names are in the format ``LAST F``. If there are no authors,
            returns an empty list.
        """

        if self['aulast'] is None:
            return []

        auths = [' '.join([a, l]).upper() for a,l
                 in zip(self['aulast'], self['auinit'])]
        return auths
