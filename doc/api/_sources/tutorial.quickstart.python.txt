Quickstart (Python)
===================

After starting Python, import Tethne modules with:

.. code-block:: python

   >>> import tethne.readers as rd

To parse some data from the Web of Science, use the :mod:`tethne.readers.wos` module. See 
the :class:`.Paper` class for more information about what Tethne extracts from your WoS 
data.

.. code-block:: python

   >>> papers = rd.wos.read("/Path/To/FirstDataSet.txt")
   >>> papers[0]
   <tethne.data.Paper instance at 0x1015ed200>

You can either generate a network directly from your data using the methods in
:mod:`tethne.networks.wos` , or you can package your data in a :class:`.DataCollection`
for comparative or longitudinal analysis. If you want to generate a dynamic network, then
use a :class:`.DataCollection` .

Simple Networks
---------------

To generate a single network directly from your data, use the :mod:`tethne.networks.wos` 
module. For example, to build a bibliographic coupling network:

.. code-block:: python

   >>> import tethne.networks as nt
   >>> BC = nt.citations.bibliographic_coupling(papers)
   >>> BC
   <networkx.classes.graph.Graph object at 0x101b4fe50>

NetworkX provides 
`algorithms 
<http://networkx.github.io/documentation/networkx-1.7/reference/algorithms.html>`_ 
for graph analysis. To generate betweenness-centrality values for each node, try:

.. code-block:: python

   >>> import networkx as nx
   >>> b_centrality = nx.betweenness_centrality(BC)
   >>> nx.set_node_attributes(BC, 'betweenness', b_centrality)
   >>> BC.nodes(data=True)[0]
   ('BRADSHAW 1965 ADV GENET', {'betweenness': 0.12345})

You can then export your network for visualization using one of the methods
in :mod:`tethne.writers` . For example, to generate a simple interaction file (SIF):

.. code-block:: python

   >>> import tethne.writers as wr
   >>> wr.graph.to_sif(BC, '/Path/to/Output/File')

Sliced Networks for Comparative or Longitudinal Analysis
--------------------------------------------------------

Especially if you want to create a dynamic network (a network that changes over time), use
a :class:`.DataCollection` to organize your data.

To create a :class:`.DataCollection` :

.. code-block:: python

   >>> from tethne.data import DataCollection, GraphCollection
   >>> D = DataCollection(papers)

You can then use the :func:`tethne.data.DataCollection.slice` method to slice your data, 
e.g. by publication date. To use a 4-year sliding time-window:

.. code-block:: python

   >>> D.slice('date', 'time_window', window_size=4)
   
Create a :class:`.GraphCollection` to manage your graphs. :mod:`tethne.builders` provides
some helpful classes for creating a :class:`.GraphCollection` from a 
:class:`.DataCollection` . For example :class:`.authorCollectionBuilder` build a
:class:`.GraphCollection` using an author-based network (e.g. coauthorship networks) in
:mod:`tethne.networks.authors` :

.. code-block:: python

   >>> from tethne.builders import authorCollectionBuilder
   >>> builder = authorCollectionBuilder(D)
   >>> C = builder.build('date', 'coauthors')

To write `dynamic XGMML <https://code.google.com/p/dynnetwork/wiki/DynamicXGMML>`_
for visualization in `Cytoscape <http://cytoscape.org>`_, use the writing methods in 
:mod:`tethne.writers.collection` :

   >>> import tethne.writers as wr
   >>> wr.collection.to_dxgmml(C, '/Path/to/Network.xgmml')