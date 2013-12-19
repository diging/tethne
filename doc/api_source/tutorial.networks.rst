tethne.networks: Creating Bibliographic Networks
================================================

There are many different network models that can be used to describe bibliographic data. These can be
roughly divided into two categories: networks that describe relationships among documents, 
and networks that describe relationships among the authors of those documents. Each of these is
described in turn, below.

Once you have collected_ and parsed_ your bibliographic data, you're ready to build networks.

.. _collected: tutorial.getting_data
.. _parsed: tutorial.readers

First, import the :mod:`.networks` module.

.. code-block:: python

   >>> import tethne.networks as nt

Networks of Documents
---------------------

Methods for building networks in which vertices represent documents are provided in the :mod:`.networks.citations` module. 

Direct-Citation Graphs
``````````````````````

Direct-citation graphs are `directed acyclic graphs`__ in which vertices are documents, and each 
(directed) edge represents a citation of the target paper by the source paper. The 
:func:`.networks.citations.direct_citation` method generates both a global citation graph, which 
includes all cited and citing papers, and an internal citation graph that describes only citations 
among papers in the original dataset.

.. _dag: http://en.wikipedia.org/wiki/Directed_acyclic_graph

__ dag_

To generate direct-citation graphs, use the :func:`.networks.citations.direct_citation` method.
Note the size difference between the global and internal citation graphs.

.. code-block:: python

   >>> gDC, iDC = nt.citations.direct_citation(papers)
   >>> len(gDC)
   5998
   >>> len(iDC)
   163

Bibliographic Coupling
``````````````````````

Two papers are **bibliographically coupled** when they both cite the same, third, paper. You 
can generate a bibliographic coupling network using the :func:`.networks.citations.bibliographic_coupling`
method.

.. code-block:: python

   >>> BC = nt.citations.bibliographic_coupling(papers)
   >>> BC
   <networkx.classes.graph.Graph object at 0x102eec710>

Especially when working with large datasets, or disciplinarily narrow literatures, it is 
usually helpful to set a minimum number of shared citations required for two papers to be 
coupled. You can do this by setting the **threshold** parameter.

.. code-block:: python

   >>> BC = nt.citations.bibliographic_coupling(papers, threshold=1)
   >>> len(BC.edges())
   1216
   >>> BC = nt.citations.bibliographic_coupling(papers, threshold=2)
   >>> len(BC.edges())
   542

Co-Citation Networks
````````````````````

A **cocitation network** is a network in which vertices are papers, and edges indicate that two papers were cited 
by the same third paper. CiteSpace_ is a popular desktop application for co-citation analysis, and you can read 
about the theory behind it here_.

.. _CiteSpace: http://cluster.cis.drexel.edu/~cchen/citespace/
.. _here: http://cluster.cis.drexel.edu/~cchen/citespace/doc/jasist2006.pdf

You can generate a co-citation network using the :func:`.networks.citations.cocitation` method:

.. code-block:: python

   >>> CC = nt.citations.cocitation(papers)
   >>> CC
   <networkx.classes.graph.Graph object at 0x102eec790>

For large datasets, you may wish to set a minimum number of co-citations required for an edge between two papers.
Keep in mind that all of the references in a single paper are co-cited once, so a threshold of at least 2 is
prudent. Note the dramatic decrease in the number of edges when the threshold is changed from 2 to 3.

.. code-block:: python

   >>> CC = nt.citations.cocitation(papers, threshold=2)
   >>> len(CC.edges())
   8889
   >>> CC = nt.citations.cocitation(papers, threshold=3)
   >>> len(CC.edges())
   1493


