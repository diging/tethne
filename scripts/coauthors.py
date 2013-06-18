import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
coauthors = nt.nx_coauthors(meta_list, 'atitle', 'date', 'badkey', 'jtitle') 

import tethne.writers as wr
wr.to_gexf(coauthors, "/home/apoh/Repository/output/coauthors")
