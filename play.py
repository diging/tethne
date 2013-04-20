import tethne as t

l = t.wos_library("./data/davidson/WoS-combined.txt")
bc = l.bibliographicCoupling(6)
ac = l.authorCoupling(2)

f = open("./data/davidson/prob.csv", "w")
match = []

print len(bc.edges(data=True))

#for b_edge in bc.edges(data=True):
#    for a_edge in ac.edges(data=True):
#        if ((b_edge[0] == a_edge[0]) and (b_edge[1] == a_edge[1])) or ((b_edge[0] == a_edge[1]) and (b_edge[1] == a_edge[0])):
#            f.write (b_edge[0] + "," + b_edge[1] + "," + str(b_edge[2]['overlap']) + "," + str(a_edge[2]['overlap']) + "\n")
#            match.append( (b_edge[0], b_edge[1]) )
#print len(match)


thresh = 2

g = open("./data/davidson/matching.eda", "w")
g.write("matching\n")

#for thresh in range (0, 20):
#    out_string = ""
#    for athresh in range(0,20):
#        author_but_no_biblio = 0
#        biblio_but_no_author = 0
#        comparisons = 0
#        matched = 0
#        for x in range(0, len(l.library)):
#            for i in range(x, len(l.library)):
#                citation_overlap = 0
#                authorial_overlap = 0
#                if x != i:
#                    try:
#                        citation_overlap = len(set(l.library[x].citations) & set(l.library[i].citations))
#                    except TypeError:
#                        citation_overlap = 0
#                    try:
#                        authorial_overlap = len(set(l.library[x].meta['AU']) & set(l.library[i].meta['AU']))
#                    except TypeError:
#                        authorial_overlap = 0
#                    if (authorial_overlap <= athresh and citation_overlap > thresh):
#                        biblio_but_no_author += 1
#                    if (authorial_overlap > athresh and citation_overlap <= thresh):
#                        author_but_no_biblio += 1
#                    if (authorial_overlap > athresh and citation_overlap > thresh):
#                        matched += 1
#                    if (authorial_overlap > athresh or citation_overlap > thresh):
#                        comparisons += 1
#                    #f.write (str(citation_overlap) + "," + str(authorial_overlap) + "\n")
#        g.write (l.library[x].identifier + " (overlap) " + l.library[i].identifier + " = " + str(float(matched)/(float(author_but_no_biblio) + float(biblio_but_no_author))) + "\n")
#        out_string += str(float(matched)/(float(author_but_no_biblio) + float(biblio_but_no_author))) + ","
#    print out_string
        
#    print str(comparisons) +","+str(matched)+","+str(author_but_no_biblio)+"," +str(biblio_but_no_author)

h = open("./data/davidson/test.sif", "w")

max_a = max_b = 0
for entry in l.library:
    try:
        if len(entry.citations) > max_b:
            max_b = len(entry.citations)
    except TypeError:
        pass
    try:
        if len(entry.meta['AU']) > max_a:
            max_a = len(entry.meta['AU'])
    except TypeError:
        pass

for x in range(0, len(l.library)):
    for i in range(x, len(l.library)):
        if x != i:
            try:
                citation_overlap = len(set(l.library[x].citations) & set(l.library[i].citations))
            except TypeError:
                citation_overlap = 0
            try:
                authorial_overlap = len(set(l.library[x].meta['AU']) & set(l.library[i].meta['AU']))
            except TypeError:
                authorial_overlap = 0

            rel_b = float(citation_overlap)/max_b
            rel_a = float(authorial_overlap)/max_a



            diff = abs(rel_b - rel_a)

            inv_diff = 1/(diff)

            g.write (l.library[x].identifier.replace(" ","_") + " (overlap) " + l.library[i].identifier.replace(" ","_") + " = " + str(inv_diff) + "\n")
            if (citation_overlap > 2 or authorial_overlap > 1):
                h.write(l.library[x].identifier.replace(" ","_") + " overlap " + l.library[i].identifier.replace(" ","_") + "\n")

