Quickstart
==========

Load some data
--------------

Assuming that you have a JSTOR DfR dataset (in XML format) containing some wordcount
data unzipped at ``/path/to/my/dataset``, create a :class:`.Corpus` with:

.. code-block:: python

   >>> from tethne.readers import dfr
   >>> C = dfr.read_corpus('/path/to/my/dataset', 'uni')
   
Or if you're working with data from the Web of Science, try:

.. code-block:: python

   >>> from tethne.readers import wos
   >>> C = dfr.read_corpus('/path/to/my/wosdata.txt')
   
Index your :class:`.Corpus` by publication date and journal using the 
:func:`tethne.classes.corpus.Corpus.slice` method.

.. code-block:: python

   >>> C.slice('date', method='time_period', window_size=5)
   >>> C.slice('jtitle')
   
Now use :func:`tethne.classes.corpus.Corpus.plot_distribution` to see how your 
:class:`.Paper`\s are distributed over time...

.. code-block:: python

   >>> C.plot_distribution('date')
   
.. figure:: _static/images/corpus_plot_distribution.png
   :width: 400
   :align: center

...or by both time and journal:
   
.. code-block:: python

   >>> C.plot_distribution('date', 'jtitle')   

.. figure:: _static/images/corpus_plot_distribution_2d.png
   :width: 600
   :align: center
   
Simple networks simply
----------------------
   
Network-building methods are in :mod:`.networks`\. You can create a coauthorship
network like this:

.. code-block:: python

   >>> from tethne.networks import authors
   >>> coauthors = authors.coauthors(C)
   
To introduce a temporal component, slice your :class:`.Corpus` and then create a :class:`.GraphCollection` (``cumulative=True`` means that the coauthorship network
will grow over time without losing old connections):

.. code-block:: python

   >>> C.slice('date', 'time_period', window_size=5, cumulative=True)	# 5-year bins.
   >>> from tethne import GraphCollection
   >>> G = GraphCollection().build(C, 'authors', 'coauthors')
   
If you're using WoS data (with citations), you can also build citation-based graphs (see
:mod:`.networks.papers`\). Here's a static co-citation graph from a :class:`.Corpus`:

.. code-block:: python

   >>> C.slice('date', 'time_period', window_size=5) 	# No need for `cumulative` here.
   >> from tethne.networks import papers
   >>> cocitation = papers.cocitation(C.all_papers(), threshold=2, topn=300)

``threshold=2`` means that papers must be co-cited twice, and ``topn=300`` means that
only the top 300 most cited papers will be included.

To see a time-variant co-citation network, build a :class:`.GraphCollection` just as
before:

.. code-block:: python

   >>> G = GraphCollection().build(C, 'papers', 'cocitation', threshold=2, topn=300)

Visualize your networks
-----------------------

You can export a graph for visualization in `Cytoscape <http://cytoscape.org>`_ using
 :mod:`.writers`\:

.. code-block:: python

   >>> from tethne.writers import graph
   >>> graph.to_graphml(coauthors, '/path/to/my/graph.graphml')
   
To visualize a :class:`.GraphCollection` as a dynamic graph in Cytoscape, export it using
:func:`.writers.collection.to_dxgmml`\:

.. code-block:: python

   >>> from tethne.writers import collection
   >>> collection.to_dxgmml(G, '/path/to/my/dynamicNetwork.xgmml')
   
