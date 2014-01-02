Analyzing Bibliographic Networks
================================

All of the network-building_ functions in Tethne return NetworkX_
:class:`.Graph` objects. This means that you can use the rich suite of 
algorithms_ provided by NetworkX to analyze your bibliographic networks.

.. _network-building: tutorial.networks.html
.. _NetworkX: http://networkx.github.io

First, import the NetworkX module.

.. code-block:: python

   >>> import networkx as nx
   
To calculate the betweenness-centrality of all of the nodes in a bibliographic
coupling network, for example, use:

.. code-block:: python

   >>> import tethne.readers as rd
   >>> import tethne.networks as nt

   >>> # Parse your data:
   >>> wos_list = rd.wos.parse_wos("/Path/to/savedrecs.txt")
   >>> papers = rd.wos.wos2meta(wos_list)

   >>> # Build a bibliographic coupling network:
   >>> BC = nt.papers.bibliographic_coupling(papers)

   >>> # Use the NetworkX betweenness-centrality algorithm:
   >>> btw = nx.betweenness_centrality(G)
   >>> btw
   {'a': 0.0, 'c': 0.0, 'b': 0.6666666666666666, 'd': 0.0}
   
To add the betweenness-centrality values to your network as node attributes...

.. code-block:: python

   >>> nx.set_node_attributes(BC, 'betweenness', btw)

You can find a complete list of graph analysis algorithms in the NetworkX
documentation_.

.. _documentation: http://path/to/nx/docs

tethne.analyze subpackage
-------------------------

The tethne.analyze_ sub-package provides additional analysis methods not
provided by NetworkX. The sub-package is comprised of three modules: 
tethne.analyze.collection_, tethne.analyze.graph_, and tethne.analyze.workflow_. 
The use of .collection_ to analyze time-sliced networks represented by a 
:class:`.GraphCollection` is covered in tutorial.collections_. The methods in 
.workflow_ are described in tutorial.workflow_.

.. _tethne.analyze: tethne.analyze.html
.. _tethne.analyze.collection: tethne.analyze.html#collection-module
.. _tethne.analyze.graph: tethne.analyze.html#graph-module
.. _tethne.analyze.workflow: tethne.analyze.html#workflow-module
.. _tutorial.collections: tutorial.collections.html
.. _tutorial.workflow: tutorial.workflow.html

tethne.analyze.graph module
```````````````````````````

tethne.analyze.graph_ contains graph analysis functions not provided by
NetworkX. To use this module, first import it with:

.. _tethne.analyze.graph: tethne.analyze.html#graph-module

.. code-block:: python

   >>> import tethne.analyze.graph as azg

Global Closeness Centrality
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Closeness centrality is based on the average shortest path length
between a focal node and all other nodes in the network. For multi-component
graphs, conventional closeness centrality metrics fail because it is not
possible to traverse between a given node and all other nodes in the graph.
Global closeness centrality is calculated in a way that yields values even for
multi-component graphs. For an example of how global closeness centrality can
be used to analyze co-authorship networks, see the blog post here_.

.. _here: http://devo-evo.lab.asu.edu/????

To calculate the global closeness centrality of a single node, building on the
bibliographic coupling network generated in the previous section, use
:func:`.node_global_closeness_centrality` :

.. code-block:: python

   >>> ngbc = azg.node_global_closeness_centrality(BC, 'SMITH 1975 EVOLUTION')
   >>> ngbc
   0.154245
   
You can calculate the global closeness centrality of all nodes in the network
using :func:`.global_closeness_centrality` . 

.. code-block:: python

   >>> GBC = azg.global_closeness_centrality(BC)
   >>> GBC
   {'a': 0.0, 'c': 0.0, 'b': 0.6666666666666666, 'd': 0.0}