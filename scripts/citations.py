#right now this crashes: next step is to make networks not make any attributes
#with value of None
import tethne.readers as rd
#filepath = "../docs/savedrecs.txt"
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/semantic_web.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
cites, internal_cites = nt.citations.direct_citation(meta_list, 'ayjid', 'atitle', 'date',
                                        'badkey', 'jtitle') 

import tethne.writers as wr
wr.graph.to_gexf(cites, "/Users/ramki/tethne/tethne/output/cites" )
wr.graph.to_gexf(internal_cites, "/Users/ramki/tethne/tethne/output/internal_cites")
