import tethne.readers as rd
filepath = "../testsuite/testin/paper_cocitations#62809724.txt"
#filepath = "../testsuite/testin/iptraffic.txt"
wos_list = rd.wos.parse_wos(filepath)

meta_list=rd.wos.wos2meta(wos_list)

import tethne.networks as nt


coinst = nt.papers.cocitation(meta_list, 2,10,'True')
counts = nt.papers.citation_count(meta_list)
top,counts = nt.papers.top_cited(meta_list)
top_parent,top,counts= nt.papers.top_parents(meta_list)
print "cocit", counts
print "top", top
print "top_parent########"

for p in top_parent:
    print "Papers:#########",p['ayjid']


#asstr=('ADRIANO D. 2001 TRACE ELEMENTS TERRE', 'RAO J 1992 RNEA TECHN B SER LAN')
#print asstr[1]

import tethne.writers as wr
wr.graph.to_gexf(coinst, "../testsuite/testout/cocitation_1threshold_dec31")