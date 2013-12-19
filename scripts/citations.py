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


import tethne.readers as rd
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

c_des = nt.papers.descendants(cites,'Abdullah S 2012 INFORM SCIENCES')
i_des = nt.papers.descendants(internal_cites,'ACAMPORA G 2013 INFORMATION SCIENCES')

c_ans = nt.papers.ancestors(cites,'Borda J. 1981 MEMOIRE ELECTIONS SC')
#i_ans = nt.citations.ancestors(internal_cites,'Borda J. 1981 MEMOIRE ELECTIONS SC')

#print 'cites des:', c_des
#print 'Internal des:', i_des

print 'cites ans:', c_ans
#print 'Internal ans:', i_ans

is_directed = cites.is_directed()
is_dag = nt.papers.is_directed_acyclic_graph(cites)
print 'Is it directed? :' , is_directed
print 'Is it dag :' , is_dag