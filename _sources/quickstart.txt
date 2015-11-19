Quickstart
==========

Load some data
--------------

Assuming that you have a JSTOR DfR dataset (in XML format) containing some wordcount
data unzipped at ``/path/to/my/dataset``, create a :class:`.Corpus` with:

.. code-block:: python

   >>> from tethne.readers import dfr
   >>> dfr_corpus = dfr.read('/path/to/my/dataset')

Or if you're working with data from the Web of Science, try:

.. code-block:: python

   >>> from tethne.readers import wos
   >>> wos_corpus = dfr.read('/path/to/my/wosdata.txt')

Your corpus is automatically indexed by author, publication date, and (if
available) citations.

.. code-block:: python

   >>> corpus.indices.keys()
   ['date', 'citations', 'authors']

You can select all of the :class:`.Paper`\s published in 1980 with:

.. code-block:: python

   >>> corpus[('date', 1980)]
   [<tethne.classes.paper.Paper at 0x1072191d0>,
    <tethne.classes.paper.Paper at 0x1069ae0d0>,
    <tethne.classes.paper.Paper at 0x1073345d0>,
    <tethne.classes.paper.Paper at 0x107282210>,
    <tethne.classes.paper.Paper at 0x106c7b050>,
    ...
    <tethne.classes.paper.Paper at 0x106ad6150>,
    <tethne.classes.paper.Paper at 0x10718b490>,
    <tethne.classes.paper.Paper at 0x10695b850>,
    <tethne.classes.paper.Paper at 0x1068c4310>]

Create a new index using the :meth:`.Corpus.index` method:

.. code-block:: python

   >>> corpus.index('journal')
   >>> corpus.indices.keys()
   ['date', 'journal', 'citations', 'authors']

   >>> corpus[('journal', 'Journal of the History of Biology')]
   [<tethne.classes.paper.Paper at 0x1072191d0>,
    <tethne.classes.paper.Paper at 0x1069ae0d0>,
    <tethne.classes.paper.Paper at 0x1073345d0>,
    <tethne.classes.paper.Paper at 0x107282210>,
    <tethne.classes.paper.Paper at 0x106c7b050>,
    ...
    <tethne.classes.paper.Paper at 0x106ad6150>,
    <tethne.classes.paper.Paper at 0x10718b490>,
    <tethne.classes.paper.Paper at 0x10695b850>,
    <tethne.classes.paper.Paper at 0x1068c4310>]

:meth:`.Corpus.distribution` will show you how the :class:`.Paper`\s in your
:class:`.Corpus` are distributed over time.

.. code-block:: python

   >>> x, y = corpus.distribution()
   >>> import matplotlib.pyplot as plt
   >>> plt.bar(x, y)

.. figure:: _static/images/corpus_plot_distribution.png
   :width: 400
   :align: center

A :class:`.Paper` is a bibliographic record. Depending on the data source, the
fields contained by a :class:`.Paper` may vary.

.. code-block:: python

   >>> pprint(corpus[0].__dict__)
   {'abstract': "PPB, MBO and ZBB have each been implemented in the U S. Federal government, ostensibly as means for facilitating planning and control in agencies and programmes. The purpose of this paper is to evaluate the use of these techniques as management tools, political strategies and ritualistic symbols using concepts discussed in the organizational theory, planning and control, and policy science literatures Two basic conclusions emerge from the evaluation First, PPB, MBO and ZBB may inappropriately encourage the use of an analytical, computational decision strategy, and a cost/benefit method of performance assessment at a level within the organization and in environmental settings which call for an inspirational decision strategy and social test performance assessment As a result, environmental variety may not be matched by an organizational response which is equally variable Secondly, PPB, MBO and ZBB may have been used more as political strategies and ritualistic symbols for controlling and directing controversy by both the executive and legislative branches of the U.S Federal government and less as management tools for improving decision making within the U S Federal bureaucracy These management tools give the appearance of rationality in the formulation of public policy which is consistent with man's need for confidence building and conflict avoidance in running the affairs of state.",
    'authors_full': [('DIRSMITH', 'MARK W'),
                     ('JABLONSKY', 'STEPHEN F'),
                     ('LUZI', 'ANDREW D')],
    'date': 1980,
    'documentType': 'fla',
    'doi': '10.2307/2486258',
    'issue': '4',
    'journal': 'Strategic Management Journal',
    'pagerange': 'pp. 303-329',
    'publisher': 'Wiley',
    'title': 'Planning and Control in the U.S. Federal Government: A Critical Analysis of PPB, MBO and ZBB',
    'volume': '1'}

