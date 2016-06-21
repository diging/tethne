Overview
========

Tethne is a Python software package for parsing and analyzing bibliographic
metadata. The overarching goal of the project is to make it easier for scholars
to build metadata-based network models, such as co-author and co-citation
graphs.

You can use Tethne to parse bibliographic metadata from the ISI Web of Science,
JSTOR Data-for-Research, and even your Zotero collections (support for Scopus is
planned, stay tuned!), and use those metadata to generate graphs for analysis
and visualization.

Who uses Tethne?
----------------

Tethne was developed with tech-savvy scholars in the humanities and social
sciences in mind, especially those interested in scientific change.


Python
------

This documentation assumes that you are familiar with the Python programming
language. Python is a high-level programming language that has gained widespread
adoption in the world of scientific computing. It's easy to learn, and has
accrued a rich ecosystem of high-performance scientific and numerical
libraries. Environments like `Jupyter/IPython
<https://ipython.org/notebook.html>`_ have made Python extremely accessible for
those with little or no background in programming.

For a gentle introduction to Python, check out
`learnpython.org <http://www.learnpython.org/>`_.

Tethne is developed in Python 2.7. Python 3 is a distinct language from Python
2.7, and many packages have not yet made the leap to this new platform. A
Python 3-compatible version is in the works, however, so stay tuned!

How to cite
-----------

Peirson, B. R. Erick., et al. (2016). Tethne v0.7.
http://diging.github.io/tethne/

For a complete list of contributors, see :ref:`contributors`.

License
-------

Tethne is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Tethne is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
`GNU General Public License <http://www.gnu.org/licenses/>`_ for more details.

.. image:: http://www.gnu.org/graphics/gplv3-127x51.png

.. _contributors:

Contributors
------------

Tethne is developed by the `Digital Innovation Group <http:///diging.asu.edu>`_
at Arizona State University. Countless people have contributed to this project
over the years, so the list below is undoubtedly incomplete.

Project lead: `Erick Peirson <http://asu.academia.edu/ErickPeirson>`_.

DigInG developers:

- Aaron Baker
- Ramki Subramanian
- Abhishek Singh
- Yogananda Yalugoti

External contributors:

- `@guilhermeleobas <https://github.com/guilhermeleobas>`_.

.. _contribute:

How to contribute
-----------------

1. `Fork <https://help.github.com/articles/fork-a-repo/>`_ the `Tethne
   GitHub repository <https://github.com/diging/tethne>`_.
2. Check out the ``develop`` branch:

   .. code-block:: bash

      $ git checkout develop

3. Create a new branch for your contribution, e.g. ``git checkout -b issue45``
4. Make your changes. Be sure to include a docstring for each function and
   class!
5. Write tests. We aim for 95% test coverage. Put your tests in ``tests``, where
   they belong.
6. Ensure that all of your tests are passing. We use
   `nose <https://nose.readthedocs.org/en/latest/>`_. Test with:

   .. code-block:: bash

      $ nosetests --with-coverage --cover-package=tethne --cover-min-percentage=95

7. Check for code cleanliness! Code should conform to
   `PEP 0008 <https://www.python.org/dev/peps/pep-0008/>`. We use
   `Pylint <http://www.pylint.org/>`_. For example:

   .. code-block:: bash

      $ pylint tethne/mycontribution.py

8. Create a `pull request
   <https://help.github.com/articles/using-pull-requests>`_.
   Be sure to select ``diging/develop`` as the base branch.
