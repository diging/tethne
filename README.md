![Tethneus, an orb weaving spider](http://diging.github.io/tethne/doc/0.6.1-beta/_static/logo_round.png)

Tethne [![Build Status](https://travis-ci.org/diging/tethne.svg?branch=python)](https://travis-ci.org/diging/tethne)
======
Tethne is a Python package for integrated bibliographic and corpus analysis developed by
the Digital Innovation Group at Arizona State University. Tethne provides simple tools
for generating networks from bibliographic datasets, and provides a framework for weaving
together techniques from scientometrics, computational linguistics, topic modeling, and
social influence modeling. Rather than reinvent or re-implement existing algorithms,
Tethne is designed to interface with existing software packages, and to provide
mechanisms for drawing the results and functionalities of those packages together.

Key features
------------
* Flexible core model for text and citation-data.
* Provides core analytic features of popular citation-analysis software (e.g. Citespace).
* Integrates popular topic modeling software (e.g. MALLET).
* Export network models to mainstream formats (e.g. for visualization in Cytoscape).
* Leverages powerful computational and network-analysis libraries in Python. 

Documentation
-------------
For more information, see the Tethne [website](http://diging.github.io/tethne/).

The documentation project (ReST sources, etc.) can be found in [``tethne-docs``](https://github.com/diging/tethne-docs).

Requirements
------------
These should be installed automatically when you install Tethne, but just in case they
aren't:

```
networkx>=1.8.1
Unidecode>=0.04.16
iso8601
rdflib
```

New in v0.7
-----------
v0.7 was a nearly ground-up refactor, resulting in a more modular and testable codebase
and a simplified API. Here are some of the most notable changes:
* Network-building functions were made significantly more abstract and flexible.
* Numpy and SciPy are no longer required. We weren't really taking advantage of the
  performance gains afforded by those packages, and some users were running into
  installation issues with SciPy.
* Plotting functionality has been removed. This was causing bloat, and we were making
  aesthetic and formatting decisions for the user that weren't easily customizable.
* Huge improvements to the WoS reader. The old reader was bloated and suffered from some
  nasty bugs.
* Re-designed ``Corpus`` and ``Paper`` classes. See the docs for more information.
* Introduced ``Feature`` and ``FeatureSet`` classes to provide a more consistent and
  user-friendly mechanism for managing document features.
  
Coming in v0.8
--------------
* Support for [igraph](http://igraph.org/redirect.html) and 
  [graph-tool](https://graph-tool.skewed.de/).
* 

Questions?
----------
Ask [Erick](https://asu.academia.edu/ErickPeirson)

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
