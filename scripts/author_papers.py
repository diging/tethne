import tethne.readers as rd
filepath = "/home/apoh/Repository/tethne/docs/savedrecs.txt"
wos_list = rd.wos.parse_wos(filepath)
meta_list = rd.wos.wos2meta(wos_list)

import tethne.networks as nt
author_papers = nt.authors.author_papers(meta_list, 'ayjid', 'date', 'badkey',
                                    'atitle')

import tethne.writers as wr
wr.graph.to_gexf(author_papers, "/home/apoh/Repository/output/author_papers")