Simple networks simply
----------------------

Network-building methods are available in :mod:`tethne.networks`\. You can
create a :func:`.coauthors` network like this:

.. code-block:: python

   >>> from tethne.networks import coauthors
   >>> coauthor_graph = coauthors(wos_corpus)

All of Tethne's network-building methods return :class:`networkx.Graph` objects.
For more information, see the `NetworkX documentation
<https://networkx.github.io/>`_.

To create a time-variant coauthor network, use a :class:`.GraphCollection`\.

.. code-block:: python

   >>> from tethne import GraphCollection
   >>> coauthor_collection = GraphCollection(wos_corpus, coauthors)
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

You access the network for 1992 like this:

.. code-block:: python

   >>> coauthor_collection[1992]
   <networkx.classes.graph.Graph at 0x15f3016d0>

You can control how the :class:`.GraphCollection` is assembled by passing
``slice_kwargs`` to the constructor. To create a series of coauthor graphs using
a 4-year sliding time-window, for example, you could do:

.. code-block:: python

   >>> from tethne import GraphCollection
   >>> coauthor_collection = GraphCollection(wos_corpus, coauthors,            \
                                             slice_kwargs={'window_size': 4,   \
                                                           'step_size': 1})
   >>> coauthor_collection.node_distribution()
   {1980: 99,
    1981: 90,
    1982: 92,
    1983: 100,
    1984: 117,
    1985: 151,
    1986: 180,
    1987: 209,
    1988: 241,
    1989: 261,
    1990: 287,
    1991: 321}

If you're using WoS data (with citations), you can also build citation-based
graphs (see :mod:`.networks.papers`\). Here's a static co-citation graph from a
:class:`.Corpus`:

.. code-block:: python

   >> from tethne.networks import cocitation
   >>> cocitation_graph = cocitation(wos_corpus, min_weight=3)

``min_weight=3`` means that a pair of papers must be co-cited three times to be
included in the network.

Visualize your networks
-----------------------

You can export a graph for visualization in `Cytoscape <http://cytoscape.org>`_
or `Gephi <http://gephi.org>`_ using :mod:`tethne.writers`\:

.. code-block:: python

   >>> from tethne.writers.graph import to_graphml
   >>> to_graphml(coauthor_graph, '/path/to/my/graph.graphml')

To visualize a :class:`.GraphCollection` as a dynamic graph in Cytoscape, export
it using :func:`.writers.collection.to_dxgmml`\:

.. code-block:: python

   >>> from tethne.writers.collection import to_dxgmml
   >>> to_dxgmml(coauthor_collection, '/path/to/my/dynamicNetwork.xgmml')

Working with Words
------------------

Suppose you loaded up a :class:`.Corpus` from some DfR datasets, using:

.. code-block:: python

   >>> from tethne.readers import dfr
   >>> dfr_corpus = dfr.read('/path/to/my/dataset')

Now you have some ``'wordcounts'`` in ``dfr_corpus.features``.

.. code-block:: python

   >>> dfr_corpus.features
   {'authors': <tethne.classes.feature.FeatureSet at 0x100534e90>,
    'bigrams': <tethne.classes.feature.FeatureSet at 0x11e599810>,
    'citations': <tethne.classes.feature.FeatureSet at 0x10051b990>,
    'keyterms': <tethne.classes.feature.FeatureSet at 0x107355ad0>,
    'trigrams': <tethne.classes.feature.FeatureSet at 0x14c126050>,
    'wordcounts': <tethne.classes.feature.FeatureSet at 0x1931c7290>}

