"""
Methods for analyzing :class:`.Corpus` objects.

.. autosummary::
   :nosignatures:

   burstness
   feature_burstness
   sigma

"""

import networkx as nx
import warnings

from math import exp, log
from collections import defaultdict
from itertools import izip

from tethne.utilities import argmin, mean

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str
    xrange = range



def _forward(X, s=1.1, gamma=1., k=5):
    """
    Forward dynamic algorithm for burstness automaton HMM, from `Kleinberg
    (2002) <http://www.cs.cornell.edu/home/kleinber/bhs.pdf>`_.

    Parameters
    ----------
    X : list
        A series of time-gaps between events.
    s : float
        (default: 1.1) Scaling parameter ( > 1.)that controls graininess of
        burst detection. Lower values make the model more sensitive.
    gamma : float
        (default: 1.0) Parameter that controls the 'cost' of higher burst
        states. Higher values make it more 'difficult' to achieve a higher
        burst state.
    k : int
        (default: 5) Number of states. Higher values increase computational
        cost of the algorithm. A maximum of 25 is suggested by the literature.

    Returns
    -------
    states : list
        Optimal state sequence.
    """
    X = list(X)

    def alpha(i):
        return (n/T)*(s**i)

    def tau(i, j):
        if j > i:
            return (j-i)*gamma*log(n)
        return 0.

    def f(j, x):
        return alpha(j) * exp(-1. * alpha(j) * x)

    def C(j, t):
        if j == 0 and t == 0:
            return 0.
        elif t == 0:
            return float("inf")

        C_tau = min([C_values[l][t-1] + tau(l, j) for l in xrange(k)])
        return (-1. * log(f(j,X[t]))) + C_tau

    T = sum(X)
    n = len(X)

    # C() requires default (0) values, so we construct the "array" in advance.
    C_values = [[0 for t in xrange(len(X))] for j in xrange(k)]
    for j in xrange(k):
        for t in xrange(len(X)):
            C_values[j][t] = C(j,t)

    # Find the optimal state sequence.
    states = [argmin([c[t] for c in C_values]) for t in xrange(n)]
    return states

def _top_features(corpus, feature, topn=20, perslice=False, axis='date'):
    warnings.warn("Removed in 0.8. Use corpus.top_features() instead.",
                  DeprecationWarning)
    return corpus.top_features(feature, topn=topn, perslice=perslice)

def burstness(corpus, featureset_name, features=[], k=5, topn=20,
              perslice=False, normalize=True, **kwargs):
    """
    Estimate burstness profile for the ``topn`` features (or ``flist``) in
    ``feature``.

    Uses the popular burstness automaton model inroduced by `Kleinberg (2002)
    <http://www.cs.cornell.edu/home/kleinber/bhs.pdf>`_.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    feature : str
        Name of featureset in ``corpus``. E.g. ``'citations'``.
    k : int
        (default: 5) Number of burst states.
    topn : int or float {0.-1.}
        (default: 20) Number (int) or percentage (float) of top-occurring
        features to return. If ``flist`` is provided, this parameter is ignored.
    perslice : bool
        (default: False) If True, loads ``topn`` features per slice. Otherwise,
        loads ``topn`` features overall. If ``flist`` is provided, this
        parameter is ignored.
    flist : list
        List of features. If provided, ``topn`` and ``perslice`` are ignored.
    normalize : bool
        (default: True) If True, burstness is expressed relative to the hightest
        possible state (``k-1``). Otherwise, states themselves are returned.
    kwargs : kwargs
        Parameters for burstness automaton HMM.

    Returns
    -------
    B : dict
        Keys are features, values are tuples of ( dates, burstness )

    Examples
    --------

    .. code-block:: python

       >>> from tethne.analyze.corpus import burstness
       >>> B = burstness(corpus, 'abstractTerms', flist=['process', 'method']
       >>> B['process']
       ([1990, 1991, 1992, 1993], [0., 0.4, 0.6, 0.])

    """

    # If `features` of interest are not specified, calculate burstness for the
    #  top `topn` features.
    if len(features) == 0:
        T = corpus.top_features(featureset_name, topn=topn, perslice=perslice)
        if perslice:
            features = list(set([f[0] for flist in zip(*T)[1] for f in flist]))
        else:
            features = list(zip(*T))[0]

    B = {feature: feature_burstness(corpus, featureset_name, feature, k=k,
                                    normalize=normalize, **kwargs)
         for feature in features}
    return B

