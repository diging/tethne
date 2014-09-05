"""
Methods for analyzing :class:`.Corpus` objects.

.. autosummary::
   :nosignatures:
   
   burstness
   feature_burstness
   plot_burstness
   plot_sigma
   sigma
   
"""

import networkx
import numpy
from ..networks.helpers import top_cited

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

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

    def alpha(i):
        return (n/T)*(s**i)

    def tau(i,j):
        if j > i:
            return (j-i)*gamma*numpy.log(n)
        return 0.

    def f(j,x):
        return alpha(j) * numpy.exp(-1. * alpha(j) * x)

    def C(j,t):
        if j == 0 and t == 0:
            return 0.
        elif t == 0:
            return numpy.inf
        return ( -1.* numpy.log(f(j,X[t])) ) + \
                numpy.min( [ C_values[l,t-1] + tau(l,j) for l in xrange(k) ] )

    T = float(numpy.sum(X))
    n = len(X)
    C_values = numpy.zeros((k,n))
    for j in xrange(k):
        for t in xrange(len(X)):
            C_values[j,t] = C(j,t)
            
    states = []
    for t in xrange(n):
        state = numpy.argmin(C_values[:,t])
        states.append(state)

    return states

def _top_features(corpus, feature, topn=20, perslice=False, axis='date'):
    if perslice:
        top = []
        for key, papers in corpus.get_slices(axis).iteritems():
            scounts = corpus.feature_counts(feature, key, axis,
                                                documentCounts=True)
            scvalues = numpy.array(scounts.values())
            top += [scounts.keys()[c] for c in scvalues.argsort()[-topn:][::-1]]
    else:
        counts = corpus.features[feature]['counts']
        cvalues = numpy.array(counts.values())
        top = [ counts.keys()[c] for c in cvalues.argsort()[-topn:][::-1] ]
    return top

def plot_burstness(corpus, feature=None, k=5, topn=20, perslice=False,
                                flist=None, normalize=True, fig=None, **kwargs):
    """
    Generate a figure depicting burstness profiles for ``feature``.
    
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
    fig : :class:`matplotlib.figure.Figure`
        (default: None) You may provide a Figure instance if you wish. 
        Otherwise, a new figure is generated.
    kwargs : kwargs
        Parameters for burstness automaton HMM.
        
    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
    
    Examples
    --------
    
    .. code-block:: python
    
       >>> from tethne.analyze.corpus import burstness
       >>> fig = plot_burstness(corpus, 'citations', topn=2, perslice=True)
       >>> fig.savefig('~/burstness.png')
       
    Years prior to the first occurrence of each feature are grayed out. Periods
    in which the feature was bursty are depicted by colored blocks, the opacity
    of which indicates burstness intensity.
    
    .. figure:: _static/images/burstness.png
       :width: 600
       :align: center

    """
    if feature is None:
        raise ValueError('No feature specified.')
        
    B = burstness(corpus, feature, k=k, topn=topn, perslice=perslice,
                                flist=flist, normalize=normalize, **kwargs)
    
    color = kwargs.get('color', 'red')
    
    # Get width based on slices.
    years = sorted(corpus.axes['date'].keys())
    width = years[1] - years[0]
    height = 1.0
    
    if fig is None:
        fig = plt.figure(figsize=(10,len(B)/4.))

    f = 1
    axes = {}
    for key, value in B.iteritems():
        x,y = value
        ax = fig.add_subplot(len(B),1,f) 
        f+=1
        ax.set_yticks([])
        ax.set_xbound(min(years), max(years) + 1)
        
        if not f == len(B)+1:   # Only show xticks on the bottom subplot.
            ax.set_xticklabels([])
    
        # Block out years until first occurrence of feature.
        rect = mpatches.Rectangle( (min(years),0), sorted(x)[1]-min(years),
                                        height, fill=True, linewidth=0.0    )
        rect.set_facecolor('black')
        rect.set_alpha(0.3)
        ax.add_patch(rect)
        
        # Add a rectangle for each year, shaded according to burstness state.
        for d in xrange(min(x), max(x)):
            try:
                i = x.index(d)
            except ValueError:
                continue

            xy = (d, 0.)
        
            state = y[i]
            rect = mpatches.Rectangle(  xy, width, height, fill=True,
                                                           linewidth=0.0    )
            rect.set_facecolor(color)
            rect.set_alpha(state)
            ax.add_patch(rect)
        
        ax.set_ylabel(  key, rotation=0,
                             horizontalalignment='right',
                             verticalalignment='center'   )
    plt.subplots_adjust(left=0.5)
    fig.tight_layout(h_pad=0.25)
    
    return fig

