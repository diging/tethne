# Tethne
Tethne is a script for analyzing citation data. Right now it just works on data from the Web of Science, but hopefully it will be expanded to work on data from other sources as well. It generates a variety of networks, such as bibliographic coupling, citation, author-paper, and co-author networks, using networkx. 

## Warning
This code is hacked together in a short amount of time to serve my own (academic) purposes. I'm not a software developer, and the code is far from polished. If you have ideas about how to make this better, go right ahead and contribute some code.

## Collecting Web of Science data
To use Tethne you need a Web of Science data file to work with. One such file is docs/savedrecs.txt. This file was generated from the Web of Science by first following the Web of Science's recommended search "oil spill\* mediterranean" on the Web of Science tab of the Web of Knowledge service.  

![alt-text](https://github.com/erickpeirson/tethne/docs/WebOfScienceSearch.png "Web of Science Search")  

If you scroll down to the bottom of the search results page, you will see a set of options to save your search results.  

![alt-text](https://github.com/erickpeirson/tethne/docs/WebOfScienceResults.png "Web of Science Results")  

Select a set of "Records" (we could have specified 1 to 156, the number of "Results" for this query), select "Full Record" and "Cited References" if you would like to utilize the full extent of Tethne's power, and finally "Save to Plain Text" your results, by default named "savedrecs.txt". An example savedrecs.txt for this tutorial is also provided in tethne/docs/.

## Requirements
* [Python](http://www.python.org/)
* [NetworkX](http://networkx.github.io/)

I think that's it...

## Questions?
erick [dot] peirson [at] asu [dot] edu
