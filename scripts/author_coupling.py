import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
records = rd.build(filepath)

import tethne.networks as nt
author_coup = nt.nx_author_coupling(records,1) 

import tethne.writers as wr
wr.to_sif(author_coup, "/home/apoh/Repository/output/author_coupling")
