import tethne.readers as rd
#filepath = '../testsuite/testin/data_validation.txt'
filepath = '../testsuite/testin/iptraffic.txt'
wos_list = rd.wos.parse_wos(filepath)
wos_list = rd.wos.parse_wos(filepath)

#cr = rd.wos.parse_cr("[Anonymous], 2012, 3015452 ETSI EN")
#print "CR values:",cr['aulast'], cr['auinit']
meta_list = rd.wos.wos2meta(wos_list)

#for paper in meta_list:
#	print paper['aulast']


import tethne.networks as nt
coinst = nt.authors.author_cocitation(meta_list, 1)

print 'networks created'

import tethne.writers as wr
wr.graph.to_gexf(coinst, "../testsuite/testout/cocitation_anonymus_nodes_check")

