"""
Each file reader provides methods to parse bibliographic data from a
scholarly database (e.g. Web of Science or PubMed), resulting in a
list of :class:`.Paper` instances containing as many as possible of
the following keys (missing values are set to None):

    * aulast (list) -- Authors' surnames, as a list.
    * auinit (list) -- Authors' initials, as a list.
    * institution (dict) -- Institutions with which the authors are affiliated.
    * atitle (str) -- Article title.
    * jtitle (str) -- Journal title or abbreviated title.
    * volume (str) -- Journal volume number.
    * issue (str) -- journal issue number.
    * spage (str) -- Etarting page of article in journal.
    * epage (str) -- Ending page of article in journal.
    * date (int) -- Date of publication.
    * abstract (str)

These keys are associated with the meta data entries in the databases of
organizations such as the International DOI Foundation and its Registration
Agencies such as CrossRef and DataCite.

In addition, :class:`.Paper` instances will contain keys with information
relevant to the networks of interest for Tethne including:

    * citations -- list of minimum :class:`.Paper` instances for cited
        references.
    * ayjid -- First author's name (last, fi), publication year, and journal.
    * doi -- Digital Object Identifier
    * pmid -- PubMed ID
    * wosid -- Web of Science UT fieldtag

Missing data here also results in the above keys being set to None.
"""

import wos
import pubmed

class DataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)
