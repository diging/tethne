.. _working-with-corpora:

Working with Corpora
====================

Building a :class:`.Corpus` is the starting-point for working with bibliographic data
in Tethne. :class:`.Corpus` objects encapsulate and index :class:`.Paper`\s and
:ref:`corpora-featuresets`\, and mechanisms for analyzing data diachronically.

The :class:`.Corpus` class lives in :mod:`tethne.classes`\, but can be imported directly
from :mod:`tethne`\:

.. code-block:: python

   >>> from tethne import Corpus

Creating Corpora
----------------

Minimally, a :class:`.Corpus` requires a set of :class:`.Paper`\s. 

.. code-block:: python

   >>> from tethne.readers import wos
   >>> papers = wos.read('/path/to/wosdata.txt')    # Load some data.

   >>> MyCorpus = Corpus(papers)
   
Indexing
````````
   
By default, :class:`.Paper`\s and their cited references are indexed by 'ayjid', an
identifier generated from the first-author, publication date, and journal name of each
entry. 

You can use alternate indexing fields for :class:`.Paper`\s and their cited references:

.. code-block:: python

   >>> MyCorpus = Corpus(papers, index_by='wosid', index_citation_by='ayjid')
      
These are (usually) your options for index fields for :class:`.Papers` (``index_by``):

==============  =============
Source          Fields
==============  =============
Web of Science  wosid, ayjid
Scopus          eid, ayjid
JSTOR DfR		doi, ayjid
==============  =============

It should be obvious that ``ayjid`` is a good option if you plan to integrate data from
multiple datasources. ``ayjid`` is your best option for ``index_citations_by``, unless
you're confident that all cited references include alternate identifiers (this is rare).

By default, a :class:`.Corpus` calls its own :func:`Corpus.index` method on instantiation.
This results in a few useful attributes:

=============       ======================================================================
Attribute           Type/Description
=============       ======================================================================
papers              A dictionary mapping :class:`.Paper` IDs onto :class:`.Paper` 
                    instances.
authors             A dictionary mapping author names onto lists of :class:`.Paper` IDs.
citations           A dictionary mapping citation IDs onto cited references (themselves
                    :class:`.Paper` instances), if data available.
papers_citing       A dictionary mapping citation IDs onto lists of citing 
                    :class:`.Paper`\s (by ID) in the dataset, if data available.
=============       ======================================================================

If the :class:`.Paper`\s in the :class:`.Corpus` contain cited references, then a 
featureset called ``citations`` will also be created.

Directly from data
``````````````````

All of the modules in :mod:`.readers` should include methods to generate a
:class:`.Corpus` directly from data:

* :func:`.dfr.read_corpus`
* :func:`.scopus.read_corpus`
* :func:`.wos.read_corpus`

.. _corpora-featuresets:

Featuresets
-----------

In Tethne, a feature is a scalar property of one or more document in a :class:`.Corpus`\.
The most straightforward example of a feature is a word, which can occur some number of
times ( >= 0 ) in a document.

A featureset is a set of data structures that describe the distribution of features 
over :class:`.Paper`\s in a corpus. For example, a :class:`.Corpus` might contain a
featureset describing the distribution of words or citations over its :class:`.Paper`\s.

In Tethne v0.6.0-beta, featuresets are simply dictionaries contained in the 
:class:`.Corpus`\' ``features`` attribute. Each featureset should contain the following
keys and values:

+-------------------+--------------------------------------------------------------------+
| Key               | Value Type/Description                                             |
+===================+====================================================================+
| ``index``         | Dictionary mapping integer IDs onto string representations of      |
|                   | features. For wordcounts, think of this as a vocabulary.           |
+-------------------+--------------------------------------------------------------------+
| ``features``      | Dictionary mapping :class:`.Paper` IDs onto sparse feature vectors |
|                   | (e.g. wordcounts). These vectors are lists of ( feature index,     |
|                   | value ) tuples.                                                    |
+-------------------+--------------------------------------------------------------------+
| ``counts``        | Dictionary mapping feature indices (in ``index``) onto the sum of  |
|                   | values from ``features``. For wordcounts, for example, this is the |
|                   | total number of times that a word occurs in the :class:`.Corpus`\. |
+-------------------+--------------------------------------------------------------------+
| ``documentCounts``| Dictionary mapping feature indices (in ``index``) onto the number  |
|                   | of :class:`.Paper`\s in which the feature occurs (e.g. the number  |
|                   | of documents containing that word).                                |
+-------------------+--------------------------------------------------------------------+

The following methods in :class:`.Corpus` are useful for working with featuresets:

.. currentmodule:: tethne.classes.corpus

.. autosummary::
   
   Corpus.abstract_to_features
   Corpus.add_features
   Corpus.apply_stoplist
   Corpus.feature_counts
   Corpus.feature_distribution
   Corpus.filter_features
   Corpus.plot_distribution
   Corpus.transform
                        