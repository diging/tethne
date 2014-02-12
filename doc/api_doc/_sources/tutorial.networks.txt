Creating Networks from Bibliographic Data
=========================================

.. sidebar:: Ready to Proceed?

   Once you have collected_  
   your bibliographic data, you're ready 
   to start building networks.

Parsing Data
------------

Methods for parsing bibliographic data are contained in the :mod:`.readers` module. 
Tethne parses bibliographic data into a list of :class:`.Paper` objects that can then
be used to generate networks.

Many (but not all) of the networks that Tethne can generate require citation data. The
current version of Tethne only supports citation data from the Web of Science, which can
be parsed using the :mod:`.readers.wos` module. For example:

.. code-block:: python

   >>> import tethne.readers as rd
   >>> papers = rd.wos.read("/Path/to/savedrecs.txt")

Tethne can also parse data from `JSTOR's
Data-for-Research portal <http://dfr.jstor.org>`_, using the :mod:`.readers.dfr` module.
Those data can be merged with a WoS dataset (see :func:`.readers.merge`\), or
used on their own to generate coauthor networks, with
:func:`.networks.authors.coauthors`\.

.. code-block:: python

   >>> import tethne.readers as rd
   >>> papers = rd.dfr.read("/Path/to/DfR")

Creating Networks
-----------------

There are many different network models that can be used to describe bibliographic data. 
These can be roughly divided into two categories: networks that describe relationships 
among documents, and networks that describe relationships among the authors of those 
documents. For specific methods, see :ref:`networks-of-documents` and 
:ref:`networks-of-authors`.

.. _collected: tutorial.getting_data.html
.. _parsed: tutorial.readers.html

All network-building methods can be found in the :mod:`.networks` module. ``nt`` is the
recommended namespace convention.

.. code-block:: python

   >>> import tethne.networks as nt

There are two main ways of using network-building methods:

1. Generating a single network directly from a list of :class:`.Paper` objects
``````````````````````````````````````````````````````````````````````````````

All methods in :mod:`tethne.networks` take lists of :class:`.Paper` as arguments. For
example:

.. code-block:: python

   >>> import tethne.readers as rd
   >>> papers = rd.wos.read("/Path/to/savedrecs.txt")
   >>> import tethne.networks as nt
   >>> BC = nt.papers.bibliographic_coupling(papers, threshold=2)
   
2. Generating a :class:`.GraphCollection` from a :class:`.DataCollection` 
`````````````````````````````````````````````````````````````````````````

This is useful in cases where you want to evaluate the evolution of network structure
over time, or compare networks generated using subsets of your data.

To generate a time-variant :class:`.GraphCollection`\, slice your 
:class:`.DataCollection` using the ``date`` field. In the example below, data are sliced
using a 4-year sliding time-window (for details about slicing, see 
:func:`tethne.data.DataCollection.slice`\).

.. code-block:: python

   >>> # Parse data.
   >>> import tethne.readers as rd
   >>> papers = rd.wos.read("/Path/To/FirstDataSet.txt")
   
   >>> # Create a DataCollection, and slice it.
   >>> from tethne.data import DataCollection, GraphCollection
   >>> D = DataCollection(papers)
   >>> D.slice('date', 'time_window', window_size=4)
   
   >>> # Build a GraphCollection using a network from tethne.networks.
   >>> from tethne.builders import authorCollectionBuilder
   >>> builder = authorCollectionBuilder(D)
   >>> C = builder.build('date', 'coauthors')
   
``C.keys()`` should now yield a list of publication dates in the original dataset.

A :class:`.DataCollection` can be sliced using any ``int`` or ``str`` field in the
:class:`.Paper` class. If you wish to compare networks generated from two WoS downloads,
for example, you could slice using the ``accession`` id:

   >>> # Parse data.
   >>> import tethne.readers as rd
   >>> papers = rd.wos.read("/Path/To/FirstDataSet.txt")
   >>> papers += rd.wos.read("/Path/To/SecondDataSet.txt")
   
   >>> # Create a DataCollection, and slice it.
   >>> from tethne.data import DataCollection, GraphCollection
   >>> D = DataCollection(papers)
   >>> D.slice('accession')
   
   >>> # Build a GraphCollection using a network from tethne.networks.
   >>> from tethne.builders import authorCollectionBuilder
   >>> builder = paperCollectionBuilder(D)
   >>> C = builder.build('date', 'cocitation', threshold=2)
   
``C.keys()`` should now yield two values, each an accession UUID.

.. _networks-of-documents:

Networks of Documents
---------------------

Methods for building networks in which vertices represent documents are provided in the 
:mod:`.networks.papers` module. 

.. autosummary::

   tethne.networks.papers.author_coupling
   tethne.networks.papers.bibliographic_coupling
   tethne.networks.papers.cocitation
   tethne.networks.papers.direct_citation

.. _networks-of-authors:

Networks of Authors
-------------------

Methods for building networks in which vertices represent authors are provided in the :mod:`.networks.authors` module. 

.. autosummary::

   tethne.networks.authors.author_cocitation
   tethne.networks.authors.author_coinstitution
   tethne.networks.authors.author_institution
   tethne.networks.authors.author_papers
   tethne.networks.authors.coauthors