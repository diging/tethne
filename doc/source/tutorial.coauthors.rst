.. _coauthorship:

Coauthorship Networks
=====================

.. contents::
   :local:
   :depth: 2

.. note:: This tutorial was developed for the course `Introduction to Digital &
   Computational Methods in the Humanities (HPS) <http://devo-evo.lab.asu.edu/methods>`_,
   created and taught by `Julia Damerow <http://devo-evo.lab.asu.edu/?q=damerow>`_ and   
   `Erick Peirson <http://gradinfo.cbs.asu.edu/?page_id=49>`_.

Coauthorship networks are among the most popular models for studying the structure of 
research communities, due in no small part to the ease with which coauthorship networks
can be generated.

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

Slicing a Corpus
----------------

In this tutorial, we will analyze the evolution of a coauthorship network over time. To do
this, we will slice our data using the ``date`` field of each paper in our dataset.

Think of slicing as indexing: we will divide the :class:`.Paper`\s in our :class:`.Corpus` 
into bins by publication date, so that later on we can retrieve sets of papers 
corresponding to particular time-periods. You can slice your data using the 
:func:`Corpus.slice` method.

We'll use the ``time_period`` slice method, which means that the data will be divided into
subsets each containing data from a particular time period. The default window size is 1,
and the window will advance by 1 year in each slice.

We will assume that the first coauthorship event represents (with some delay) the
commencement of a collaborative relationship between two researchers, and that this
social tie does not simply disappear after the coauthorship event. A more sophisticated
model might parameterize the decay of potential social influence after a coauthorship
event, but for the purpose of this tutorial we will assume that those social ties are
effectively permanent. In order to realize this assumption in the final coauthorship
model, we will  use the cumulative slicing option, which means that the data from each 
time period will contain data from all of the previous time-periods. In other words, the
1957 subset will contain data from 1957, and the 1958 subset will contain data from 1957 
and 1958. This means that coauthorship ties will be added in each sequential graph, but
never removed.

Use the :func:`tethne.data.DataCollection.slice` method to slice your data. 

.. code-block:: python

   >>> MyCorpus.slice('date', 'time_period', window_size=1, cumulative=True)

Building a Static Co-author Graph
---------------------------------

Tethne will generate a graph using the ``AU`` field in your WoS data. See 
:ref:`fieldtagged` for more information about the fields available in a WoS datafile.

To get a sense of the overall structure of the graph, we can first build a static 
coauthorship graph by calling the :func:`.networks.authors.coauthors` method directly.

.. code-block:: python

   >>> from tethne.networks import authors
   >>> ca_graph = authors.coauthors(MyCorpus.all_papers())

.. _coauthors_to_graphml:

Visualize the Static Graph
--------------------------

Write the Graph to GraphML
```````````````````````````
`GraphML <http://graphml.graphdrawing.org>`_ is a widely-used static network data format.
We will write our graph to GraphML for visualization in Cytoscape.

Use the :func:`.to_graphml` method in :mod:`.writers.collection` to create a GraphML
data file.

.. code-block:: python

   >>> from tethne.writers import graph
   >>> graph.to_graphml(ca_graph, '/path/to/my/graphmlfile.grapml')
   
