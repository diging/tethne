import tethne.readers as rd
filepath = "../testsuite/testin/coauthors_2_recs.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
coauthors = nt.authors.coauthors(meta_list, 'date','jtitle','ayjid')

print "comes here################"
import tethne.writers as wr
wr.graph.to_gexf(coauthors, "../testsuite/testout/coauthors_code_jan07")

print coauthors.nodes()
print '@@@@@@@@edges@@@@@'
print coauthors.edges()