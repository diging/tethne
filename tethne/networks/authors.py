"""
Methods for generating networks in which authors are vertices.

.. autosummary::
   :nosignatures:

   author_papers
   coauthors

"""

from tethne.networks.base import cooccurrence, multipartite


def author_papers(corpus, min_weight=1, **kwargs):
    """
    A bi-partite graph containing :class:`.Paper`\s and their authors.
    """
    return multipartite(corpus, ['authors'], min_weight=min_weight, **kwargs)


def coauthors(corpus, min_weight=1, edge_attrs=['ayjid', 'date'], **kwargs):
    """
    A graph describing joint authorship in ``corpus``.
    """
    return cooccurrence(corpus, 'authors', min_weight=min_weight,
                        edge_attrs=edge_attrs, **kwargs)
