import tethne.readers as rd
filepath = "/Users/ramki/tethne/tethne/testsuite/testin/tissues.txt"
wos_list = rd.parse_wos(filepath)

for wos in wos_list:
    print wos,'\n'

meta_list=rd.wos2meta(wos_list)    

for meta in meta_list:
    print meta , '\n'
    
#import tethne.networks as nt
#author_coup = nt.nx_author_coupling(meta_list, 1, 'ayjid', 'atitle', 'date',
#                                    'badkey', 'jtitle') a

#import tethne.writers as wr
#wr.to_gexf(author_coup, "/home/apoh/Repository/output/author_coupling")
