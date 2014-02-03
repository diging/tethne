datapath = "/Users/erickpeirson/Dropbox/collins_project/eco mono/Eco Mono.txt"
datapath1 = "/Users/erickpeirson/Dropbox/collins_project/ecology/ecology_complete.txt"
datapath2 = "/Users/erickpeirson/Dropbox/collins_project/j anim eco/J Anim Eco.txt"
datapath3 = "/Users/erickpeirson/Dropbox/collins_project/j eco/J Eco.txt"

import tethne.readers as rd
import tethne.networks as nt
import tethne.data as dt
import tethne.analyze as az
import tethne.writers as wr

wl = rd.wos.parse_wos(datapath)
wl += rd.wos.parse_wos(datapath1)
wl += rd.wos.parse_wos(datapath2)
wl += rd.wos.parse_wos(datapath3)
papers = rd.wos.wos2meta(wl)

pub_dates = [ p['date'] for p in papers ]
min_date = min(pub_dates)
max_date = max(pub_dates)

window_size = 5
step = 1

C = dt.GraphCollection()

for start in xrange(min_date, max_date-(window_size-2), step):
    end = start + 3

    p_slice = [ p for p in papers if start <= p['date'] < end ]

    C[start] = nt.papers.cocitation(p_slice, 3, topn=150, verbose=False)

bc = az.collection.algorithm(C, 'betweenness_centrality')

hist = az.collection.node_history(C, 'TURESSON G 1922 HEREDITAS', 'times_cited')

wr.collection.to_dxgmml(C, '/Users/erickpeirson/Dropbox/collins_project/eco mono/dx.xgmml')
print hist