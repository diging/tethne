from corpus import burstness
import networkx
import numpy
from tethne import GraphCollection

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

def plot_sigma(G, corpus, topn=20, sort_by='max', perslice=False, flist=None,
                                                            fig=None, **kwargs):
    """
    Plot sigma values for the ``topn`` most influential nodes.
    
    Parameters
    ----------
    G : :class:`.GraphCollection`
        A co-citation graph collection.
    corpus : :class:`.Corpus`
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
    G = sigma(G, corpus)
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
            rect.set_alpha(state + 0.1)
            ax.add_patch(rect)
        
        ax.set_ylabel(  G.node_index[node], rotation=0,
                             horizontalalignment='right',
                             verticalalignment='center'   )

    plt.subplots_adjust(left=0.5)
    fig.tight_layout(h_pad=0.25)
    return fig, G

def sigma(G, corpus, **kwargs):
    """
    Calculate sigma (from `Chen 2009 <http://arxiv.org/pdf/0904.1439.pdf>`_) for
    all of the nodes in a cocitation :class:`.GraphCollection`\.
    
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
        A co-citation graph collection.
    corpus : :class:`.Corpus`
    
    Returns
    -------
    G : :class:`.GraphCollection`
        A co-citation graph collection, updated with ``sigma`` node attributes.
        
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
       >>> from tethne.analyze.cocitation import sigma
       >>> G = sigma(G, corpus)
       
       >>> # Visualize...
       >>> from tethne.writers import collection
       >>> collection.to_dxgmml(G, '~/cocitation.xgmml')
       
    In the visualization below, node and label sizes are mapped to ``sigma``,
    and border width is mapped to ``citations``.
    
    .. figure:: _static/images/cocitation_sigma2.png
       :width: 600
       :align: center

    """
    
    nodes = G.node_lookup.keys()

    B = burstness(corpus, 'citations', flist=nodes, **kwargs)
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