Cytoscape
`````````

Cytoscape was developed in 2002, with funding from the National Instute of General Medical
Sciences and the National Resource for Network Biology. The primary user base is the 
biomedical research community, especially systems biologists who study gene or protein 
interaction networks and pathways.

You can download Cytoscape 3 from \url{http://www.cytoscape.org}. This tutorial assumes
that you are using Cytoscape 3.0.2.

Import
''''''

In Cytoscape, import your network by selecting ``File > Import > Network > From file...``
and selecting the GraphML file generated by Tethne in your output directory.

Apply a Force Directed layout by selecting ``Layout > Prefuse Force Directed Layout``.

Coauthorship networks are usually comprised of a very large connected component, and many
very small components. For convenience, we will only look at the few largest components.
Select the largest connected components (click and drag to create a selection box). Then
create a new network with those selected components: select
``File > New > Networks > From selected nodes, all edges``.

.. image:: _static/images/tutorial/coauthors.7.png
   :width: 500
   :align: center   

You should now see a new graph in its own viewing window, containing only the components 
that you selected.

.. image:: _static/images/tutorial/coauthors.8.png
   :width: 500
   :align: center

Betweenness Centrality
''''''''''''''''''''''

This coauthorship network is clearly very modular: there are dense clusters connected by a
few linking nodes that occupy sparse areas of the graph (so-called "structural holes"). We
can identify the structurally most-significant actors by their "betweenness centrality."
Formally, betweenness centrality is a measure of the number of shortest paths that pass 
through a particular node.

Run Cytoscape's network-analysis algorithm. Go to 
``Tools > NetworkAnalyzer > Network Analysis > Analyze Network``.

.. image:: _static/images/tutorial/coauthors.9.png
   :width: 450
   :align: center   

Cytoscape may ask you whether to interpret the network as directed or undirected. A
coauthorship network is always undirected, since coauthorship is a symmetric relationship.

.. image:: _static/images/tutorial/coauthors.10.png
   :width: 400
   :align: center   
   
Once network analysis is complete, a window titled ``Results Panel`` will appear. Close
this window.

.. image:: _static/images/tutorial/coauthors.11.png
   :width: 400
   :align: center

To visualize the betweenness centrality of each node, create a new visual mapping.

1. Go to the VizMapper tab, in the left part of the Cytoscape workspace.
2. Find ``Node Size`` in the unused visual properties, and double-click to move it to the
   ``Node Visual Properties`` list.
3. Click in the area to the right of ``Node Size`` and select ``BetweennessCentrality``.
4. Click in the area to the right of ``Mapping Type`` and select ``Continuous Mapping``.

.. image:: _static/images/tutorial/coauthors.12.png
   :width: 400
   :align: center   
   
To change the size - centrality mapping function, double-click on the figure to the right
of ``Curent Mapping``, and drag the red open boxes up and down to change the angle of the 
function.

.. image:: _static/images/tutorial/coauthors.13.png
   :width: 400
   :align: center

The largest nodes are the most central nodes in their respective connected components. 
These are the nodes most responsible for connecting disparate clusters in the network.

To see a list of the most central nodes, set the Table Panel to show all nodes.

.. image:: _static/images/tutorial/coauthors.14.png
   :width: 500
   :align: center
   
Then sort by betweenness centrality by clicking on the column header in the Node Table 
(you may have to click twice to sort in descending order).

.. image:: _static/images/tutorial/coauthors.15.png
   :width: 550
   :align: center

Institutional affiliation
'''''''''''''''''''''''''

Wherever possible, Tethne includes institutional affiliations for authors as node 
attributes. You should see institutions listed in the Node Table.

.. image:: _static/images/tutorial/coauthors.16.png
   :width: 400
   :align: center
      
Create a visual mapping for institutional affiliation.

1. Go to the VizMapper.
2. Find ``Node Fill Color`` in the unused visual properties, and double-click to activate.
3. Click to the right of ``Node Fill Color'' and select ``institution''.
4. Set the ``Mapping Type'' to ``Discrete Mapping.'' A list of institutions should appear
   below ``Mapping Type.''
5. Right-click on ``Discrete Mapping'', and select 
   ``Mapping Value Generators > Random Color``.

.. image:: _static/images/tutorial/coauthors.17.png
   :width: 550
   :align: center
      
Each node should now be colored according to its institutional affiliation. 
Inspecting the network yields an immediate impression of whether coauthorship clusters are
due to affiliation with the same institution.

.. image:: _static/images/tutorial/coauthors.18.png
   :width: 550
   :align: center
      
Since some institutions may be colored quite similarly, select a cluster to view the 
specific institutional affiliation of each node. You may need to set the Node Table to 
``show selected`` rather than ``show all``.

.. image:: _static/images/tutorial/coauthors.19.png
   :width: 450
   :align: center
   
Circular layouts can also yield some insights into connectivity between different 
institutions. In the menu bar, select ``Layout > Attribute Circle Layout > institution``. 
This should arrange the nodes in each connected component in a circle. Nodes that are 
affiliated with the same institution should be adjacent to each other, so that the 
circumference of each circle can be divided into regions that correspond to single 
institutions. Edges crossing from one region to another should give a visual impression of
the magnitude of linkages between institutions.

.. image:: _static/images/tutorial/coauthors.20.png
   :width: 550
   :align: center
   
A similar layout, the ``Degree Sorted Circle`` layout, can yield more information about 
the structure of the network. As the name suggests, this layout arranges nodes in 
ascending order of degree (the number of links that each node has with other nodes in the 
network). The lowest-degree nodes begin just west of due-south, and degree increases 
clockwise around the circle so that the highest-degree nodes are just east of due-south. 
In the network depicted below, there is extremely dense connectivity among the
highest-degree nodes, while the rest of the graph is sparse by comparison. In other words,
the most well-connected nodes are all highly connected to each other. This may be due in 
part to papers with a very large number of authors.

.. image:: _static/images/tutorial/coauthors.21.png
   :width: 550
   :align: center
 
To export an image of your network, select 
``File > Export > Current Network View as Graphics``, and follow the prompts to save your
image.

.. _coauthors_gephi:

Inter-institutional Collaboration in Gephi
``````````````````````````````````````````

`Gephi <http://www.gephi.org>`_ provides additional tools for analyzing coauthorship
networks. In this section, we'll use Gephi to generate an inter-institutional 
collaboration network using your coauthorship network. That is, we will mash authors from
the same institutions together into institutional nodes, and combine coauthorship edges
so that we can see the magnitude of coauthorship activity between different institutions.

