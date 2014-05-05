import tethne.readers as rd
filepath = "../testsuite/testin/savedrecs.txt"
wos_list = rd.wos.parse(filepath)
meta_list = rd.wos.convert(wos_list)

import tethne.networks as nt
author_papers = nt.authors.author_papers(meta_list, 'ayjid', 'date', 'badkey',
                                    'atitle')

import tethne.writers as wr
wr.graph.to_gexf(author_papers, "../testsuite/testout/author_papers")
