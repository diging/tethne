import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
records = rd.build(filepath)

import tethne.networks as nt
cites, internal_cites = nt.nx_citations(records) 

import tethne.writers as wr
wr.to_sif(cites, "/home/apoh/Repository/output/citations")
