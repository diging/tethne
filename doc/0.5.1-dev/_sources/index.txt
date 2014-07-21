.. tethne documentation master file, created by
   sphinx-quickstart on Fri Jun 27 15:13:57 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. warning:: This documentation is not complete, and not all of the examples are tested.
             More soon.

Tethne: Corpus Analysis for Historians
======================================

Tethne is a Python package that draws together tools and techniques from bibliometrics, 
computational linguistics, and social influence modeling into a single easy-to-use corpus
analysis framework. Scholars can use Tethne to parse and organize data from the ISI Web of
Science and JSTOR Data-for-Research databases, and generate time-variant citation-based
:mod:`.networks`\, :mod:`.corpus` models, and :mod:`.social` influence models. Tethne also 
provides :mod:`.writers` that make it easy to visualize those models using mainstream
network visualization software (eg `Cyotoscape <http://cytoscape.org>`_ and 
`Gephi <http://gephi.org>`_) and the `MatPlotLib Python library 
<http://matplotlib.org/>`_. Dataset :mod:`.persistence` for archiving and sharing data is
achieved using the `HDF5 file format <http://www.hdfgroup.org/HDF5/>`_.

.. toctree::
   :maxdepth: 2
   
   installation
   quickstart
   support
   tutorials
   modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

