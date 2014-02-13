Getting Bibliographic Data
==========================

The current version of Tethne supports bibliographic data from the ISI Web of Science
and JSTOR's Data-for-Research portal. Future releases will support data from PubMed and
Scopus.

Getting Data from the Web of Science
------------------------------------

The ISI Web of Science is a proprietary database owned by Thompson Reuters. 
If you are affiliated with an academic institution, you may have access to
this database via an institutional license.

To access the Web of Science database via the Arizona State University library,
find the Web of Science entry_ in the library's online catalog. You may be prompted 
to log in to the University's Central Authentication System. 

.. _entry: http://library.lib.asu.edu/record=e1000458

.. image:: _static/images/tutorial/getting.0.png
   :width: 600

Perform a search for literature of interest using the interface provided.

.. image:: _static/images/tutorial/getting.1.png
   :width: 600

Once you have found the papers that you are interested in, find the "Send to:" menu
at the top of the list of results. Click the small orange down-arrow, and select
"Other File Formats".

.. image:: _static/images/tutorial/getting.2.png
   :width: 600

A small in-browser window should open in the foreground. Specify the range of
records that you wish to download. **Note that you can only download 500 records
at a time**, so you may have to make multiple download requests. Be sure to specify
"Full Record and Cited References" in the *Record Content* field, and "Plain Text"
in the *File Format* field. Then click "Send".

.. image:: _static/images/tutorial/getting.3.png
   :width: 600

After a few moments, a download should begin. WoS usually returns a field-tagged
data file called "savedrecs.txt". Put this in a location on your filesystem where
you can find it later; this is the input for Tethne's WoS reader methods.

.. image:: _static/images/tutorial/getting.4.png
   :width: 600

Structure of the WoS Field-Tagged Data File
```````````````````````````````````````````

If you open the text file returned by the WoS database (usually named 'savedrecs.txt'), 
you should see a whole bunch of field-tagged data. "Field-tagged" means that each metadata
field is denoted by a "tag" (a two-letter code), followed by values for that field. A 
complete list of WoS field tags can be found here_. For best results, you should avoid 
making changes to the contents of WoS data files.

.. _here: http://images.webofknowledge.com/WOKRS53B4/help/WOS/hs_wos_fieldtags.html

The metadata record for each paper in your data file should begin with:

.. code-block:: none

   PT J

...and end with:

.. code-block:: none:

   ER

There are two author fields: the AU field is always provided, and values take the form 
"Last, FI". AF is provided if author full-names are available, and values take the form 
"Last, First Middle". For example:

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

For more information about WoS field tags, see a list on the Thompson Reuters website, 
here_.

.. _here: http://images.webofknowledge.com/WOKRS53B4/help/WOS/hs_wos_fieldtags.html

Getting Data from JSTOR Data-for-Research
-----------------------------------------

The `JSTOR Data-for-Research (DfR) portal <http://dfr.jstor.org/?&helpview=about_dfr>`_
gives researchers access to bibliographic data and N-grams for the entire JSTOR database. 
Tethne can use DfR data to generate coauthorship networks, and to improve metadata for Web
of Science records. Increasingly, Tethne is also able to use N-gram counts to add 
information to networks, and can generate corpora for common topic modeling tools (coming 
soon!).

Access the DfR portal at 
`http://dfr.jstor.org/ <http://dfr.jstor.org/>`_ If you don't already have an account, 
you will need to `create a new account <http://dfr.jstor.org/accounts/register/>`_. 

After you've logged in, perform a search using whatever criteria you please. When you have
achieved the result that you desire, create a new dataset request. Under the "Dataset
Request" menu in the upper-right corner of the page, click "Submit new request".

.. image:: _static/images/tutorial/getting.5.png
   :width: 600
   
On the **Download Options** page, select your desired **Data Type**. If you do not intend 
to make use of the contents of the papers themselves, then "Citations Only" is sufficient.
Otherwise, choose word counts, bigrams, etc.

**Output Format** should be set to **XML**.

Give your request a title, and set the maximum number of articles. *Note that the maximum
documents allowed per request is 1,000. Setting **Maximum Articles** to a value less than
the number of search results will yield a random sample of your results.*

.. image:: _static/images/tutorial/getting.6.png
   :width: 600
   
Your request should now appear in your list of **Data Requests**. When your request is
ready (hours to days later), you will receive an e-mail with a download link. When
downloading from the **Data Requests** list, be sure to use the link in the 
**full dataset** column.

.. image:: _static/images/tutorial/getting.7.png
   :width: 600
   
When your dataset download is complete, unzip it. The contents should look something like 
those shown below.

.. image:: _static/images/tutorial/getting.8.png
   :width: 600

`citations.XML` contains bibliographic data in XML format. The `bigrams`, `trigrams`, 
`wordcounts` folders contain N-gram counts for each document.

In the example above, the path this dataset is 
`/Users/erickpeirson/Downloads/DfR/ecology_1960-64`. This is the path used in
:func:`tethne.readers.dfr.read` .
