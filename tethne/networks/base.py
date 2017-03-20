import networkx as nx
from itertools import combinations
from collections import Counter, defaultdict

from tethne.utilities import _iterable
from tethne import Corpus, FeatureSet, StructuredFeatureSet, StreamingCorpus


def _generate_graph(graph_class, pairs, node_attrs={}, edge_attrs={},
                    min_weight=1):
    graph = graph_class()
    for combo, count in pairs.iteritems():
        if count >= min_weight:
            if combo in edge_attrs:
                attrs = edge_attrs[combo]
            else:
                attrs = {}
            graph.add_edge(combo[0], combo[1], weight=count, **attrs)

    for k, attrs in node_attrs.iteritems():
        if k in graph.node:
            graph.node[k].update(attrs)
    return graph


def _get_featureset(corpus_or_featureset, featureset_name):
    if type(corpus_or_featureset) in [Corpus, StreamingCorpus]:  # Retrieve FeatureSet from Corpus.
        if not featureset_name:
            raise ValueError('featureset_name must be provided for Corpus')
        if featureset_name not in corpus_or_featureset.features:
            corpus_or_featureset.index_feature(featureset_name)
        return corpus_or_featureset.features[featureset_name]
    elif type(corpus_or_featureset) in [FeatureSet, StructuredFeatureSet]:
        return corpus_or_featureset     # Already a FeatureSet.
    else:
        raise ValueError('First parameter must be Corpus or FeatureSet')


def cooccurrence(corpus_or_featureset, featureset_name=None, min_weight=1,
                 edge_attrs=['ayjid', 'date'],
                 filter=None):
    """
    A network of feature elements linked by their joint occurrence in papers.

    Parameters
    ----------
    corpus_or_featureset : :class:`.Corpus` or :class:`.FeatureSet` or :class:`.StructuredFeatureSet`
    featureset_name : str
        (default: None)
    min_weight : int
        (default: 1) Minimum number of papers with joint authorship.
    edge_attrs : list
        (default: ``['ayjid', 'date']``\) Edge attributes in the graph.
    filter : callable
        (default: None) Should take four parameters: :class:`.FeatureSet`/
        :class:`.StructedFeatureSet`, value in :class:`.FeatureSet` (e.g.
        overall count), feature count, and document count (i.e. number of
        documents in which the feature value occurs). Should return a bool
        value to indicate if the feature is to be filtered out.

    Returns
    -------
    :class:`.networkx.Graph`
    """

    if not filter:
        filter = lambda f, v, c, dc: dc >= min_weight

    featureset = _get_featureset(corpus_or_featureset, featureset_name)

    if type(corpus_or_featureset) in [Corpus, StreamingCorpus]:
        attributes = {i: {a: corpus_or_featureset.indices_lookup[i][a] for a in edge_attrs}
                      for i in corpus_or_featureset.indexed_papers.keys()}

    c = lambda f: featureset.count(f)           # Overall count.
    dc = lambda f: featureset.documentCount(f)  # Document count.
    attributes = {}

    # select applies filter to the elements in a (Structured)Feature. The
    #  iteration behavior of Feature and StructuredFeature are different, as is
    #  the manner in which the count for an element in each (Structured)Feature.
    if type(featureset) is FeatureSet:
        select = lambda feature: [f for f, v in feature
                                  if filter(f, v, c(f), dc(f))]
    elif type(featureset) is StructuredFeatureSet:
        select = lambda feature: [f for f in feature
                                  if filter(f, feature.count(f), c(f), dc(f))]

    pairs = Counter()
    eattrs = defaultdict(dict)
    nattrs = defaultdict(dict)
    nset = set()

    for paper, feature in featureset.iteritems():
        if len(feature) == 0:
            continue

        selected = select(feature)
        nset |= set(selected)
        for combo in combinations(selected, 2):
            combo = tuple(sorted(combo))
            pairs[combo] += 1

            if paper in attributes:
                eattrs[combo] = attributes[paper]

    # Generate node attributes.
    for n in list(nset):
        nattrs[n]['count'] = featureset.count(n)
        nattrs[n]['documentCount'] = featureset.documentCount(n)

    return _generate_graph(nx.Graph, pairs, edge_attrs=eattrs,
                            node_attrs=nattrs, min_weight=min_weight)



