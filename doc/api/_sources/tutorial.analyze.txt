Analyzing Bibliographic Networks
================================

All networks in Tethne are 
`NetworkX Graphs <http://networkx.lanl.gov/reference/classes.graph.html>`_. 
This means means that you can use the rich suite of 
`algorithms <http://networkx.github.io/documentation/latest/reference/algorithms.html>`_
provided by NetworkX to analyze your bibliographic networks.

Analyzing individual networks
-----------------------------

If you built your network directly from a list of :class:`.Paper`\, you can import
and use NetworkX directly.

To calculate the betweenness-centrality of all of the nodes in a bibliographic
coupling network, for example, use:

.. code-block:: python

   >>> # Parse your data:
   >>> import tethne.readers as rd
   >>> wos_list = rd.wos.parse_wos("/Path/to/savedrecs.txt")
   >>> papers = rd.wos.rad(wos_list)

   >>> # Build a bibliographic coupling network:
   >>> import tethne.networks as nt
   >>> BC = nt.papers.bibliographic_coupling(papers)

   >>> # Use the NetworkX betweenness-centrality algorithm:
   >>> import networkx as nx
   >>> btw = nx.betweenness_centrality(G)
   >>> btw
   {'a': 0.0, 'c': 0.0, 'b': 0.6666666666666666, 'd': 0.0}
   
To add the betweenness-centrality values to your network as node attributes...

.. code-block:: python

   >>> nx.set_node_attributes(BC, 'betweenness', btw)

You can find a complete list of graph analysis algorithms in the `NetworkX
documentation 
<http://networkx.github.io/documentation/latest/reference/algorithms.html>`_.

A few additional methods internal to Tethne can be found in the :mod:`.analyze.graph`
module.

Analyzing a :class:`GraphCollection`
------------------------------------

The :mod:`.analyze.collection` sub-package provides mechanisms for analyzing an entire
:class:`.GraphCollection`\. Most NetworkX algorithms are accessible via
:func:`.analyze.collection.algorithm`\. To calculate betweenness centrality for an
entire :class:`.GraphCollection`\, for example, use:

.. code-block:: python

   >>> import tethne.analyze as az
   >>> BC = az.collection.algorithm(C, 'betweenness_centrality')
   >>> print BC[0]
   {1999: 0.010101651117889644,
   2000: 0.0008689093723107329,
   2001: 0.010504898852426189,
   2002: 0.009338654511194512,
   2003: 0.007519105636349891}
   
For more information, see the :mod:`.analyze.collection` sub-package.

Methods
```````

.. autosummary::

   tethne.analyze.collection.algorithm
   tethne.analyze.collection.connected
   tethne.analyze.collection.edge_history
   tethne.analyze.collection.node_history
   tethne.analyze.collection.node_global_closeness_centrality