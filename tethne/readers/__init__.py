"""
Methods for parsing bibliographic datasets.

.. autosummary::

   dfr
   wos

Each file reader provides methods to parse bibliographic data from a
scholarly database (e.g. Web of Science or PubMed), resulting in a
list of :class:`.Paper` instances containing as many as possible of
the following keys (missing values are set to None):

===========    =====    ===================================================
Field          Type     Description
===========    =====    ===================================================
aulast         list     Authors' surnames, as a list.
auinit         list     Authors' initials, as a list.
institution    dict     Institutions with which the authors are affiliated.
atitle         str      Article title.
jtitle         str      Journal title or abbreviated title.
volume         str      Journal volume number.
issue          str      Journal issue number.
spage          str      Starting page of article in journal.
epage          str      Ending page of article in journal.
date           int      Date of publication.
abstract       str
===========    =====    ===================================================

These keys are associated with the meta data entries in the databases of
organizations such as the International DOI Foundation and its Registration
Agencies such as CrossRef and DataCite.

In addition, :class:`.Paper` instances will contain keys with information
relevant to the networks of interest for Tethne including:

===========    =====    ======================================================
Field          Type     Description
===========    =====    ======================================================
citations      list     List of minimum :class:`.Paper` instances for cited
                        references.
ayjid          str      First author's name (last, fi), publication year, and
                        journal.
doi            str      Digital Object Identifier.
pmid           str      PubMed ID.
wosid          str      Web of Science UT fieldtag.
===========    =====    ======================================================

Missing data here also results in the above keys being set to None.

"""

import wos
import dfr

from ..classes import Paper

class DataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def merge(P1, P2, fields=['ayjid']):
    """
    Combines two lists (P1 and P2) of :class:`.Paper` instances into a single
    list, and attempts to merge papers with matching fields. Where there are
    conflicts, values from :class:`.Paper` in P1 will be preferred.

    Parameters
    ----------
    P1 : list
        A list of :class:`.Paper` instances.
    P2 : list
        A list of :class:`.Paper` instances.
    fields : list
        Fields used to identify matching :class:`.Paper`

    Returns
    -------
    combined : list
        A list of :class:`.Paper` instances.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> P1 = rd.wos.read("/Path/to/data1.txt")
       >>> P2 = rd.dfr.read("/Path/to/DfR")
       >>> papers = rd.merge(P1, P2, ['ayjid'])
    """

    combined = []
    del_P1 = []
    del_P2 = []

    for x in xrange(len(P1)):
        p_1 = P1[x]
        for y in xrange(len(P2)):
            p_2 = P2[y]
            match = True
            for field in fields:
                if p_1[field] != p_2[field]:
                    match = False
                    break

            if match:   # Add values first from P2 paper, then from P1 paper.
                new_p = Paper()
                for key, value in p_2.iteritems():
                    if value != '' and value != None:
                        new_p[key] = value
                for key, value in p_1.iteritems():
                    if value != '' and value != None:
                        new_p[key] = value

                del_P1.append(x)    # Flag for deletion.
                del_P2.append(y)

                combined.append(new_p)

    for x in xrange(len(P1)):
        if x not in del_P1:
            combined.append(P1[x])
    for x in xrange(len(P2)):
        if x not in del_P2:
            combined.append(P2[x])

    return combined