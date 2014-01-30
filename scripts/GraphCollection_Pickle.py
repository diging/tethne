import tethne.readers as rd
from pprint import pprint

#filepath = "../testsuite/testin/instituitions_2_types_input.txt"
filepath = "../testsuite/testin/iptraffic.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list=rd.wos.wos2meta(wos_list)

import tethne.data as ds
g1 = ds.GraphCollection()
g2 = ds.GraphCollection()


# DiGraph and MultiGraph so these cannot be used as a parameter
# to GraphCollection

#import tethne.networks as nt
#author_inst = nt.authors.author_institution(meta_list, 'date',  'jtitle')

#import tethne.networks as nt
#cites, internal_cites = nt.papers.direct_citation(meta_list, 'ayjid', #'atitle', 'date')



# Generate Author coupling and co-authors networks networks 

import tethne.networks as nt
coauthors = nt.authors.coauthors(meta_list, 'date','jtitle','ayjid')
author_coup = nt.papers.author_coupling(meta_list, 1, 'ayjid', 'atitle', 'date')


g1.__setitem__('ayjid',coauthors)
g2.__setitem__('ayjid',author_coup)


# g1.__getitem__('ayjid')
#print g1.nodes()
#print g1.edges()

# Append 2 objects to


g2.dump_objects\
         (g2,"../testsuite/testout/dumped_graphcollections_objects.txt")

g1.dump_objects\
    (g1,"../testsuite/testout/dumped_graphcollections_objects.txt")

loaded= \
         g1.load_objects("../testsuite/testout/dumped_graphcollections_objects.txt")


