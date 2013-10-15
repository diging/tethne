#right now this crashes: next step is to make networks not make any attributes
#with value of None
import tethne.readers as rd
#filepath = "../docs/savedrecs.txt"
filepath = "C:\Users\Ramki\Downloads\savedrecs.txt"
wos_list = rd.parse_wos(filepath) 
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
cites, internal_cites = nt.nx_citations(meta_list, 'ayjid', 'atitle', 'date',
                                        'badkey', 'jtitle') 

import tethne.writers as wr
wr.to_gexf(cites, "C:\Users\Ramki\Downloads\cites_output")
wr.to_gexf(internal_cites, "C:\Users\Ramki\Downloads\interal_cites_output")
