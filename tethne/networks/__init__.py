"""
Methods for building networks from bibliographic data.

Each network relies on certain meta data in the :class:`.Paper` associated with
each document. Often we wish to construct a network with nodes representing
these documents and edges representing relationships between those documents,
but this is not always the case.

Where it is the case, it is recommended but not required that nodes are
represented by an identifier from {ayjid, wosid, pmid, doi}. Each has certain
benefits. If the documents to be networked come from a single database source
such as the Web of Science, wosid is most appropriate. If not, using doi
will result in a more accurate, but also more sparse network; while ayjid
will result in a less accurate, but more complete network.

Any type of meta data from the :class:`.Paper` may be used as an identifier,
however.

We use "head" and "tail" nomenclature to refer to the members of a directed
edge (x,y), x -> y, xy, etc. by calling x the "tail" and y the "head".

Modules
```````

.. autosummary::

   authors
   helpers
   papers
   terms
   
"""


#import papers
#import authors
#import helpers
#import terms

#Added because of pylint error.
import tethne.networks.papers
import tethne.networks.authors
import tethne.networks.helpers
import tethne.networks.terms
