import tethne.readers as rd
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/tissues.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
author_coup = nt.nx_author_coupling(meta_list, 1, 'ayjid', 'atitle', 'date',
                                    'badkey', 'jtitle') 

import tethne.writers as wr
wr.to_gexf(author_coup, "/Users/ramki/output/author_coupling")
