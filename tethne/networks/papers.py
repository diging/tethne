"""
Methods for generating networks in which papers are vertices.

.. autosummary::
   :nosignatures:

   author_coupling
   bibliographic_coupling
   cocitation
   direct_citation

"""

from tethne.networks.base import multipartite, coupling, cooccurrence


def direct_citation(corpus, min_weight=1, **kwargs):
    """
    A directed paper-citation network.

    Direct-citation graphs are `directed acyclic graphs`__ in which vertices
    are papers, and each (directed) edge represents a citation of the target
    paper by the source paper. The :func:`.networks.papers.direct_citation`
    method generates both a global citation graph, which includes all cited and
    citing papers, and an internal citation graph that describes only citations
    among papers in the original dataset.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    min_weight : int
        (default: 1) Minimum number of cited papers.
    """

    return multipartite(corpus, ['citations'], min_weight=min_weight, **kwargs)


def bibliographic_coupling(corpus, min_weight=1, **kwargs):
    """
    Generate a bibliographic coupling network.

    Two papers are **bibliographically coupled** when they both cite the same,
    third, paper.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    min_weight : int
        (default 1) Minimum number of cited papers.
    """
    return coupling(corpus, 'citations', min_weight=min_weight, **kwargs)


def cocitation(corpus, min_weight=1, edge_attrs=['ayjid', 'date'], **kwargs):
    """
    Generate a cocitation network.

    A **cocitation network** is a network in which vertices are papers, and
    edges indicate that two papers were cited by the same third paper.
    `CiteSpace
    <http://cluster.cis.drexel.edu/~cchen/citespace/doc/jasist2006.pdf>`_
    is a popular desktop application for co-citation analysis, and you can read
    about the theory behind it
    `here <http://cluster.cis.drexel.edu/~cchen/citespace/>`_.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    min_weight : int
        (default 1) Minimum number of cited papers.
    edge_attrs : list
        (default: ``['ayjid', 'date']``\) Edge attributes in the graph.
    **kwargs
        kwargs to pass on to :func:`.tethne.networks.base.cooccurrence`.

    Returns
    -------
    :class:`.networkx.Graph`
    """
    return cooccurrence(corpus, 'citations', min_weight=min_weight,
                        edge_attrs=edge_attrs, **kwargs)


def author_coupling(corpus, min_weight=1, **kwargs):
    """
    A network of papers linked by their joint possession of features.

    Parameters
    ----------
    corpus_or_featureset : :class:`.Corpus`
    min_weight : int
        (default: 1) Minimum number of linked papers.
    **kwargs
        kwargs to pass on to :func:`.tethne.networks.base.coupling`.

    Returns
    -------
    :class:`.networkx.Graph`
    """
    return coupling(corpus, 'authors', min_weight=min_weight, **kwargs)
