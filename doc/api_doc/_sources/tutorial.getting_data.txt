Getting Data from the Web of Science
====================================

The ISI Web of Science is a proprietary database owned by Thompson Reuters. 
If you are affiliated with an academic institution, you may have access to
this database via an institutional license.

To access the Web of Science database via the Arizona State University library,
find the Web of Science entry_ in the library's online catalog. You may be prompted 
to log in to the University's Central Authentication System. 

.. _entry: http://library.lib.asu.edu/record=e1000458

.. image:: images/tutorial/getting.0.png
   :width: 600

Perform a search for literature of interest using the interface provided.

.. image:: images/tutorial/getting.1.png
   :width: 600

Once you have found the papers that you are interested in, find the "Send to:" menu
at the top of the list of results. Click the small orange down-arrow, and select
"Other File Formats".

.. image:: images/tutorial/getting.2.png
   :width: 600

A small in-browser window should open in the foreground. Specify the range of
records that you wish to download. **Note that you can only download 500 records
at a time**, so you may have to make multiple download requests. Be sure to specify
"Full Record and Cited References" in the *Record Content* field, and "Plain Text"
in the *File Format* field. Then click "Send".

.. image:: images/tutorial/getting.3.png
   :width: 600

After a few moments, a download should begin. WoS usually returns a field-tagged
data file called "savedrecs.txt". Put this in a location on your filesystem where
you can find it later; this is the input for Tethne's WoS reader methods.

.. image:: images/tutorial/getting.4.png
   :width: 600

Structure of the WoS Field-Tagged Data File
-------------------------------------------

If you open the text file returned by the WoS database (usually named 'savedrecs.txt'), you should see a whole bunch of
field-tagged data. "Field-tagged" means that each metadata field is denoted by a "tag" (a two-letter code), followed by
values for that field. A complete list of WoS field tags can be found here_. For best results, you should avoid making
changes to the contents of WoS data files.

.. _here: http://images.webofknowledge.com/WOKRS53B4/help/WOS/hs_wos_fieldtags.html

The metadata record for each paper in your data file should begin with:

.. code-block:: none

   PT J

...and end with:

.. code-block:: none:

   ER

There are two author fields: the AU field is always provided, and values take the form "Last, FI". AF is provided if
author full-names are available, and values take the form "Last, First Middle". For example:

.. code-block:: none

   AU Dauvin, JC
      Grimes, S
      Bakalem, A
   AF Dauvin, Jean-Claude
      Grimes, Samir
      Bakalem, Ali

Citations are listed in the CR block. For example:

.. code-block:: none:

   CR Airoldi L, 2007, OCEANOGR MAR BIOL, V45, P345
      Alexander Vera, 2011, Marine Biodiversity, V41, P545, DOI 10.1007/s12526-011-0084-1
      Arvanitidis C, 2002, MAR ECOL PROG SER, V244, P139, DOI 10.3354/meps244139
      Bakalem A, 2009, ECOL INDIC, V9, P395, DOI 10.1016/j.ecolind.2008.05.008
      Bakalem Ali, 1995, Mesogee, V54, P49
      …
      Zenetos A, 2005, MEDITERR MAR SCI, V6, P63
      Zenetos A, 2004, CIESM ATLAS EXOTIC S, V3

For more information about WoS field tags, see a list on the Thompson Reuters website, here_.

.. _here: http://images.webofknowledge.com/WOKRS53B4/help/WOS/hs_wos_fieldtags.html
