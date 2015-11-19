
.. code:: python

   %matplotlib inline

.. code:: python

   from pprint import pprint
   import matplotlib.pyplot as plt

A Closer Look at Corpora
========================

A :class:`.Corpus` is a collection of :class:`.Paper`\ s with superpowers. Most
importantly, it provides a consistent way of indexing bibliographic
records. Indexing is important, because it sets the stage for all of the
subsequent analyses that we may wish to do with our bibliographic data.

In :ref:`parsingdata` we used the ``read`` function in
:mod:`tethne.readers.wos` to parse a collection of Web of Science
field-tagged data files and build a :class:`.Corpus`.

.. code:: python

   >>> from tethne.readers import wos
   >>> datapath = '/Users/erickpeirson/Downloads/datasets/wos'
   >>> corpus = wos.read(datapath)

In this notebook, we'll dive deeper into the guts of the :class:`.Corpus`,
focusing on indexing and and features.

Setting the primary indexing field: ``index_by``
================================================

The **primary indexing field** is the field that Tethne uses to identify
each of the :class:`.Paper`\ s in your dataset. Ideally, each one of the
records in your bibliographic dataset will have this field. Good
candidates include DOIs, URIs, or other unique identifiers.

Depending on which module you use, ``read`` will make assumptions about
which field to use as the primary index for the :class:`.Paper`\ s in your
dataset. The default for Web of Science data, for example, is
``'wosid'`` (the value of the ``UT`` field-tag).

   >>> 'The primary index field for the Papers in my Corpus is "%s"' % corpus.index_by
   The primary index field for the Papers in my Corpus is "wosid"

The primary index for your :class:`.Corpus` can be found in the
``indexed_papers`` attribute. ``indexed_papers`` is a dictionary that
maps the value of the indexing field for each :class:`.Paper` onto that
:class:`.Paper` itself.

   >>> corpus.indexed_papers.items()[0:10]   # We'll just show the first ten Papers, for the sake of space.
   [('WOS:000078288500016', <tethne.classes.paper.Paper at 0x10d886dd0>),
    ('WOS:000225242500007', <tethne.classes.paper.Paper at 0x10c1c9f50>),
    ('WOS:000074414100009', <tethne.classes.paper.Paper at 0x10d950890>),
    ('WOS:000268928200019', <tethne.classes.paper.Paper at 0x110506b10>),
    ('WOS:000305886800001', <tethne.classes.paper.Paper at 0x109516610>),
    ('WOS:000275757500014', <tethne.classes.paper.Paper at 0x10fbe6d50>),
    ('WOS:A1995RV72900015', <tethne.classes.paper.Paper at 0x10e162290>),
    ('WOS:000308634600013', <tethne.classes.paper.Paper at 0x108b14990>),
    ('WOS:000314781600006', <tethne.classes.paper.Paper at 0x1083a9350>),
    ('WOS:000220323300004', <tethne.classes.paper.Paper at 0x10c4e4290>)]

So if you know (in this case) the ``wosid`` of a :class:`.Paper`, you can
retrieve that :class:`.Paper` by passing the ``wosid`` to ``indexed_papers``:

   >>> corpus.indexed_papers['WOS:000321911200011']
   <tethne.classes.paper.Paper at 0x10760a490>

If you'd prefer to index by a different field, you can pass the
``index_by`` parameter to ``read``.

   >>> otherCorpus = wos.read(datapath, index_by='doi')
   >>> 'The primary index field for the Papers in this other Corpus is "%s"' % otherCorpus.index_by
   The primary index field for the Papers in this other Corpus is "doi"

