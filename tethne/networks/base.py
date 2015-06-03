import networkx as nx
from itertools import combinations
from collections import Counter, defaultdict

from tethne.utilities import _iterable

def cooccurrence(corpus, featureset_name, min_weight=1):
    """
    A network of feature elements linked by their joint occurrence in papers.
    """

    featureset = corpus.features[featureset_name]
    pairs = Counter()
    for paper, feature in featureset.items():
        for combo in combinations(zip(*feature)[0], 2):
            combo = tuple(sorted(combo))
            pairs[combo] += 1

    graph = nx.Graph()
    for combo, count in pairs.iteritems():
        if count >= min_weight:
            graph.add_edge(combo[0], combo[1], weight=count)
    return graph

def coupling(corpus, featureset_name, min_weight=1):
    """
    A network of papers linked by their joint posession of features.
    """

    featureset = corpus.features[featureset_name]
    pairs = defaultdict(list)
    for feature, papers in featureset.with_feature.iteritems():
        for combo in combinations(papers, 2):
            combo = tuple(sorted(combo))
            pairs[combo].append(featureset.index[feature])

    graph = nx.Graph()
    for combo, features in pairs.iteritems():
        count = len(features)
        if count >= min_weight:
            graph.add_edge(combo[0], combo[1], features=features, weight=count)
    return graph
