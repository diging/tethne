import tethne.readers as rd
filepath = "../testsuite/testin/instituitions_2_types_input.txt"
wos_list = rd.wos.parse_wos(filepath)

meta_list=rd.wos.wos2meta(wos_list)

import tethne.networks as nt
author_coinst = nt.authors.author_coinstitution(meta_list, 1)

import tethne.writers as wr
wr.graph.to_gexf(author_coinst, "../testsuite/testout/author_coinstitutions")

