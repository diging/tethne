import tethne.readers as rd
import networkx as nx
filepath = "../testsuite/testin/coauthors_2_recs.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
coauthors = nt.authors.coauthors(meta_list, 'date','jtitle','ayjid')

print "comes here################"
#import tethne.writers as wr
#wr.graph.to_gexf(coauthors, "../testsuite/testout/coauthors_code_jan07")

print coauthors.nodes()
print '### edges######'
print coauthors.edges()
print "####edge attribs ########"
print nx.get_edge_attributes(coauthors,'ayjid')
print nx.get_edge_attributes(coauthors,'date')
print nx.get_edge_attributes(coauthors,'jtitle')
