tethne.readers: Parsing Bibliographic Data
==========================================

Web of Science
--------------

Methods for parsing bibliographic data from the Web of Science are contained in the 
:mod:`.readers.wos` module. Tethne parses Web of Science field-tagged data into a 
list of :class:`.Paper` objects. This is a two-step process: data are first parsed 
into a list of dictionaries with field-tags as keys, and then each dictionary is 
converted to a :class:`.Paper` .

First import the :mod:`.readers.wos` module:

.. code-block:: python

   >>> import tethne.readers as rd

Then parse the WoS data to a list of field-tagged dictionaries using :func:`.readers.wos.parse_wos` :

.. code-block:: python

   >>> wos_list = rd.wos.parse_wos("/Path/to/savedrecs.txt")
   >>> wos_list[0].keys()
   ['EM', '', 'CL', 'AB', 'WC', 'GA', 'DI', 'IS', 'DE', 'VL', 'CY', 'AU', 'JI', 'AF', 'CR', 'DT', 'TC', 'EP', 'CT', 'PG', 'PU', 'PI', 'RP', 'J9', 'PT', 'LA', 'UT', 'PY', 'ID', 'SI', 'PA', 'SO', 'Z9', 'PD', 'TI', 'SC', 'BP', 'C1', 'NR', 'RI', 'ER', 'SN']

Alternatively, if you have many data files saved in the same directory, you can use :func:`.readers.wos.parse_from_dir` :

.. code-block:: python

   >>> wos_list = rd.wos.parse_from_dir("/Path/to")

Finally, convert those field-tagged dictionaries to :class:`.Paper` objects using :func:`.readers.wos.wos2meta` :

.. code-block:: python

   >>> papers = rd.wos.wos2meta(wos_list)
   >>> papers[0]
   <tethne.data.Paper instance at 0x101b575a8>