import sys
from optparse import OptionParser
import pickle
import datetime
from pprint import pprint

sys.path.append('/Users/erickpeirson/Dropbox/DigitalHPS/Scripts/Tethne/')
from tethne import wos_object
from tethne import triple
from tethne import wos_library
from tethne import wos_paper
from tethne import contains

class node:
    def __init__ (self, identifier, start, end):
        self.identifier = identifier
        self.start = start
        self.end = end

class edge:
    def __init__ (self, source, predicate, target, year):
        self.source = source
        self.predicate = predicate
        self.target = target
        self.year = year


identifier = "eco01"
data_path = "/Users/erickpeirson/Dropbox/collins_project/ecology/ecology_complete.txt"
out_file = "ack.xgmml"
threshold = 1

library = wos_library(identifier, data_path)
library.buildLibrary()

start = 1992
end = 1993


nodes = []
edges = []


for y in range(start, end+1):
    if (y + 2) > end:
        limit = end
    else:
        limit = y + 2
    subset = (library.getAll(lambda x: y <= int(x.pub_year) <= limit))
    for i in range(0, len(subset)):
        i_added = 0                                     #   Assuming that subset[i] is unique, this will save checking the node list on every pass to avoid redundancy.
        for x in range(i, len(subset)):                 #   Don't be redundant
            if i is not x:
                overlap = library.overlap(subset[x], subset[i])
                if overlap > threshold:
                    for o in overlap:
                        #   Add edges
                        edges.append(edge(subset[i], "cites", o, y))
                        edges.append(edge(subset[x], "cites", o, y))

idents = []

for edge in reversed(edges):
    #   Citing node
    try: 
        index = idents.index(edge.source.identifier)
    except ValueError:
        nodes.append(node(edge.source.identifier, int(edge.source.pub_year), int(edge.source.pub_year) + 2))
        idents.append(edge.source.identifier)
    #   Cited node
    try: 
        index = idents.index(edge.target)
    except ValueError:
        nodes.append(node(edge.target, int(edge.source.pub_year), int(edge.source.pub_year) + 2))
        idents.append(edge.target)

#   XGMML dynamic network
xgmml = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
xgmml += '\n<graph label="asdf" directed="1" id="5" start="{0}" end="{1}">'.format(start-1, end + 3)
for node in nodes:
    xgmml += '\n\t<node label="{0}" id="{0}" start="{1}" end="{2}" />'.format(node.identifier.replace("&","&amp;").replace(" ","_"), node.start, node.end)

for edge in edges:
    xgmml += '\n\t<edge source="{0}" target="{1}" />'.format(edge.source.identifier.replace("&","&amp;").replace(" ","_"), edge.target.replace("&","&amp;").replace(" ","_"))

xgmml += '\n</graph>'

out = open(out_file, "w")
out.write(xgmml)
out.close()
