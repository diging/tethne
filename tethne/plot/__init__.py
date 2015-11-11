import networkx as nx
import warnings

from math import exp, log
from collections import defaultdict
from itertools import izip

from tethne.utilities import argmin, mean, argsort


def plot_burstness(corpus, B, **kwargs):
    """
    Generate a figure depicting burstness profiles for ``feature``.

    Parameters
    ----------
    B

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
    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise RuntimeError('This method requires the package matplotlib.')

    color = kwargs.get('color', 'red')

    # Get width based on slices.
    years = sorted(corpus.indices['date'].keys())
    width = years[1] - years[0]
    height = 1.0

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

        rect = mpatches.Rectangle((min(years), 0), sorted(x)[0]-min(years),
                                   height, fill=True, linewidth=0.0)
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
            rect = mpatches.Rectangle(xy, width, height,
                                      fill=True, linewidth=0.0)
            rect.set_facecolor(color)
            rect.set_alpha(state)
            ax.add_patch(rect)

        ax.set_ylabel(key, rotation=0,
                      horizontalalignment='right',
                      verticalalignment='center')
    plt.subplots_adjust(left=0.5)
    fig.tight_layout(h_pad=0.25)

    plt.show()


def plot_sigma(corpus, sigma, nodes=None, **kwargs):
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

    try:
        import matplotlib.pyplot as plt
        import matplotlib.patches as mpatches
    except ImportError:
        raise RuntimeError('This method requires the package matplotlib.')

    if nodes == 'all':
        nodes = sigma.keys()

    # Display parameters.
    color = kwargs.get('color', 'red')
    years = sorted(corpus.indices['date'].keys())
    width = years[1] - years[0] # Get width based on slices.
    height = 1.0

    sort_by = kwargs.get('sort_by', 'max')
    perslice = kwargs.get('perslice', False)
    topn = kwargs.get('topn', 20)

    if not nodes:
        # Get only the topn most significant papers.
        include = []
        if sort_by == 'max':
            if perslice:    # Get topn per slice.
                vals = {}
                norm_by = 0.

                # Organize values in a way that makes selection easier.
                for node, history in sigma.iteritems():
                    years, values = history
                    if max(values) == 0.:
                        continue
                    for year, val in zip(years, values):
                        if year not in vals:
                            vals[year] = {}
                        vals[year][node] = val

                # Get the maximum values for each slice.
                for year, node_values in vals.iteritems():
                    indices = argsort(node_values.values())[-topn:][::-1]
                    include += [node_values.keys()[i] for i in indices]
                    max_value = max(node_values.values())
                    if max_value > norm_by:
                        norm_by = max_value

            else:   # Get topn overall.
                maxes = [max(v[1]) for v in sigma.values() ]
                indices = argsort(maxes)[-topn:][::-1]
                include = [sigma.keys()[i] for i in indices]
                norm_by = max(maxes)

        # Nodes to include.
        nodes = [node for node, values in sigma.iteritems()
                 if max(values[1]) > 0 and node in include]

#     if fig is None: # Create a new Figure instance.
    fig = plt.figure(figsize=(10, len(nodes)/4.))

    # Plot!
    f = 1   # Current subplot.
    axes = {}

    # Earliest year for which we have values.
    x_min = min([min(years) for years, values in sigma.values()])

    for node in nodes:
        x_order = argsort(sigma[node][0])
        x = sorted(sigma[node][0])
        y = [sigma[node][1][i]/norm_by for i in x_order]

        ax = fig.add_subplot(len(nodes), 1, f)
        f+=1
        ax.set_yticks([])
        ax.set_xbound(x_min, max(years)+1)

        # Only show xticks on the bottom subplot.
        if not f == len(nodes) + 1:
            ax.set_xticklabels([])

        # Block out years until first occurrence of feature.
        rect = mpatches.Rectangle((x_min, 0), x[0] - x_min,
                                  height, fill=True, linewidth=0.0)
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
            rect = mpatches.Rectangle(xy, width, height,
                                      fill=True, linewidth=0.0)
            rect.set_facecolor(color)
            rect.set_alpha(state + 0.1)
            ax.add_patch(rect)

        ax.set_ylabel(node, rotation=0,
                      horizontalalignment='right',
                      verticalalignment='center')

    plt.subplots_adjust(left=0.5)
    fig.tight_layout(h_pad=0.25)
    plt.show()