Import & visualize
''''''''''''''''''
1. In Gephi, select ``File > Open...`` and select your GraphML network file.
2. Click on the ``Preview`` tab.

.. image:: _static/images/tutorial/coauthors.22.png
   :width: 400
   :align: center
   
3. Open the ``Graph`` window: select ``Window > Graph``.

.. image:: _static/images/tutorial/coauthors.23.png
   :width: 400
   :align: center
   
4. Open the ``Layout`` window: select ``Window > Layout``.

5. In the ``Layout`` window, select the ``Force Atlast 2 layout``, then click ``Run``. 
   After a few seconds the graph should be spread out; click ``Stop``.

.. image:: _static/images/tutorial/coauthors.25.png
   :width: 550
   :align: center

Partition by institution
''''''''''''''''''''''''
1. Open the ``Partition`` window: select ``Window > Partition``. You may need to drag the 
   window to the left-hand area of the Gephi workspace.
   
2. In the ``Partition`` window, you should be on the ``Nodes`` tab by default. Click the 
   green ``refresh’’ button, then select ``institution’’ from the drop-down menu. You 
   should see a list of all institutions. 

3. To color nodes by institution, click the ``Apply`` button.

.. image:: _static/images/tutorial/coauthors.26.png
   :width: 350
   :align: center
   
Zooming in on the network, you’ll notice that some clusters of nodes are comprised of one
or a few colors, while other clusters are quite mixed. Just as in Cytoscape, this gives a
visual impression of which research communities involve inter-institutional 
collaborations, and which are more internal to a particular institution.

.. image:: _static/images/tutorial/coauthors.27.png
   :width: 550
   :align: center

Gephi makes it easy to collapse individual author nodes into nodes corresponding to their 
institutions. Cytoscape has this feature as well, but not all of the bugs are completely 
worked out. 

To group authors together into their respective institutions, click the ``Group`` button 
in the ``Partition`` window. 

Click on the dark **T** button in the lower left corner to show node labels, and use the 
right-hand slider at the bottom of the Graph window to make the labels smaller or larger.

The result may look a bit messy. There are a few things to notice:

* The edges between authors have been pooled into edges between institutions. The edge 
  weight indicates the number of coauthorship relationships between a pair of 
  institutions.

* The biggest node is called ``null``. This represents all of the authors for which no 
  institutional information was available. You may wish to delete this node; right-click 
  on the node and select ``Delete``. When prompted, click ``Yes``.

.. image:: _static/images/tutorial/coauthors.28.png
   :width: 550
   :align: center

To re-layout the network, go back to the ``Layout`` tab, and run the layout algorithm 
again. You may notice that the network contracts rapidly. You may find it useful to reduce
the edge width and zoom in, to achieve a nice node-size : edge-weight ratio. 

