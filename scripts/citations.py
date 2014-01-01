#right now this crashes: next step is to make networks not make any attributes
#with value of None
# import tethne.readers as rd
# #filepath = "../docs/savedrecs.txt"
# filepath = "../testsuite/testin/cocitations_test_2recs.txt"
# wos_list = rd.wos.parse_wos(filepath)
# meta_list = rd.wos.wos2meta(wos_list)
# 
# import tethne.networks as nt
# cites, internal_cites = nt.citations.direct_citation(meta_list, 'ayjid', 'atitle', 'date',
#                                         'badkey', 'jtitle') 
# 
# import tethne.writers as wr
# wr.graph.to_gexf(cites, "../testsuite/testout/cites" )
# wr.graph.to_gexf(internal_cites, "../testsuite/testout/internal_cites")

#making some changs for testing new fork feature.

import tethne.readers as rd
import networkx as nx
#filepath = "../docs/savedrecs.txt"
filepath = "../testsuite/testin/citations_test.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
cites, internal_cites = nt.papers.direct_citation(meta_list, 'ayjid', 'atitle', 'date')

print "------Cites Nodes----"
print cites.nodes()
print "####Cites Edges####"
print cites.edges()
print "----Internal Cites--"
print internal_cites.nodes()
print internal_cites.edges()

c_des = nx.descendants(cites,'ALAMPORA G 1999 INFORMATION SCIENCES')
i_des = nx.descendants(internal_cites,'WU Z 2012 NEUROCOMPUTING')
c_ans = nx.ancestors(cites,'Hu J. 2008 SIGIR 08')
i_ans = nx.ancestors(internal_cites,'WU Z 2012 NEUROCOMPUTING')
print '####cites des#####:', c_des
print 'Internal des:', i_des

print '----cites ans------:', c_ans
print '-----Internal ans----:', i_ans

is_directed = cites.is_directed()
is_dag = nx.is_directed_acyclic_graph(cites)
print 'Is it directed? :' , is_directed
print 'Is it dag :' , is_dag
