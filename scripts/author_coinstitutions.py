import tethne.readers as rd
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/instituitions_2_types_input.txt"
wos_list = rd.parse_wos(filepath)

for wos in wos_list:
    print wos,'\n'
print ' am done '
meta_list=rd.wos.wos2meta(wos_list)

for meta in meta_list:
    print meta , '\n'
    
import tethne.networks as nt
author_coinst = nt.authors.author_coinstitution(meta_list, 1)

import tethne.writers as wr
wr.graph.to_gexf(author_coinst, "/Users/ramki/tethne/tethne/output/author_coinstitutions")

