"""
A :class:`.Paper` represents a single bibliographic record.
"""

from tethne.classes.feature import Feature, feature


class Paper(object):
    """
    Tethne's representation of a bibliographic record.
    """

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    @property
    def ayjid(self):
        """
        Fuzzy WoS-style identifier, comprised of first author's name (LAST I),
        pubdate, and journal.
        """

        al, ai = self.authors_init[0]
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

        Returns
        -------
        authors : list
        Author names are in the format ``LAST F``. If there are no authors,
        returns an empty list.
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
        """
        if hasattr(self, 'citedReferences'):
            return [cr.ayjid for cr in self.citedReferences if cr is not None]
        return []


