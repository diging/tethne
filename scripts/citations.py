#right now this crashes: next step is to make networks not make any attributes
#with value of None
import tethne.readers as rd
#filepath = "../docs/savedrecs.txt"
filepath = "../testsuite/testin/semantic_web.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
cites, internal_cites = nt.citations.direct_citation(meta_list, 'ayjid', 'atitle', 'date',
                                        'badkey', 'jtitle') 

import tethne.writers as wr
wr.graph.to_gexf(cites, "../testsuite/testout/cites" )
wr.graph.to_gexf(internal_cites, "../testsuite/testout/internal_cites")
