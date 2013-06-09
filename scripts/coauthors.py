import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
records = rd.build(filepath)

import tethne.networks as nt
coauthors = nt.nx_coauthors(records) 

import tethne.writers as wr
wr.to_sif(coauthors, "/home/apoh/Repository/output/coauthors")
