import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
cites, internal_cites = nt.nx_citations(meta_list, 'ayjid') 

import tethne.writers as wr
wr.to_sif(cites, "/home/apoh/Repository/output/citations")
wr.to_xgmml(cites, "/home/apoh/Repository/output/citations")
