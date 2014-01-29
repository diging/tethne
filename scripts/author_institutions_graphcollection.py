import tethne.readers as rd

filepath = "../testsuite/testin/instituitions_2_types_input.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list=rd.wos.wos2meta(wos_list)

import tethne.data as ds
g1 = ds.GraphCollection()



import tethne.networks as nt
author_inst = nt.authors.author_institution(meta_list, 'date',  'jtitle')



g1.dump_objects\
         (author_inst,"../testsuite/testout/author_institutions_dumped.txt")

loaded= \
         g1.load_objects("../testsuite/testout/author_institutions_dumped.txt")

from pprint import pprint
pprint(loaded)

import tethne.writers as wr
wr.collection.to_dxgmml(g1,"../testsuite/testout/author_institutions_graph")