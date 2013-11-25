import tethne.readers as rd
filepath = "../testsuite/testin/cocitations_test.txt"
wos_list = rd.wos.parse_wos(filepath)

meta_list=rd.wos.wos2meta(wos_list)

import tethne.networks as nt
coinst = nt.citations.cocitation(meta_list, 1, 2013)

import tethne.writers as wr
wr.graph.to_gexf(coinst, "../testsuite/testout/cocitation")
