import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
records = rd.build(filepath)

import tethne.networks as nt
biblios = nt.nx_biblio_coupling(records,1) 

import tethne.writers as wr
wr.to_sif(biblios, "/home/apoh/Repository/output/biblio_coupling")
