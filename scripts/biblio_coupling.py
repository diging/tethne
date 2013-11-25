import tethne.readers as rd
filepath = "../testsuite/testin/savedrecs.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
biblios = nt.citations.bibliographic_coupling(meta_list, 'ayjid', 1, 'ayjid',
                                'atitle', 'date', 'badkey', 'jtitle') 

import tethne.writers as wr
wr.graph.to_gexf(biblios, "../testsuite/testout/biblio_coupling")
