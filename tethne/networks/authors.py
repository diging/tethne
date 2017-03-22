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

    Parameters
    ----------
    corpus : :class:`.Corpus`
    min_weight : int
        (default: 1) Minimum number of papers per author in the graph.
    **kwargs
        kwargs to pass on to :func:`.tethne.networks.base.multipartite`.

    Returns
    -------
    :class:`.networkx.DiGraph`
    """
    return multipartite(corpus, ['authors'], min_weight=min_weight, **kwargs)


def coauthors(corpus, min_weight=1, edge_attrs=['ayjid', 'date'], **kwargs):
    """
    A graph describing joint authorship in ``corpus``.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    min_weight : int
        (default: 1) Minimum number of papers with joint authorship.
    edge_attrs : list
        (default: ``['ayjid', 'date']``\) Edge attributes in the graph.
    **kwargs
        kwargs to pass on to :func:`.tethne.networks.base.cooccurrence`.

    Returns
    -------
    :class:`.networkx.Graph`
    """
    return cooccurrence(corpus, 'authors', min_weight=min_weight,
                        edge_attrs=edge_attrs, **kwargs)
