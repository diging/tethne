Quickstart
==========

Everything starts with bibliographic metadata. Tethne supports the ISI Web of
Science field-tagged format, JSTOR Data-for-Research XML format, and Zotero RDF.
For details on how to obtain metadata in the correct format, see
:ref:`gettingdata`.

You can find parsers in the :mod:`tethne.readers` module.

Let's parse a WoS field-tagged metadata file.

.. code-block:: python

   >>> from tethne.readers import wos
   >>> corpus = wos.read('/path/to/my/data.txt')

Now I have a :class:`.Corpus` instance with 500 :class:`.Paper` instances:

.. code-block:: python

   >>> len(corpus)
   500

A :class:`.Corpus` is basically just an indexed container for bibliographic
records. Each bibliographic record is represented by a :class:`.Paper` instance.

For more information about parsing bibliographic metadata, see :ref:`parsing`.

--------------

Network-building methods are available in :mod:`tethne.networks`\. You can
create a :func:`.coauthors` network like this:

.. code-block:: python

   >>> from tethne.networks import coauthors
   >>> coauthor_graph = coauthors(corpus)

All of Tethne's graph-building methods return :ref:`networkx.Graph <networkx:graph>` objects.
For more information, see the `NetworkX documentation
<https://networkx.github.io/>`_. The upshot is that you can use any of the
`algorithms
<http://networkx.readthedocs.io/en/networkx-1.11/reference/algorithms.html>`_
in NetworkX to analyze your graphs!

If you're using WoS data (with citations), you can also build citation-based
graphs (see :mod:`.networks.papers`\). Here's a static co-citation graph from a
:class:`.Corpus`:

.. code-block:: python

   >>> from tethne.networks import cocitation
   >>> cocitation_graph = cocitation(corpus, min_weight=3)

``min_weight=3`` means that a pair of papers must be co-cited three times to be
included in the network.

To create a time-variant coauthor network, use a :class:`.GraphCollection`\.

.. code-block:: python

   >>> from tethne import GraphCollection
   >>> coauthor_collection = GraphCollection(corpus, coauthors)
   >>> coauthor_collection.node_distribution()
   {1980: 32,
    1981: 26,
    1982: 24,
    1983: 26,
    1984: 20,
    1985: 30,
    1986: 35,
    1987: 49,
    1988: 60,
    1989: 66,
    1990: 69,
    1991: 85,
    1992: 82,
    1993: 91,
    1994: 110}

For more information about building graphs from bibliographic metadata,
see :ref:`graphs`.

--------------

You can export a graph for visualization in `Cytoscape <http://cytoscape.org>`_
or `Gephi <http://gephi.org>`_ using :mod:`tethne.writers`\:

.. code-block:: python

   >>> from tethne.writers.graph import to_graphml
   >>> to_graphml(coauthor_graph, '/path/to/my/graph.graphml')

For more information about exporting graphs, see :ref:`serialization`.
