import tethne.readers as rd
import networkx as nx
from collections import defaultdict

filepath = "../testsuite/testin/coauthors_2_recs.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
coauthors = nt.authors.coauthors(meta_list, 'date','jtitle','ayjid')

print "comes here################"
import tethne.writers as wr
wr.graph.to_sif(coauthors, "../testsuite/testout/coauthors_code_jan07")

print coauthors.nodes()
print '### edges######'

coauthors_list=coauthors.edges(data=True)

coauthors_dict={(a[0],a[1]): a[2:] for a in coauthors_list}


print "co auhor dict",coauthors_dict
print "####edge attribs ########", 'ayjid'
print nx.get_edge_attributes(coauthors,'ayjid')
print "####edge attribs ########", 'date'
print nx.get_edge_attributes(coauthors,'date')
print "####edge attribs ########", 'jtitle'
print nx.get_edge_attributes(coauthors,'jtitle')
