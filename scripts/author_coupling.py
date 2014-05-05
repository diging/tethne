import tethne.readers as rd
filepath = "../testsuite/testin/tissues.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
author_coup = nt.papers.author_coupling(meta_list, 1, 'ayjid', 'atitle', 'date',
                                    'badkey', 'jtitle') 

import tethne.writers as wr
wr.graph.to_gexf(author_coup, "../testsuite/testout/author_coupling")
