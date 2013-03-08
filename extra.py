subset = library.getAll(lambda x: 1992 < int(x.pub_year) < 1995)

couplings = []  #   Will be a list of triple objects

direct = []


x = 0
while x < len(subset):
    i = 0
    node_added = 0
    while i < len(subset):
        if (i != x):    # don't compare to self
            overlap = library.overlap(subset[x], subset[i])     # This isn't quite right...
            if len(overlap) > threshold:
                for paper in overlap:
                    direct.append(triple(subset[x].identifier, "cites", paper))
                    direct.append(triple(subset[i].identifier, "cites", paper))
                
                #   This will add nodes for all paper in the library that fall within the specified time domain and have a coupling relationship above threshold.
                if node_added is 0:
                    nodes.append (wos_paper(subset[x].meta['UT'][0], subset[x].identifier,  subset[x].meta['SO'][0], int(subset[x].pub_year), subset[x].meta['DT'][0], subset[x].meta['TI'][0], subset[x].authors, subset[x].citations))
                    node_added = 1
                #   Add triple to couplings list
                t = triple(subset[x].meta['UT'][0], "bc", subset[i].meta['UT'][0], {'overlap': str(len(overlap)), 'start': max(subset[i].pub_year,subset[x].pub_year)})
                couplings.append(t)
        i = i + 1
    x = x + 1

f = open("./ack.sif", "w")
for d in direct:
    f.write(d.subject.replace(" ", "_") + "\t" + d.predicate + "\t" + d.object.replace(" ", "_") + "\n")
f.close



#library.compareAbsolute(options.overlap_threshold,options.output_path, 1992, 1995)
            