If some of the :class:`.Paper`\ s lack the indexing field that you specified
with the ``index_by`` parameter, Tethne will automatically generate a
unique identifier for each of those ``Papers``. For example, in our
``otherCorpus`` that we indexed by ``doi``, most of the papers have
valid DOIs, but a few (#1, below) did not -- a nonsensical-looking
sequence of alphanumeric characters was used instead.

   >>> i = 0
   >>> for doi, paper in otherCorpus.indexed_papers.items()[0:10]:
   ...     print '(%i) DOI: %s \t ---> \t Paper: %s' % (i, doi.ljust(30), paper)
   ...     i += 1
   (0) DOI: 10.1007/s004420050317        	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x1080dd0d0>
   (1) DOI: 44a4e0d3fa05975610ae51e51b02fb3d 	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x107ddf1d0>
   (2) DOI: 10.1111/evo.12036           	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x10d9bb6d0>
   (3) DOI: 10.1111/nph.12388           	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x11059e090>
   (4) DOI: 10.1007/s00442-007-0712-4     	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x1197befd0>
   (5) DOI: 10.1684/ers.2012.0589        	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x122ea5510>
   (6) DOI: 10.1046/j.1365-2435.2002.00663.x 	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x10eebb250>
   (7) DOI: 10.1080/17550874.2011.577459   	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x109215750>
   (8) DOI: 10.1016/0378-1127(94)03497-K   	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x108655950>
   (9) DOI: 10.1111/j.1420-9101.2011.02393.x 	 ---> 	 Paper: <tethne.classes.paper.Paper object at 0x120158890>


Other indexing fields
=====================

In addition to the primary index, you can index the :class:`.Paper`\ s in your
:class:`.Corpus` using any other fields that you like. By default, the Web of
Science ``read`` method will index ``'citations'`` and ``'authors'``:

   >>> 'The following Paper fields have been indexed: \n\n\t%s' % '\n\t'.join(corpus.indices.keys())
   The following Paper fields have been indexed:
   	    citations
   	    authors

The ``'citations'`` index, for example, allows us to look up all of the
:class:`.Paper`\ s that contain a particular bibliographic reference:

   >>> for citation, papers in corpus.indices['citations'].items()[7:10]:   # Show the first three, for space's sake.
   ...     print 'The following Papers cite %s: \n\n\t%s \n' % (citation, '\n\t'.join(papers))
   The following Papers cite WHITFIELD J 2006 NATURE:
        WOS:000252758800011
        WOS:000253464000004
   The following Papers cite WANG T 2006 GLOBAL CHANGE BIOL:
        WOS:000282225000019
        WOS:000281546800001
        WOS:000251903200006
        WOS:000292901400010
        WOS:000288656800015
        WOS:000318353300001
        WOS:000296710600017
        WOS:000255552100006
        WOS:000272153800012
   The following Papers cite LINKOSALO T 2009 AGR FOREST METEOROL:
        WOS:000298398700003

Notice that the values above are not :class:`.Paper`\s themselves, but
identifiers. These are the same identifiers used in the primary index,
so we can use them to look up :class:`.Paper`\ s:

   >>> papers = corpus.indices['citations']['CARLSON SM 2004 EVOL ECOL RES']  # Who cited Carlson 2004?
   >>> print papers
   >>> for paper in papers:
   ...     print corpus.indexed_papers[paper]
   ['WOS:000311994600006', 'WOS:000304903100014', 'WOS:000248812000005']
   <tethne.classes.paper.Paper object at 0x112d1fe10>
   <tethne.classes.paper.Paper object at 0x1121e8310>
   <tethne.classes.paper.Paper object at 0x1144ad390>

We can create new indices using the ``index`` method. For example, to
index our :class:`.Corpus` using the ``authorKeywords`` field:

   >>> corpus.index('authorKeywords')
   >>> for keyword, papers in corpus.indices['authorKeywords'].items()[6:10]:   # Show the first three, for space's sake.
   ...     print 'The following Papers contain the keyword %s: \n\n\t%s \n' % (keyword, '\n\t'.join(papers))
   The following Papers contain the keyword EFFICIENCY:
       WOS:000322031500005
       WOS:000256598600035
       WOS:A1997WW80400007
   The following Papers contain the keyword SALVELINUS-ALPINUS L.:
       WOS:000314988900003
   The following Papers contain the keyword ALLOCHRONIC SPECIATION:
       WOS:000292040700014
   The following Papers contain the keyword AEROBIC PERFORMANCE:
       WOS:000316115400013
       WOS:000316115400014

Since we're interested in historical trends in our :class:`.Corpus`, we
probably also want to index the ``date`` field:

   >>> corpus.index('date')
   >>> for date, papers in corpus.indices['date'].items()[-11:-1]:   # Last ten years.
   ...     print 'There are %i Papers from %i' % (len(papers), date)
   There are 58 Papers from 2003
   There are 77 Papers from 2004
   There are 84 Papers from 2005
   There are 71 Papers from 2006
   There are 103 Papers from 2007
   There are 130 Papers from 2008
   There are 143 Papers from 2009
   There are 161 Papers from 2010
   There are 190 Papers from 2011
   There are 201 Papers from 2012

We can examine the distribution of :class:`.Paper`\ s over time using the
``distribution`` method:

   >>> corpus.distribution()[-11:-1]   # Last ten years.
   [58, 77, 84, 71, 103, 130, 143, 161, 190, 201]

.. image:: _static/images/corpora/output_30_0.png

Selecting :class:`.Paper`\ s from the :class:`.Corpus`
======================================================

In previous examples, we selected a :class:`.Paper` from our :class:`.Corpus`
using the primary index, ``indexed_papers``. In fact, there is a much simpler
way! :class:`.Corpus` allows us to "select" :class:`.Paper`\ s using its
built-in ``get`` method:

   >>> corpus['WOS:000309391500014']
   <tethne.classes.paper.Paper at 0x1126787d0>

Whoa! But it gets better. We can select :class:`.Paper`\ s using any of the
indices in the :class:`.Corpus`. For example, we can select all of the papers
with the ``authorKeyword`` ``LIFE``:

   >>> corpus[('authorKeywords', 'LIFE')]
   [<tethne.classes.paper.Paper at 0x112580090>,
    <tethne.classes.paper.Paper at 0x11187ca50>,
    <tethne.classes.paper.Paper at 0x11e4af9d0>,
    <tethne.classes.paper.Paper at 0x11dca0290>,
    <tethne.classes.paper.Paper at 0x11b249b90>,
    <tethne.classes.paper.Paper at 0x11a83a290>,
    <tethne.classes.paper.Paper at 0x11eb05910>,
    <tethne.classes.paper.Paper at 0x112578110>,
    <tethne.classes.paper.Paper at 0x11db9ce90>]

We can also select :class:`.Paper`\ s using several values. For example, with
the primary index field:

   >>> corpus[['WOS:000309391500014', 'WOS:000306532900015']]
   [<tethne.classes.paper.Paper at 0x1126787d0>,
    <tethne.classes.paper.Paper at 0x112578110>]

...and with other indexed fields (think of this as an OR search):

   >>> corpus[('authorKeywords', ['LIFE', 'ENZYME GENOTYPE', 'POLAR AUXIN'])]
   [<tethne.classes.paper.Paper at 0x112580090>,
    <tethne.classes.paper.Paper at 0x11187ca50>,
    <tethne.classes.paper.Paper at 0x11e4af9d0>,
    <tethne.classes.paper.Paper at 0x11dca0290>,
    <tethne.classes.paper.Paper at 0x11b249b90>,
    <tethne.classes.paper.Paper at 0x11a83a290>,
    <tethne.classes.paper.Paper at 0x11eb05910>,
    <tethne.classes.paper.Paper at 0x112578110>,
    <tethne.classes.paper.Paper at 0x11db9ce90>,
    <tethne.classes.paper.Paper at 0x1126787d0>,
    <tethne.classes.paper.Paper at 0x114140fd0>]

Since we indexed ``'date'`` earlier, we could select any ``Papers``
published between 2011 and 2012:

   >>> papers = corpus[('date', range(2002, 2013))] # range() excludes the "last" value.
   >>> 'There are %i Papers published between %i and %i' % (len(papers), 2002, 2012)
   There are 1267 Papers published between 2002 and 2012


Features
========

Earlier we used specific fields in our :class:`.Paper`\ s to create indices.
The inverse of an index is what we call a **:class:`.FeatureSet`**. A
:class:`.FeatureSet` contains data about the occurrence of specific features
across all of the :class:`.Paper`\ s in our :class:`.Corpus`.

The ``read`` method generates a few :class:`.FeatureSet` by default. All of
the available :class:`.FeatureSet`\ s are stored in a dictionary,
:attr:`.Corpus.features`

   >>> corpus.features.items()
   [('citations', <tethne.classes.feature.FeatureSet at 0x123ce0dd0>),
    ('authors', <tethne.classes.feature.FeatureSet at 0x123ce0d90>)]

Each :class:`.FeatureSet` has several properties:

:attr:`.FeatureSet.index` maps integer identifiers to specific features.
For example, for author names:

   >>> featureset = corpus.features['authors']
   >>> for k, author in featureset.index.items()[0:10]:
   ...     print '%i  -->  "%s"' % (k, ', '.join(author)) # Author names are stored as (LAST, FIRST M).
   0  -->  "AHLROTH, P"
   1  -->  "SUHONEN, J"
   2  -->  "ALATALO, RV"
   3  -->  "HYVARINEN, E"
   4  -->  "HUSBAND, BC"
   5  -->  "BURGESS, KS"
   6  -->  "FISCHER, M"
   7  -->  "MATTHIES, D"
   8  -->  "ELZINGA, JELMER A"
   9  -->  "BERNASCONI, GIORGINA"

:attr:`.FeatureSet.lookup` is the reverse of :attr:`.FeatureSet.index` : it maps
features onto their integer IDs:

   >>> featureset = corpus.features['authors']
   >>> for author, k in featureset.lookup.items()[0:10]:
   ...     print '%s  -->  %i' % (', '.join(author).ljust(25), k)
   LIU, SR               -->  4087
   IVEY, CHRISTOPHER T      -->  805
   BURNS, KEVIN C          -->  2338
   FUTUYMA, DOUGLAS J       -->  4111
   FERRIER, SHARON M        -->  2687
   ROOD, SB               -->  2910
   YOKOYAMA, JUN           -->  3033
   DODD, RS               -->  3211
   SEXTON, JASON P         -->  3112
   PEARSONS, TODD N         -->  387


:attr:`.FeatureSet.documentCounts` shows how many :class:`.Paper`\ s in our
:class:`.Corpus` have a specific feature:

   >>> featureset = corpus.features['authors']
   >>> for k, count in featureset.documentCounts.items()[0:10]:
   ...     print 'Feature %i (which identifies author "%s") is found in %i documents' % (k, ', '.join(featureset.index[k]), count)
   Feature 0 (which identifies author "AHLROTH, P") is found in 1 documents
   Feature 1 (which identifies author "SUHONEN, J") is found in 1 documents
   Feature 2 (which identifies author "ALATALO, RV") is found in 1 documents
   Feature 3 (which identifies author "HYVARINEN, E") is found in 1 documents
   Feature 4 (which identifies author "HUSBAND, BC") is found in 1 documents
   Feature 5 (which identifies author "BURGESS, KS") is found in 1 documents
   Feature 6 (which identifies author "FISCHER, M") is found in 5 documents
   Feature 7 (which identifies author "MATTHIES, D") is found in 4 documents
   Feature 8 (which identifies author "ELZINGA, JELMER A") is found in 1 documents
   Feature 9 (which identifies author "BERNASCONI, GIORGINA") is found in 2 documents

:attr:`.FeatureSet.features` shows how many times each feature occurs in
each :class:`.Paper`.

   >>> featureset.features.items()[0]
   ('WOS:000078288500016',
    [(('SUHONEN', 'J'), 1),
     (('AHLROTH', 'P'), 1),
     (('ALATALO', 'RV'), 1),
     (('HYVARINEN', 'E'), 1)])

We can create a new :class:`.FeatureSet` from just about any field in our
:class:`.Corpus`, using :meth:`.Corpus.index_feature`\. For example, suppose
that we were interested in the distribution of ``authorKeywords`` across
the whole corpus:

   >>> corpus.index_feature('authorKeywords')
   >>> corpus.features.keys()
   ['citations', 'authorKeywords', 'authors']

   >>> featureset = corpus.features['authorKeywords']
   >>> for k, count in featureset.documentCounts.items()[0:10]:
   ...     print 'Keyword %s is found in %i documents' % (featureset.index[k], count)
   Keyword EVOLUTION is found in 233 documents
   Keyword DIMORPHISM is found in 8 documents
   Keyword LIMNOPORUS-CANALICULATUS is found in 1 documents
   Keyword DISPERSAL is found in 39 documents
   Keyword INSECTS is found in 8 documents
   Keyword MORPHS is found in 1 documents
   Keyword FLIGHTLESSNESS is found in 1 documents
   Keyword REMIGIS is found in 1 documents
   Keyword LIFE-HISTORY is found in 73 documents
   Keyword LOUISIANA IRISES is found in 3 documents

   >>> featureset.features['WOS:000324532900018']   # Feature for a specific Paper.
   [('GENETIC SIMILARITY RULE', 1),
    ('ANT-APHID INTERACTIONS', 1),
    ('HERITABILITY', 1),
    ('GENOTYPE', 1),
    ('CONSEQUENCES', 1),
    ('FOOD-WEB', 1),
    ('DEFENSE', 1),
    ('FOREST ECOSYSTEM', 1),
    ('DIVERSITY', 1),
    ('ECOSYSTEM GENETICS', 1)]

:meth:`.Corpus.feature_distribution` yields the occurrence of a specific
feature over time.

   >>> plt.figure(figsize=(10, 3))
   >>> years, values = corpus.feature_distribution('authorKeywords', 'DIVERSITY')
   >>> start = min(years)
   >>> end = max(years)
   >>> X = range(start, end + 1)
   >>> plt.plot(years, values, lw=2)
   >>> plt.ylabel('Papers with DIVERSITY in authorKeywords')
   >>> plt.xlim(start, end)
   >>> plt.show()

.. image:: _static/images/corpora/output_55_0.png
