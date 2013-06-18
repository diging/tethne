import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

#set any keys you want to use as a list; this puts all of them
import tethne.data_struct as ds
keys = ds.new_meta_dict().keys()

import tethne.networks as nt
coauthors = nt.nx_coauthors(meta_list, *keys) 
#this is equivalent to
#coauthors = nt.nx_coauthors(meta_list, aulast, auinit, jtitle, atitle, ...)

import tethne.writers as wr
wr.to_gexf(coauthors, "/home/apoh/Repository/output/coauthors")
