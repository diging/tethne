![Tethneus, an orb weaving spider](http://diging.github.io/tethne/doc/0.6.1-beta/_static/logo_round.png)

Tethne [![Build Status](https://travis-ci.org/diging/tethne.svg?branch=python)](https://travis-ci.org/diging/tethne)
======
Tethne is a Python package for integrated bibliographic and corpus analysis developed by the Digital Innovation Group at Arizona State University. Tethne provides simple tools for generating networks from bibliographic datasets, and provides a framework for weaving together techniques from scientometrics, computational linguistics, topic modeling, and social influence modeling. Rather than reinvent or re- implement existing algorithms, Tethne is designed to interface with existing software packages, and to provide mechanisms for drawing the results and functionalities of those packages together.

Over 270 unit tests can be found in [``tethne-tests``](https://github.com/diging/tethne-tests). 

Key features
------------
* Flexible core model for text and citation-data.
* Provides core analytic features of popular citation-analysis software (e.g. Citespace).
* Integrates popular topic modeling software (e.g. MALLET).
* Export network models to mainstream formats (e.g. for visualization in Cytoscape).
* Leverages powerful computational and network-analysis libraries in Python. 
* HDF5 data management for persistence and interoperability.

Documentation
-------------
For more information, see the Tethne [website](http://diging.github.io/tethne/) and
[documentation](http://diging.github.io/tethne/doc/0.6.1-beta/index.html) (under development).

The documentation project (ReST sources, etc.) can be found in [``tethne-docs``](https://github.com/diging/tethne-docs).

Requirements
------------
We recommend using the Anaconda Python suite. See
[installation](http://diging.github.io/tethne/doc/0.6.1-beta/installation.html#installation) for details.

```
scipy==0.14.0
numpy==1.8.1
networkx==1.8.1
matplotlib==1.3.1
tables==3.1.1
Unidecode==0.04.16
geopy==0.99
nltk==2.0.4
```

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
