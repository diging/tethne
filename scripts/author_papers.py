import tethne.readers as rd
filepath = "/home/apoh/Repository/tethne/docs/savedrecs.txt"
records = rd.build(filepath)

import tethne.networks as nt
author_papers = nt.nx_author_papers(records) 

import tethne.writers as wr
wr.to_sif(author_papers, "/home/apoh/Repository/output/author_papers")
