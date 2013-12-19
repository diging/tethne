Tutorial
========

Installation
------------

Download & install the latest version of Tethne from our GitHub repository:

.. code-block:: bash

   $ git clone https://github.com/diging/tethne.git
   $ cd tethne
   $ pip install ./tethne

Quickstart
----------

After starting Python, import Tethne modules with:

.. code-block:: python

   >>> import tethne.readers as rd
   >>> import tethne.networks as nt
   >>> import tethne.analyze as az
   >>> import tethne.writers as wr

To parse some data from the Web of Science, use the tethne.readers.wos module.

.. code-block:: python

   >>> wos_list = rd.wos.parse_wos("/Path/To/Data.txt")  # Field-tagged data.
   >>> papers = rd.wos2meta(wos_list)
   >>> papers[0]
   <tethne.data.Paper instance at 0x1015ed200>

You can then generate a network using methods from the tethne.networks
subpackage. For example, to build a bibliographic coupling network:

.. code-block:: python

   >>> BC = nt.citations.bibliographic_coupling(papers)
   >>> BC
   <networkx.classes.graph.Graph object at 0x101b4fe50>

NetworkX provides algorithms_ for graph analysis. To generate 
betweenness-centrality values for each node, try:

.. _algorithms: http://networkx.github.io/documentation/networkx-1.7/reference/algorithms.html

.. code-block:: python

   >>> import networks as nx
   >>> b_centrality = nx.betweenness_centrality(BC)
   >>> nx.set_node_attributes(BC, 'betweenness', b_centrality)
   >>> BC.nodes(data=True)[0]
   ('BRADSHAW 1965 ADV GENET', {'betweenness': 0.12345})

You can then export your network for visualization using one of the methods
in tethne.writers. For example, to generate a simple interaction file (SIF):

.. code-block:: python

   >>> wr.graph.to_sif(BC, '/Path/to/Output/File')


Step-By-Step Guide
------------------

.. toctree::

   tutorial.getting_data
   tutorial.readers
   tutorial.networks
   tutorial.analyze
   tutorial.writers
   tutorial.collections
   tutorial.cocitation
   tutorial.vsm