.. image:: _static/images/tutorial/coauthors.29.png
   :width: 550
   :align: center

To save an image of your network, click the ``SVG/PDF/PNG`` button in the lower-left
corner of the Gephi workspace.

.. image:: _static/images/tutorial/coauthors.30.png
   :width: 350
   :align: center

Coauthorship network evolution
------------------------------

This section describes how to generate a dynamic network with Tethne, and visualize that 
network in Cytoscape. Dynamic networks allow us to go beyond analyzing the final structure
of a network, and ask how the structure of a network changes over time. In this case, 
we will use a dynamic network to see how a coauthorship network grows over time.

A seemingly ubiquitous property of social networks is that they tend to be "scale-free".
That is, the degree distribution follows a power-law: there are a few very 
highly-connected actors, and a very large number of poorly-connected actors. 
The intuitive interpretation of this behavior is that "the rich get richer." In other 
words, if you're already popular then you're more likely to make new friends. 

In this tutorial, we will visualize the impact of degree centrality on edge acquisition
by using the :func:`.analyze.collection.attachment_probability` algorithm in Tethne.

Building a GraphCollection
```````````````````````````

A :class:`.GraphCollection` is a set of graphs generated from a :class:`.Corpus` or model.
We can generate a GraphCollection (``G``) in one step, using the 
:func:`GraphCollection.build` method.

A simple example might look like this:

.. code-block:: python

   >>> G = GraphCollection().build(C, 'date', 'authors', 'coauthors')
   
Here we have instructed :func:`GraphCollection.build` to build a graph for each 'slice'
along the 'date' axis. ``'authors'`` indicates that we want to use a graph method from
the :mod:`.networks.authors` submodule, and ``'coauthors'`` indicates the
name of the method from that module that we wish to use.   

Attachment Probability
``````````````````````

The :func:`.analyze.collection.attachment_probability` method automatically updates node
attributes in your :class:`.GraphCollection`\.

.. code-block:: python

   >>> from tethne.analyze import collection
   >>> collection.attachment_probability(C)

Dynamic XGMML
`````````````

Use the :func:`.writers.collection.to_dxgmml` method to create a `dynamic XGMML
<https://code.google.com/p/dynnetwork/wiki/DynamicXGMML>`_ network data file.

.. code-block:: python

   >>> from tethne.writers import collection
   >>> collection.to_dxgmml(G, '/path/to/my/dynamicnetwork.xgmml')

Cytoscape
`````````

In Cytoscape, import your .xgmml file by selecting 
``File > Import > Dynamic Network > XGMML File...``. Apply a force-directed or 
spring-embedded layout.

.. image:: _static/images/tutorial/coauthors.34.png
   :width: 450
   :align: center

In the VizMapper, map ``Node Size`` to ``attachment_probability``.

.. image:: _static/images/tutorial/coauthors.35.png
   :width: 300
   :align: center
   
Double-click on the function icon next to ``Current Mapping`` to edit the ``Node Size``
mapping function.

1. Click the ``Min/Max`` button, and set the maximum value to ``1.0``.
2. Slick on the ``Add`` button to create a new handle at an intermediate value. Drag
   the red open box up, and drag the corresponding black arrow left and right to alter
   the mapping function.
3. Click ``OK``.

.. image:: _static/images/tutorial/coauthors.36.png
   :width: 400
   :align: center

In the Control Panel, select the ``Dynamic Network`` tab.

1. Set the time resolution to roughly match the time-range of your network. In the
   example below, the network covers about 35 years, so a resolution of 1/50 was selected.

2. Set ``Time smoothness`` to ``0 ms``.

3. Use the slider to move through the states of your dynamic network. To view all states
   in succession, use the ``<< Play`` and ``Play >>`` buttons.

.. image:: _static/images/tutorial/coauthors.37.png
   :width: 550
   :align: center
   
The size of each node should reflect the relative probability that a node will accrue a
new neighbor in the next time slice. Try zooming in on a particular region of your
network, and move between two successive states to verify that this is the case.

.. image:: _static/images/tutorial/coauthors.38.png
   :width: 550
   :align: center
   