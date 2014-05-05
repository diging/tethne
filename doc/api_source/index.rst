.. tethne documentation master file, created by
   sphinx-quickstart on Sun Nov 24 20:52:16 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tethne: Bibliographic Network Analysis in Python
================================================

.. image:: _static/images/logo.jpeg
   :width: 100%

Tethne provides tools for easily parsing and analyzing bibliographic data in Python.
The primary emphasis is on working with data from the ISI Web of Science database, and
providing efficient methods for modeling and analyzing citation-based networks. Future
versions will include support for PubMed, Scopus, and other databases.

As of v0.3, Tethne is beginning to include methods for incorporating data from the `JSTOR
Data-for-Research service <http://dfr.jstor.org>`_, and `MALLET topic modeling
<http://mallet.cs.umass.edu/topics.php>`_.

Tethne relies on NetworkX_ for graph classes, and leverages its network 
analysis algorithms. You can visualize networks produced with Tethne in `Cytoscape
<http://www.cytoscape.org/>`_ or `Gephi <https://gephi.org/>`_.

.. _NetworkX: http://networkx.github.io/

To get started, consult the `tutorial <tutorial.html>`_. For support, visit our `GitHub 
repository <https://github.com/diging/tethne/issues>`_.

.. _repository: 

Contents
--------

.. toctree::
   :maxdepth: 2

   install
   tutorial
   commandline
   tethne

About
-----

Tethne is developed by the ASU Digital Innovation Group (DigInG_), part of the Laubichler 
Lab in the Center for Biology & Society, School of Life Sciences. 

.. _DigInG: http://devo-evo.lab.asu.edu/diging

This material is based upon work supported by the National Science Foundation Graduate 
Research Fellowship Program under Grant No. 2011131209, and NSF Doctoral Dissertation 
Research Improvement Grant No. 1256752.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

