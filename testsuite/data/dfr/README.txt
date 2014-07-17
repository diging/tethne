README

Hello and thank you for downloading this dataset from the JSTOR Data for Research site.  If you have any questions, please contact us at dfr@jstor.org.

Also, you should be aware that the size of the generated dataset will often be less than the number of documents selected during your dataset building process performed on the DfR site.  For most accounts, a limit of 1,000 documents has been set for downloaded datasets.  Larger datasets may be requested by contacting us at dfr.jstor.org.  In those cases where the selection is more than permitted by the account limit, the documents returned in the dataset are selected by random sample.

--------------
Terms of Use:
--------------

"Data for Research Content” means textual extractions; information describing and/or identifying content, usage, and operations; and cataloging information pertaining to the JSTOR Archive, to be used in research involving computational analysis rather than for purposes of understanding the intellectual meaning of such content.  

By accessing the JSTOR Archive for Data for Research Content, you accept and agree to be bound by JSTOR’s standard Terms and Conditions of Use available at http://www.jstor.org/about/terms.html. Please refer to Sections 2.1 and 2.2 for permitted and prohibited uses of the Content in the JSTOR Archive, including Data for Research Content and Section 5.3 for disclaimers.

---------------
Privacy Policy:
---------------

For information on JSTOR's privacy policy, please refer to: http://dfr.jstor.org/privacy-policy

----
FAQ: 
----

An FAQ for the Data for Research program is available at http://dfr-test.jstor.org/faq.  Please consult this page for information if you don't find what you are looking for in this document.


------------------
About the Dataset:
------------------
 
If you are reading this, you have already successfully downloaded the dataset from the website and unzipped it.  The dataset is structured as follows:

	- Data Type Directory
	 - {documentid 1}.[csv|xml]
	 - {documentid 2}.[csv|xml]
	- manifest.txt
	- citations.[csv|xml]
	- README.txt

We will now explain each one of these files in detail.

------------
manifest.txt
------------
The manifest file contains basic information about the request including title, requester, query terms used, processing date, number of documents returned, etc.


-------------------
citations.[csv|xml]
-------------------
This citations file (which may be formatted as either CSV or XML) contains an entry for each document associated the dataset - either a comma delimited list or an XML element containing the metadata for each document.  The metadata provided includes, ISSN, document id, document title, journal title, publisher, date of publication, authors, copyright notice, article type, volume and issue numbers, language, and a stable URL linking to document location on the JSTOR main site.

Multiple authors will be separated by a semicolon (e.g. "Joe Smith; Michael Johnson").  

Article types are "research-article", "book-review", "misc". "news". and "editorial".  

----------------------
{documentid}.[csv|xml]
----------------------
The data files are found in 3rd level directories under the corresponding ISSN and year of publication directories.  The data files will be formatted as either CSV or XML files based on preferences stated during the dataset building process.  The filename is derived from the unique document identifier which is also contained in the citations.[csv|xml] file found in the dataset top-level directory.
