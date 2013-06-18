import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
biblios = nt.nx_biblio_coupling(meta_list, 'ayjid', 1, 'ayjid', 
                                'atitle', 'date') 

import tethne.writers as wr
wr.to_graphml(biblios, "/home/apoh/Repository/output/biblio_coupling")
