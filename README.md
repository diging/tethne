![alt text](https://raw.github.com/diging/tethne/python/doc/logo.jpeg "Tethneus, an orb weaving spider.")

Tethne
======
Tethne is a Python package that draws together tools and techniques from bibliometrics, 
computational linguistics, and social influence modeling into a single easy-to-use corpus
analysis framework. Scholars can use Tethne to parse and organize data from the ISI Web of
Science and JSTOR Data-for-Research databases, and generate time-variant citation-based
network models, topic models, and social influence models. Tethne also provides mechanisms
for visualizing those models using mainstream network visualization software (e.g. 
Cyotoscape and Gephi) and the MatPlotLib Python library.

![alt text](https://raw.githubusercontent.com/diging/tethne/python/doc/highlevel.png "Highlevel architecture for Tethne.")
![alt text](https://raw.githubusercontent.com/diging/tethne/python/doc/legend.png "Legend.")

Key features
------------
* Flexible core model for text and citation-data.
* Provides core analytic features of popular citation-analysis software (e.g. Citespace).
* Integrates popular topic modeling software (e.g. MALLET, Gensim).
* Export network models to mainstream formats (e.g. for visualization in Cytoscape).
* Leverages powerful computational and network-analysis libraries in Python. 
* HDF5 data management ensures efficient memory usage, persistence, and interoperability.

Documentation
-------------
For more information, see the Tethne [website](https://github.com/diging/tethne) and
[documentation](http://diging.github.io/tethne/api/) (under development).

Requirements
------------
* [Python 2.7](http://www.python.org/)
* [NetworkX](http://networkx.github.io/)
* [Numpy](http://numpy.org)
* [ElementTree](http://docs.python.org/2/library/xml.etree.elementtree.html)
* [PyTables](http://www.pytables.org/moin)

Questions?
----------
Ask [Erick](https://cbs.asu.edu/gradinfo/?page_id=49)

Contributors
------------
* [erickpeirson](http://github.com/erickpeirson)
* [aabaker99](http://github.com/aabaker99)
* [rsubra13](http://github.com/rsubra13)

License
-------
Tethne is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tethne is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
[GNU General Public License](http://www.gnu.org/licenses/) for more details.

![alt text](http://www.gnu.org/graphics/gplv3-127x51.png "GNU GPL 3")

About
-----
Tethne is developed by the 
[ASU Digital Innovation Group (DigInG)](http://devo-evo.lab.asu.edu/diging),
part of the [Laubichler Lab](http://devo-evo.lab.asu.edu) in the Center for Biology & 
Society, School of Life Sciences.

This material is based upon work supported by the National Science Foundation Graduate 
Research Fellowship Program under Grant No. 2011131209, and NSF Doctoral Dissertation 
Research Improvement Grant No. 1256752.
