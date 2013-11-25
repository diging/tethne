import tethne.readers as rd
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/tissues.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
author_coup = nt.authors.author_coupling(meta_list, 1, 'ayjid', 'atitle', 'date',
                                    'badkey', 'jtitle') 

import tethne.writers as wr
wr.graph.to_gexf(author_coup, "/Users/ramki/output/author_coupling")
