Co-citation Analysis
====================

.. warning:: This tutorial is incomplete for v0.5.0-alpha. Waiting on burstiness algorithm
			 in :mod:`.analyze`\.

Co-citation analysis gained popularity in the 1970s as a technique for "mapping"
scientific literatures, and for finding latent semantic relationships among technical
publications.

Two papers are co-cited if they are both cited by the same, third, paper. The standard
approach to co-citation analysis is to generate a sample of bibliographic records from a
particular field by using certain keywords or journal names, and then build a co-citation
graph describing relationships among their cited references. Thus the majority of papers
that are represented as nodes in the co-citation graph are **not** papers that responded
to the selection criteria used to build the dataset.

.. image:: _static/images/bibliocoupling/citationnetworks.png
   :width: 600
   :align: center
   
Our objective in this tutorial is to identify papers that bridge the gap between 
otherwise disparate areas of knowledge in the scientific literature. We rely on 
`Chen 2006 <http://cluster.cis.drexel.edu/~cchen/citespace/doc/jasist2006.pdf>`_ theory
of emergent change in scientific knowledge domains.

According to Chen, we can detect potentially transformative changes in scientific 
knowledge by looking for cited references that both (a) rapidly accrue citations, and (b)
have high betweenness-centrality in a co-citation network. It helps if we think of each
scientific paper as representing a "concept" (its core knowledge claim, perhaps), and a 
co-citation event as representing a proposition connecting two concepts in the
knowledge-base of a scientific field. If a new paper emerges that is highly co-cited with
two otherwise-distinct clusters of concepts, then that might mean that the field is
adopting new concepts and propositions in a way that is structurally radical for their
conceptual framework.

Getting Started
---------------

Before you begin, be sure to install the latest version of Tethne. Consult the
:ref:`installation` guide for details.

**If you run into problems**, don't panic. Tethne is under active development, and there
are certainly bugs to be found. Please report any problems, including errors in this
tutorial, via our `GitHub issue tracker 
<https://github.com/diging/tethne/issues?state=open>`_.

For this tutorial, you'll need some citation data from the ISI Web of Science. If this is 
your first time working with WoS citation data, check out :ref:`gettingdata`\. We'll
assume that you have downloaded a few sets of records from WoS, and stored them all in 
the same directory.

.. code-block:: python

   >>> datapath = '/path/to/my/data/directory'

Reading WoS Data
----------------

You can parse WoS data from one or multiple field-tagged data files, using the methods
in the :mod:`.readers` module. Since we're working with multiple data files, we'll
use the :mod:`.readers.wos.corpus_from_dir` method to parse the WoS data and create
a new :class:`.Corpus` called ``MyCorpus``.

.. code-block:: python

   >>> from tethne.readers import wos
   >>> MyCorpus = wos.corpus_from_dir(datapath)
   
``MyCorpus`` should contain some :class:`.Paper`\s, as well as some citations.

.. code-block:: python

   >>> print len(MyCorpus.papers)	# How many Papers?
   1859
   >>> print len(MyCorpus.citations)	# How many citations?
   57774

If you have fewer :class:`.Paper`\s than you expect, it is possible that some of the
records in your dataset were duplicates. If you don't have any citations, go back
and make sure that you downloaded full records with citations from the WoS database. See
:ref:`gettingdata`\.

Building a Co-citation GraphCollection
--------------------------------------

Slicing a Corpus
````````````````

.. code-block:: python

   >>> MyCorpus.slice('date', 'time_window', window_size=4)

.. code-block:: python

Time-variant co-citation graph
``````````````````````````````

.. code-block:: python

   >>> from tethne import GraphCollection
   >>> method_kwargs = { 'threshold': 2, 'topn': 100 }
   >>> G = GraphCollection().build(MyCorpus, 'date', 'papers', 'cocitation', method_kwargs=method_kwargs)

Analyzing the GraphCollection
-----------------------------

Betweenness centrality
``````````````````````

.. code-block:: python

   >>> from tethne.analyze import collection
   >>> bc = collection.algorithm(G, 'betweenness_centrality')
   
Burstiness
``````````

.. todo:: Write this section.

Sigma
`````

.. todo:: Write this section.

Visualization
-------------



