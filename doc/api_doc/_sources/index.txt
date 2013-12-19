.. tethne documentation master file, created by
   sphinx-quickstart on Sun Nov 24 20:52:16 2013.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Tethne: Bibliographic Network Analysis in Python
================================================

Tethne provides tools for easily parsing and analyzing bibliographic data in Python.
The primary emphasis is on working with data from the ISI Web of Science database, and
providing efficient methods for modeling and analyzing citation-based networks. Future
versions will include support for PubMed, Scopus, and other databases.

Tethne's four main workflow components are (1) parsing_ bibliographic 
data, (2) network construction_, (3) analysis_, and (4) writing_ network data files for
visualization using software like Cytoscape_ or Gephi_. Methods are also provided for
generating corpus objects that can be analyzed in the InPhO Vector Space Model (VSM_) 
Framework. Tethne relies on NetworkX_ for graph classes, and leverages its network analysis
algorithms.

.. _NetworkX: http://networkx.github.io/
.. _parsing: tethne.readers.html
.. _construction: tethne.networks.html
.. _analysis: tethne.analyze.html
.. _writing: tethne.writers.html
.. _Cytoscape: http://www.cytoscape.org/
.. _Gephi: https://gephi.org/
.. _VSM: https://github.com/inpho/vsm

To get started, consult the Tutorial. For support, visit our GitHub repository_.

.. _repository: https://github.com/diging/tethne

Contents
--------

.. toctree::
   :maxdepth: 3

   tutorial
   tethne

About
-----

Tethne is developed by the ASU Digital Innovation Group (DigInG_), part of the Laubichler 
Lab in the School of Life Science's Center for Biology & Society. 

.. _DigInG: http://devo-evo.lab.asu.edu/diging

This material is based upon work supported by the National Science Foundation Graduate Research Fellowship Program under Grant No. 2011131209, and NSF Doctoral Dissertation Research Improvement Grant No. 1256752.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