You can retrieve the wordcounts for an individual paper using it's DOI:

.. code-block:: python

   >>> dfr_corpus.features['wordcounts'].features['10.2307/2486258']
   [('secondly', 4),
    ('ainalysis', 2),
    ('limited', 2),
    ('dynamic', 16),
    ('externally', 1),
    ('foul', 1),
    ('four', 3),
    ('demanded', 1),
    ('relationships', 9),
    ('whose', 2),
    ('capolitical', 1),
    ('coalignmnent', 1),
    ('presents', 3),
    ('investigation', 1),
    ('systemns', 1),
    ('admninistration', 1),
    ('conjecture', 1),
    ... ]

You can apply a stoplist using :meth:`.FeatureSet.transform`\.

.. code-block:: python

   >>> from nltk.corpus import stopwords
   >>> stoplist = set(stopwords.words())
   >>> apply_stoplist = lambda f, v, C, DC: None if f in stoplist else v
   >>> wordcounts = dfr_corpus.features['wordcounts']
   >>> dfr_corpus.features['filtered'] = wordcounts.transform(apply_stoplist)

If you have some recent WoS data with abstracts, you can get a
:class:`.FeatureSet` from abstract terms, too:

.. code-block:: python

   >>> from tethne.readers import wos
   >>> wos_corpus = dfr.read('/path/to/my/wosdata.txt')
   >>> from tethne import tokenize
   >>> wos_corpus.index_feature('abstract', tokenize=tokenize)
   >>> print wos_corpus.features
   ['abstract', 'authors', 'citations', 'date']

You can see how the word ``empirical`` is distributed across your
:class:`.Corpus` using :func:`.Corpus.distribution\:

.. code-block:: python

   >>> x, y = wos_corpus.feature_distribution('wordcounts', 'empirical')
   >>> plt.plot(x, y, lw=2)
   >>> plt.ylabel('Frequency of the word `empirical`')
   >>> plt.show()

.. figure:: _static/images/testdist.png
   :width: 400
   :align: center

Models Based on Words
---------------------

Topic models are pretty popular. You can create a LDA topic model using
`MALLET <http://mallet.cs.umass.edu/>`_ right from Tethne, using
:class:`tethne.model.corpus.mallet.LDAModel`\.

.. code-block:: python

   >>> from tethne import LDAModel
   >>> model = LDAModel(wos_corpus, 'abstract')     # Use words from 'abstract'.
   >>> model.fit(Z=20, max_iter=500)    # 20 topics, 500 iterations of sampling.

You can inspect the inferred topics using :meth:`.LDAModel.print_topics`\.

.. code-block:: python

   >>> model.print_topics(5)
   Topic	Top 5 words
   0  	strategy strategic strategies firms industry
   1  	costs pp firm economic cost
   2  	performance research study variables pp
   3  	acquisition acquisitions mergers market firms
   4  	planning strategic system corporate management
   5  	strategic strategy research management process
   6  	university john strategic france school
   7  	performance change organizational ceo board
   8  	japanese firms industry companies international
   9  	model market firm industry share
   10 	decision strategic group decisions problem
   11 	firms firm corporate compensation ownership
   12 	business time work part problems
   13 	firm technology innovation resources firms
   14 	anid al aind theory strategy
   15 	firms diversification firm performance related
   16 	managers management strategic control organizational
   17 	market product products entry industry
   18 	global structure international foreign business
   19 	journal management author paper strategic

We can also look at the representation of a topic over time using
:meth:`.LDAModel.topic_over_time`\:

.. code-block:: python

   >>> plt.figure(figsize=(15, 5))
   >>> for k in xrange(5):
   ...     x, y = model.topic_over_time(k)
   ...     plt.plot(x, y, label='topic {0}'.format(k), lw=2, alpha=0.7)
   >>> plt.legend(loc='best')
   >>> plt.show()

.. figure:: _static/images/topic_over_time.png
   :width: 400
   :align: center