def feature_burstness(corpus, featureset_name, feature, k=5, normalize=True,
                      s=1.1, gamma=1., **slice_kwargs):
    """
    Estimate burstness profile for a feature over the ``'date'`` axis.

    Parameters
    ----------
    corpus : :class:`.Corpus`
    feature : str
        Name of featureset in ``corpus``. E.g. ``'citations'``.
    findex : int
        Index of ``feature`` in ``corpus``.
    k : int
        (default: 5) Number of burst states.
    normalize : bool
        (default: True) If True, burstness is expressed relative to the hightest
        possible state (``k-1``). Otherwise, states themselves are returned.
    kwargs : kwargs
        Parameters for burstness automaton HMM.
    """


    if featureset_name not in corpus.features:
        corpus.index_feature(featureset_name)

    if 'date' not in corpus.indices:
        corpus.index('date')

    # Get time-intervals between occurrences.
    dates = [min(corpus.indices['date'].keys()) - 1]    # Pad start.
    X_ = [1.]

    years, values = corpus.feature_distribution(featureset_name, feature)
    for year, N in izip(years, values):
        if N == 0:
            continue

        if N > 1:
            if year == dates[-1] + 1:
                for n in xrange(int(N)):
                    X_.append(1./N)
                    dates.append(year)
            else:
                X_.append(float(year - dates[-1]))
                dates.append(year)
                for n in xrange(int(N) - 1):
                    X_.append(1./(N - 1))
                    dates.append(year)
        else:
            X_.append(float(year - dates[-1]))
            dates.append(year)

    # Get optimum state sequence.
    st = _forward(map(lambda x: x*100, X_), s=s, gamma=gamma, k=k)

    # Bin by date.
    A = defaultdict(list)
    for i in xrange(len(X_)):
        A[dates[i]].append(st[i])

    # Normalize.
    if normalize:
        A = {key: mean(values)/k for key, values in A.items()}
    else:
        A = {key: mean(values) for key, values in A.items()}

    D = sorted(A.keys())
    return D[1:], [A[d] for d in D[1:]]


def sigma(G, corpus, featureset_name, B=None, **kwargs):
    """
    Calculate sigma (from `Chen 2009 <http://arxiv.org/pdf/0904.1439.pdf>`_)
    for all of the nodes in a :class:`.GraphCollection`\.

    You can set parameters for burstness estimation using ``kwargs``:

    =========   ===============================================================
    Parameter   Description
    =========   ===============================================================
    s           Scaling parameter ( > 1.)that controls graininess of burst
                detection. Lower values make the model more sensitive. Defaults
                to 1.1.
    gamma       Parameter that controls the 'cost' of higher burst states.
                Defaults to 1.0.
    k           Number of burst states. Defaults to 5.
    =========   ===============================================================

    Parameters
    ----------
    G : :class:`.GraphCollection`
    corpus : :class:`.Corpus`
    feature : str
        Name of a featureset in `corpus`.


    Examples
    --------

    Assuming that you have a :class:`.Corpus` generated from WoS data that has
    been sliced by ``date``.

    .. code-block:: python

       >>> # Generate a co-citation graph collection.
       >>> from tethne import GraphCollection
       >>> kwargs = { 'threshold':2, 'topn':100 }
       >>> G = GraphCollection()
       >>> G.build(corpus, 'date', 'papers', 'cocitation', method_kwargs=kwargs)

       >>> # Calculate sigma. This may take several minutes, depending on the
       >>> #  size of your co-citaiton graph collection.
       >>> from tethne.analyze.corpus import sigma
       >>> G = sigma(G, corpus, 'citations')

       >>> # Visualize...
       >>> from tethne.writers import collection
       >>> collection.to_dxgmml(G, '~/cocitation.xgmml')

    In the visualization below, node and label sizes are mapped to ``sigma``,
    and border width is mapped to ``citations``.

    .. figure:: _static/images/cocitation_sigma2.png
       :width: 600
       :align: center

    """
    if 'date' not in corpus.indices:
        corpus.index('date')

    # Calculate burstness if not provided.
    if not B:
        B = burstness(corpus, featureset_name, features=G.nodes(), **kwargs)

    Sigma = {}      # Keys are dates (from GraphCollection), values are
                    #  node:sigma dicts.
    for key, graph in G.items():
        centrality = nx.betweenness_centrality(graph)
        sigma = {}  # Sigma values for all features in this year.
        attrs = {}  # Sigma values for only those features in this graph.
        for n_, burst in B.items():
            burst = dict(list(zip(*burst)))     # Reorganize for easier lookup.

            # Nodes are indexed as integers in the GraphCollection.
            n = G.node_lookup[n_]

            # We have burstness values for years in which the feature ``n``
            #  occurs, and we have centrality values for years in which ``n``
            #  made it into the graph.
            if n in graph.nodes() and key in burst:
                sigma[n] = ((centrality[n] + 1.) ** burst[key]) - 1.
                attrs[n] = sigma[n]

        # Update graph with sigma values.
        nx.set_node_attributes(graph, 'sigma', attrs)
        Sigma[key] = sigma

    # Invert results and update the GraphCollection.master_graph.
    # TODO: is there a more efficient way to do this?
    inverse = defaultdict(dict)
    for gname, result in Sigma.items():
        if hasattr(result, '__iter__'):
            for n, val in result.items():
                inverse[n].update({gname: val})
    nx.set_node_attributes(G.master_graph, 'sigma', inverse)

    # We want to return results in the same format as burstness(); with node
    #  labels as keys; values are tuples ([years...], [sigma...]).
    return {n: list(zip(*G.node_history(G.node_lookup[n], 'sigma').items()))
            for n in B.keys()}
