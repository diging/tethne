import tethne.readers as rd
filepath = "../testsuite/testin/instituitions_2_types_input.txt"
wos_list = rd.wos.parse_wos(filepath)


print ' wos_list is done '

for c1 in wos_list:
    print c1['C1'],'\n'

meta_list=rd.wos.wos2meta(wos_list)

for paper in meta_list:
    print paper['institutions'],'\n'
    
import tethne.networks as nt
author_inst = nt.authors.author_institution(meta_list, 'date',  'jtitle')

import tethne.writers as wr
wr.graph.to_gexf(author_inst, "../testsuite/testout/author_institutions")