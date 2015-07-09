"""
A :class:`.Paper` represents a single bibliographic record.
"""

from tethne.classes.feature import Feature, feature

class Paper(object):
    """
    Tethne's representation of a bibliographic record.
    
    Fields can be set using dict-like assignment, and accessed as attributes.
    
    .. code-block:: python
    
       >>> myPaper = Paper()
       >>> myPaper['date'] = 1965
       >>> myPaper.date
       1965

    """

    def __setitem__(self, key, value):
        if hasattr(self, key):  # Don't mess with class methods.
            if hasattr(getattr(self, key), '__call__'):
                return
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def ayjid(self):
        """
        Fuzzy WoS-style identifier, comprised of first author's name (LAST I),
        pubdate, and journal.
        
        Returns
        -------
        ayjid : str
        """
    
        if hasattr(self, 'authors_init'):
                al, ai = self.authors_init[0]
        else:
            al, ai = '', ''
        if hasattr(self, 'date'):
            date = str(self.date)
        else:
            date = ''
        if hasattr(self, 'journal'):
            journal = self.journal
        else:
            journal = ''

        ayjid = ' '.join([al, ai.replace(' ',''), date, journal]).strip()
        return ayjid


    @property
    @feature
    def authors(self):
        """
        Get the authors of the current :class:`.Paper` instance.

        Uses ``authors_full`` if it is available. Otherwise, uses
        ``authors_init``.

        Returns
        -------
        authors : :class:`.Feature`
            Author names are in the format ``LAST F``.
        """

        if hasattr(self, 'authors_full'):
            return self.authors_full
        elif hasattr(self, 'authors_init'):
            return self.authors_init
        else:
            return []


    @property
    @feature
    def citations(self):
        """
        Cited references as a :class:`.Feature`\.
        
        Returns
        -------
        citations : :class:`.Feature`
        """
        
        if hasattr(self, 'citedReferences'):
            return [cr.ayjid for cr in self.citedReferences if cr is not None]
        return []
