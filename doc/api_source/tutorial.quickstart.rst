Quickstart
==========

Download & install the latest version of Tethne from our GitHub repository:

.. code-block:: bash

   git clone https://github.com/diging/tethne.git
   cd tethne
   pip install ./tethne

After starting Python, import Tethne modules with:

.. code-block:: python

   import tethne.readers as rd
   import tethne.networks as nt
   import tethne.analyze as az
   import tethne.writers as wr

To parse some data from the Web of Science, use the tethne.readers.wos module.

.. code-block:: python

   wos_list = rd.wos.parse_wos("/Path/To/Data.txt")  # Field-tagged data.
   papers = rd.wos2meta(wos_list)

You can then generate a network using methods from the tethne.networks
subpackage. For example, to build a bibliographic coupling network:

.. code-block:: python

   BC = nt.citations.bibliographic_coupling(papers, citation_id='ayjid', threshold=2, node_id='ayjid')

