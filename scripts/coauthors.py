import tethne.readers as rd
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/instituitions_2_types_input.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
coauthors = nt.authors.coauthors(meta_list, 'citations', 'date', 'badkey', 'jtitle')

import tethne.writers as wr
wr.graph.to_sif(coauthors, "/Users/ramki/tethne/tethne/output/coauthors")