def burstness(corpus, feature=None, k=5, topn=20, perslice=False,
                      flist=None, normalize=True, **kwargs):
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
    
    if feature is None:
        raise ValueError('No feature specified.')

    if flist is None:
        top = _top_features(corpus, feature, topn=topn, perslice=perslice)
    else:
        lookup = {v:k for k,v in corpus.features[feature]['index'].iteritems()}
        top = []
        for f in flist: # Get feature indices.
            try:    # Ignore features that don't exist.
                top.append(lookup[f])
            except KeyError:
                pass

    B = {}
    for f in top:   # top is a list of feature indices.
        feat = corpus.features[feature]['index'][f]
        B[feat] = feature_burstness(corpus, feature, f, k=k,
                                            normalize=normalize, **kwargs)
    return B

def feature_burstness(corpus, feature=None, findex=None, k=5, normalize=True, **kwargs):
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
    
    if feature is None:
        raise ValueError('No feature specified.')
    
    # Get time-intervals between occurrences.
    last = min(corpus.axes['date'].keys())-1
    dates = [last]    # Pad start.
    X_ = [1.]
    for y,s_ in corpus.get_slices('date').iteritems():
        this = []
        for p in s_:
            try:    # Not all papers have features.
                f_ = zip(*corpus.features[feature]['features'][p])[0]
                if findex in f_:
                    this.append(p)

            except KeyError:
                continue

        N = len(this)

        if N == 0:
            continue
        if y == last + 1:
            for n_ in xrange(N):
                X_.append(1./float(N))
                dates.append(y)
        else:
            X_.append(float(y - last))
            dates.append(y)
        last = int(y)

    # Get optimum state sequence.
    st = _forward(numpy.array(X_)*100, **kwargs)

    # Bin by date.
    A = {}
    for i in xrange(len(X_)):
        d = dates[i]
        if i not in A:
            A[d] = []
        A[d].append(st[i])

    # Get mean burstness for each year.
    for key, values in A.iteritems():
        A[key] = numpy.mean(values)

    # Normalize.
    if normalize:
        A_ = { key:float(v)/k for key,v in A.iteritems() }
    else: A_ = A

    D = sorted(A.keys())
    return D, [ A_[d] for d in D ]


