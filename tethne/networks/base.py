import networkx as nx
from itertools import combinations
from collections import Counter, defaultdict

from tethne.utilities import _iterable

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

def _get_feautureset(corpus, featureset_name):
    if featureset_name not in corpus.features:
        corpus.index_feature(featureset_name)

    return corpus.features[featureset_name]

def cooccurrence(corpus, featureset_name, min_weight=1,
                 edge_attrs=['ayjid', 'date'], filter=lambda fs, f: True):
    """
    A network of feature elements linked by their joint occurrence in papers.
    """
    featureset = _get_feautureset(corpus, featureset_name)

    pairs = Counter()
    eattrs = defaultdict(dict)
    nattrs = defaultdict(dict)
    nset = set()
    for paper, feature in featureset.items():
        if len(feature) == 0:
            continue

        selected = [f for f in zip(*feature)[0] if filter(featureset, f)]
        nset |= set(selected)
        for combo in combinations(selected, 2):
            combo = tuple(sorted(combo))
            pairs[combo] += 1

            for a in edge_attrs:    # Include edge attributes.
                eattrs[combo][a] = corpus.indexed_papers[paper][a]

    # Generate node attributes.
    for n in list(nset):
        nattrs[n]['count'] = featureset.count(n)
        nattrs[n]['documentCount'] = featureset.documentCount(n)

    return _generate_graph(nx.Graph, pairs, edge_attrs=eattrs,
                           node_attrs=nattrs, min_weight=min_weight)

def coupling(corpus, featureset_name, min_weight=1, filter=lambda fs, f: True):
    """
    A network of papers linked by their joint posession of features.
    """

    featureset = _get_feautureset(corpus, featureset_name)

    pairs = defaultdict(list)
    for feature, papers in featureset.with_feature.iteritems():
        if filter(featureset, feature):
            for combo in combinations(papers, 2):
                combo = tuple(sorted(combo))
                pairs[combo].append(featureset.index[feature])

    graph = nx.Graph()
    for combo, features in pairs.iteritems():
        count = len(features)
        if count >= min_weight:
            graph.add_edge(combo[0], combo[1], features=features, weight=count)
    return graph

def multipartite(corpus, featureset_names, min_weight=1, filters={}):
    """
    A network of papers and one or more featuresets.
    """

    pairs = Counter()
    node_type = {corpus._generate_index(p): {'type': 'paper'}
                 for p in corpus.papers}
    for featureset_name in featureset_names:
        ftypes = {}
        
        featureset = _get_feautureset(corpus, featureset_name)
        for paper, feature in featureset.items():
            if featureset_name in filters:
                if not filters[featureset_name](featureset, feature):
                    continue
            if len(feature) < 1:
                continue
            for f in zip(*feature)[0]:
                ftypes[f] = {'type': featureset_name}
                pairs[(paper, f)] += 1
        node_type.update(ftypes)

    return _generate_graph(nx.Graph, pairs, node_attrs=node_type,
                           min_weight=min_weight)
