.. _parsingdata:

Parsing Bibliographic Data
==========================

.. note:: For instructions on acquiring bibliographic data from several sources,
          see :ref:`gettingdata`.

Tethne provides several parsing modules, located in :mod:`tethne.readers`. The
recommended pattern for parsing data is to import the parsing module
corresponding to your data type, and use its' ``read`` function to parse your
data. For example:

.. code-block:: python

   >>> from tethne.readers import wos
   >>> myCorpus = wos.read('/path/to/my/data.txt')

By default, ``read`` will return a :class:`.Corpus` object.

.. code-block:: python

   >>> myCorpus
   <tethne.classes.corpus.Corpus object at 0x1046aa7d0>

A :class:`.Corpus` is a collection of :class:`.Paper`\s that can be indexed in
a variety of ways. A :class:`.Corpus` behaves like a list of :class:`.Paper`\s:

.. code-block:: python

   >>> len(myCorpus)    # How many Papers do I have?
   500
   >>> myCorpus[0]      # Returns the first Paper.
   <tethne.classes.paper.Paper at 0x10bcde290>
   >>> myCorpus[-1]     # Returns the last Paper.
   <tethne.classes.paper.Paper at 0x103911f50>

Depending on which module you use, ``read`` will make assumptions about which
field to use as the primary index for the :class:`.Paper`\s in your dataset.
The default for Web of Science data, for example, is ``'wosid'`` (the value of
the ``UT`` field-tag).

.. code-block:: python

   >>> myCorpus.index_by
   'wosid'

If you'd prefer to index by a different field, you can pass the ``index_by``
parameter.

.. code-block:: python

   >>> myOtherCorpus = wos.read('/path/to/my/data.txt', index_by='doi')
   >>> myOtherCorpus.index_by
   'doi'

The following sections describe the behavior of each of the parsing modules.

.. contents::
   :local:
   :depth: 2

Web of Science
--------------

To parse a Web of Science field-tagged file, or a collection of field-tagged
files, use the :func:`.tethne.readers.wos.read` method.

To parse a single file, provide the path to that data file. For example:

   >>> from tethne.readers import wos
   >>> corpus = wos.read('/path/to/my/data.txt')


Parsing Several WoS Files
`````````````````````````

Often you'll be working with datasets comprised of multiple data files. The Web
of Science database only allows you to download 500 records at a time (because
they're dirty capitalists). You can use the **``read``** function to load a list
of ``Paper``s from a directory containing multiple data files.

The ``read`` function knows that your path is a directory and not a data file;
it looks inside of that directory for WoS data files.

   >>> corpus = wos.read('/Path/to/my/wos/data/dir')

JSTOR Data for Research
-----------------------

The DfR parsing module is :mod:`tethne.readers.dfr`.

   >>> from tethne.readers import dfr

The DfR reader works just like the WoS reader. To load a single dataset, provide
the path to the folder created when you unzipped your dataset download (it
should contain a file called ``citations.xml``).

   >>> corpus = dfr.read('/path/to/my/dfr', features=['uni'])

Whereas Corpora generated from WoS datasets are indexed by ``wosid`` by default,
Corpora generated from DfR datasets are indexed by ``doi``.

   >>> corpus.indexed_papers.keys()[0:10]    # The first 10 dois.
   ['10.2307/2418718',
    '10.2307/2258178',
    '10.2307/3241549',
    '10.2307/2416998',
    '10.2307/20000814',
    '10.2307/2428935',
    '10.2307/2418714',
    '10.2307/1729159',
    '10.2307/2407516',
    '10.2307/2816048']

But unlike WoS datasets, DfR datasets can contain wordcounts and N-grams in
addition to bibliographic data. ``read`` will find these extra data about your
Bibliographic records, and load them as
:class:`tethne.classes.feature.FeatureSet` instances.

   >>> corpus.features
   {'authors': <tethne.classes.feature.FeatureSet at 0x100434e90>,
    'citations': <tethne.classes.feature.FeatureSet at 0x10041b990>,
    'wordcounts': <tethne.classes.feature.FeatureSet at 0x107688750>}

Parsing Several DfR Files
`````````````````````````

Just like the WoS parser, the DfR ``read`` function can load several datasets
at once. Instead of providing a path to a single dataset, provide a path to a
directory containing several datasets. ``read`` will look for DfR datasets, and
load them all into a single :class:`.Corpus`\.

   >>> corpus = dfr.read('/path/to/many/datasets')

Zotero RDF
----------

The Zotero parsing module is :mod:`tethne.readers.zotero`.

   >>> from tethne.readers import zotero

The Zotero reader works just like the WoS and DfR readers. To load a single
dataset, provide the path to the folder created when you exported your Zotero
collection (it should contain a file with an ``.rdf`` extension).

   >>> corpus = zotero.read('/path/to/my/rdf/export')

Since RDF relies on `Uniform Resource Identifiers (URIs)
<https://en.wikipedia.org/wiki/Uniform_Resource_Identifier>`_, the default
indexing field for Zotero datasets is ``uri``.

   >>> corpus.indexed_papers.items()[0:5]    # The first 10 URIs.
   [('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC3527233/',
     <tethne.classes.paper.Paper at 0x10976dcd0>),
    ('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1513266/',
     <tethne.classes.paper.Paper at 0x109dbf050>),
    ('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2211313/',
     <tethne.classes.paper.Paper at 0x109712bd0>),
    ('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC2886068/',
     <tethne.classes.paper.Paper at 0x1095dc9d0>),
    ('http://www.ncbi.nlm.nih.gov/pmc/articles/PMC1914331/',
     <tethne.classes.paper.Paper at 0x1095dc5d0>)]

By default, the Zotero reader will attempt to extract text from any attached
files. In v1.0, Tethne extracts text from PDFs and plain-text files. These are
represented as :class:`tethne.classes.feature.StructuredFeatureSet`\s.

   >>> corpus.structuredfeatures
   {'pdf_text': <tethne.classes.feature.StructuredFeatureSet at 0x10ab206d0>}

Note that text extracted from PDF files will belong to a
:class:`.StructuredFeature` named 'pdf_text'. Text extracted from plain-text
files will belong to a :class:`.StructuredFeature` named 'plain_text'.

.. note:: Tethne uses `slate <https://pypi.python.org/pypi/slate>`_ to extract
          embedded text from PDFs. Tethne does NOT perform OCR.