def coupling(corpus_or_featureset, featureset_name=None,
             min_weight=1, filter=lambda f, v, c, dc: True,
             node_attrs=[]):
    """
    A network of papers linked by their joint possession of features.

    Parameters
    ----------
    corpus_or_featureset : :class:`.Corpus` or :class:`.FeatureSet` or :class:`.StructuredFeatureSet`
    featureset_name : str
        (default: None)
    min_weight : int
        (default: 1) Minimum number of linked papers.
    filter : callable
        (default: ``lambda f, v, c, dc: True``) Should take four parameters:
        :class:`.FeatureSet`/ :class:`.StructedFeatureSet`, value in
        :class:`.FeatureSet` (e.g.  overall count), feature count, and document
        count (i.e. number of documents in which the feature value occurs).
        Should return a bool value to indicate if the feature is to be
        filtered out.
    node_attrs : list
        (default []) Add listed paper attributes to graph nodes.

    Returns
    -------
    :class:`.networkx.Graph`
    """

    featureset = _get_featureset(corpus_or_featureset, featureset_name)

    c = lambda f: featureset.count(f)           # Overall count.
    dc = lambda f: featureset.documentCount(f)  # Document count.
    f = lambda elem: featureset.index[elem]
    v = lambda p, f: featureset.features[p].value(f)

    select = lambda p, elem: filter(f(elem), v(p, f(elem)), c(f(elem)), dc(f(elem)))

    pairs = defaultdict(list)
    for elem, papers in featureset.with_feature.iteritems():
        selected = [p for p in papers if select(p, elem)]
        for combo in combinations(selected, 2):
            combo = tuple(sorted(combo))
            pairs[combo].append(featureset.index[elem])

    graph = nx.Graph()
    for combo, features in pairs.iteritems():
        count = len(features)
        if count >= min_weight:
            graph.add_edge(combo[0], combo[1], features=features, weight=count)

    # Add node attributes.
    for attr in node_attrs:
        for node in graph.nodes():
            value = ''
            if node in corpus_or_featureset:
                paper = corpus_or_featureset[node]
                if hasattr(paper, attr):
                    value = getattr(paper, attr)
                    if value is None:
                        value = ''
                    elif callable(value):
                        value = value()
            graph.node[node][attr] = value

    return graph


def multipartite(corpus, featureset_names, min_weight=1, filters={}):
    """
    A network of papers and one or more featuresets.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    featureset_names : iterable
        Iterable of featureset_names.
    min_weight : int
        (default: 1) Minimum number of linked papers.
    filters : dict
        (default: {}) Dict with featureset_name as keys and callables as
        values. The callables must accept two values: :class:`.FeatureSet` and
        :class:`.Feature`, and return a boolean value indicating if the paper
        should be filtered out.

    Returns
    -------
    :class:`.networkx.DiGraph`
    """

    pairs = Counter()
    node_type = {corpus._generate_index(p): {'type': 'paper'}
                 for p in corpus.papers}
    for featureset_name in featureset_names:
        ftypes = {}

        featureset = _get_featureset(corpus, featureset_name)
        for paper, feature in featureset.iteritems():
            if featureset_name in filters:
                if not filters[featureset_name](featureset, feature):
                    continue
            if len(feature) < 1:
                continue
            for f in list(zip(*feature))[0]:
                ftypes[f] = {'type': featureset_name}
                pairs[(paper, f)] += 1
        node_type.update(ftypes)

    return _generate_graph(nx.DiGraph, pairs, node_attrs=node_type,
                           min_weight=min_weight)
