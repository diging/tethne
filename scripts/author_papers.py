import tethne.readers as rd
filepath = "/home/apoh/Repository/tethne/docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.networks as nt
author_papers = nt.nx_author_papers(meta_list, 'ayjid', 'date', 'badkey', 
                                    'atitle')

import tethne.writers as wr
wr.to_gexf(author_papers, "/home/apoh/Repository/output/author_papers")