def plot_sigma(G=None, corpus=None, feature=None, topn=20, sort_by='max', perslice=False,
                                                flist=None, fig=None, **kwargs):
    """
    Plot sigma values for the ``topn`` most influential nodes.
    
    Parameters
    ----------
    G : :class:`.GraphCollection`
    corpus : :class:`.Corpus`
    feature : str
        Name of a featureset in `corpus`.
    topn : int or float {0.-1.}
        (default: 20) Number (int) or percentage (float) of top-occurring 
        features to return. If ``flist`` is provided, this parameter is ignored.
    sort_by : str
        (default: 'max') Criterion for selecting ``topn`` nodes.
    perslice : bool
        (default: False) If True, loads ``topn`` features per slice. Otherwise,
        loads ``topn`` features overall. If ``flist`` is provided, this
        parameter is ignored.
    flist : list
        List of nodes. If provided, ``topn`` and ``perslice`` are ignored.
    fig : :class:`matplotlib.figure.Figure`
        (default: None) You may provide a Figure instance if you wish. 
        Otherwise, a new figure is generated.
    
    Returns
    -------
    fig : :class:`matplotlib.figure.Figure`
    G : :class:`.GraphCollection`
        A co-citation graph collection, updated with ``sigma`` node attributes.
    
    Examples
    --------
    
    Assuming that you have a :class:`.Corpus` (``G``) sliced by ``'date'`` and a
    co-citation :class:`.GraphCollection` (``corpus``)...
    
    .. code-block:: python
    
       >>> from tethne.analyze.cocitation import plot_sigma
       >>> fig,G = plot_sigma(G, corpus, topn=5, perslice=True)
       >>> fig.savefig('~/sigma_plot.png')
    
    In this figure, the top 5 most sigma-influential nodes in each slice are
    shown. Red bands indicate periods in which each paper was influential; 
    opacity indicates the intensity of sigma (normalized by the highest value in
    the plot). The period prior to the first instance of each node is grayed
    out.
    
    .. figure:: _static/images/sigma_plot.png
       :width: 600
       :align: center
    """
    if G is None:
        raise ValueError('No GraphCollection specified.')
    
    
    if feature is None:
        raise ValueError('No feature specified.')
        
    if corpus is None:
        raise ValueError('No corpus specified.')                
    
    G = sigma(G, corpus, feature)
    nodes = G.nodes()

    color = kwargs.get('color', 'red')
    
    years = sorted(corpus.axes['date'].keys())
    width = years[1] - years[0] # Get width based on slices.
    height = 1.0
    
    # Get node histories for sigma.
    histories = {}
    if flist is not None:
        nodes = flist
    
    for node in nodes:
        histories[node] = G.node_history(node, 'sigma')
    
    if flist is not None:
        these_nodes = flist     # Use provided list of nodes.
    else:
        # Get only the topn most significant papers.
        include = []
        if sort_by == 'max':
            if perslice:    # Get topn per slice.
                vals = {}
                norm_by = 0.
                
                # Organize values in a way that makes selection easier.
                for node in nodes:
                    if max(histories[node].values()) == 0.:
                        continue
                    for year,val in histories[node].iteritems():
                        try:
                            vals[year][node] = val
                        except KeyError:
                            vals[year] = { node:val }
            
                # Get the maximum values for each slice.
                for year in vals.keys():
                    vals_ = numpy.array(vals[year].values())
                    indices = vals_.argsort()[-topn:][::-1]
                    include += [ vals[year].keys()[i] for i in indices ]
                    if numpy.max(vals_) > norm_by:
                        norm_by = numpy.max(vals_)

            else:   # Get topn overall.
                maxes = numpy.array([ max(v.values()) for v
                                        in histories.values() ])
                indices = maxes.argsort()[-topn:][::-1]
                include = [ histories.keys()[i] for i in indices ]
                norm_by = numpy.max(maxes)

        # Nodes to include.
        these_nodes = [ node for node in nodes
                            if max(histories[node].values()) > 0
                                and node in include ]

    if fig is None: # Create a new Figure instance.
        fig = plt.figure(figsize=(10,len(these_nodes)/4.))

    # Plot!
    f = 1   # Current subplot.
    axes = {}
    x_min = min([min(v.keys()) for v in histories.values()])

    for node in these_nodes:
        x = sorted(histories[node].keys())
        y = numpy.array([ histories[node][i] for i in x ])/norm_by

        ax = fig.add_subplot(len(these_nodes),1,f)
        f+=1
        ax.set_yticks([])
        ax.set_xbound(x_min, max(years)+1)
        
        # Only show xticks on the bottom subplot.
        if not f == len(these_nodes) + 1:
            ax.set_xticklabels([])

        # Block out years until first occurrence of feature.
        rect = mpatches.Rectangle( (min(years),0), sorted(x)[0]-min(years),
                                        height, fill=True, linewidth=0.0    )
        rect.set_facecolor('black')
        rect.set_alpha(0.1)
        ax.add_patch(rect)
        
        # Add a rectangle for each year, shaded according to burstness state.
        for d in xrange(min(x), max(x)):
            try:    # May not have values for all years.
                i = x.index(d)
            except ValueError:
                continue

            xy = (d, 0.)
        
            state = y[i]
            rect = mpatches.Rectangle(  xy, width, height, fill=True,
                                                           linewidth=0.0    )
            rect.set_facecolor(color)
            rect.set_alpha(min(state + 0.1, 1.0))
            ax.add_patch(rect)
        
        ax.set_ylabel(  G.node_index[node], rotation=0,
                             horizontalalignment='right',
                             verticalalignment='center'   )

    plt.subplots_adjust(left=0.5)
    fig.tight_layout(h_pad=0.25)
    return fig

def sigma(G, corpus=None, feature=None, **kwargs):
    """
    Calculate sigma (from `Chen 2009 <http://arxiv.org/pdf/0904.1439.pdf>`_) for
    all of the nodes in a :class:`.GraphCollection`\.
    
    You can set parameters for burstness estimation using ``kwargs``:
    
    =========   ================================================================
    Parameter   Description
    =========   ================================================================
    s           Scaling parameter ( > 1.)that controls graininess of burst 
                detection. Lower values make the model more sensitive. Defaults
                to 1.1.
    gamma       Parameter that controls the 'cost' of higher burst states.
                Defaults to 1.0.
    k           Number of burst states. Defaults to 5.
    =========   ================================================================
    
    Parameters
    ----------
    G : :class:`.GraphCollection`
    corpus : :class:`.Corpus`
    feature : str
        Name of a featureset in `corpus`.
    
    Returns
    -------
    G : :class:`.GraphCollection`
        A graph collection updated with ``sigma`` node attributes.
        
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
    
    if feature is None:
        raise ValueError('No feature specified.')
        
    if corpus is None:
        raise ValueError('No corpus specified.')      
    
    nodes = G.node_lookup.keys()

    B = burstness(corpus, feature, flist=nodes, **kwargs)
    B_ = {}
    for key, values in B.iteritems():
        dates,bursts = values
        B_[key] = { dates[i]:bursts[i] for i in xrange(len(dates)) }

    for key in sorted(G.graphs.keys()):
        centrality = networkx.betweenness_centrality(G[key])
        sigma = {}
        for n in G[key].nodes():
            n_ = G.node_index[n]
            sigma[n] = ( ( centrality[n] + 1 ) ** B_[n_][key] ) - 1.

        # Update graph.
        networkx.set_node_attributes(G[key], 'sigma', sigma)
        networkx.set_node_attributes(G[key], 'centrality', centrality)

    return G