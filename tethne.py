"""# ISI Web of Science Triple Extraction Project 2012

Author:     Erick Peirson
Contact:    erick.peirson@asu.edu
   
The primary objective of this project is to generate networks of scientific publications from the Web of Science database. Existing citation analysis software (such as CiteSpace II) is primarily oriented toward co-citation analysis and visualization, and does not easily allow visualization and analysis of citation relationships themselves. This script aims to fill that void."""

from optparse import OptionParser
import pickle
import datetime
import sys
import gnosis
import Resources.networkx as nx

def contains(list, filter):
    """Searches a list for a pattern specified in a lambda function, filter."""
    for x in list:
        if filter(x):
            return True
    return False

class wos_object:
    """Each entry in the WoS data file becomes one of these.
Arguments:
identifier -- A CR-like string, e.g. "Last FM, 2012, J EXP BIOL, V210".
authors -- A dictionary that maps CR-like to AF-like.
citations -- A list of CR-like strings.
meta -- A dictionary, containing anything."""

    def __init__(self, authors, pub_year, identifier, wosid, journal, doc_type, meta, title, citations):
        self.authors = authors
        self.year = pub_year
        self.identifier = identifier
        self.citations = citations
        self.wosid = wosid
        self.journal = journal
        self.doc_type = doc_type
        self.meta = meta
        self.title = title
        
class wos_author:
    """Might want to get rid of this."""
    
    def __init__ (self, short_name, full_name, first_pub_year=None, address=None):
        self.short_name = short_name
        self.full_name = full_name
        self.first_pub_year = first_pub_year
        self.address = address

class wos_library:
    """The main class for handling WoS data. Data should be a path to an ISI WoS data file."""

    def __init__(self, data):
        self.data = data
        self.library = []   # A list of all wos_objects.
        self.build()
                    
    def getEntry(self, filter):
        """Returns the first entry matching the lambda function filter."""
        for x in self.library:
            if filter(x):
                return x
        return False
    
    def getAll(self, filter):
        """Returns a list of entries matching the lambda function filter."""
        results = []
        for x in self.library:
            if filter(x):
                results.append(x)
        return results
    
    def build(self):
        """Reads self.data file, and builds self.library, a list of wos_objects."""
        f = open(self.data, 'r')
        cache = {}                      # Will re-use for each record
        for line in f:
            line = line.replace("\n","").replace("\r","")
            if len(line) > 1:
                prefix = line[0:2]      # The WoS data file uses two-letter prefixes to indicate field types.
            else:
                prefix = 'XX'           # So that I can ignore useless lines later.                        
            if prefix == 'EF':          # At the end of the data file
                break
            if prefix == 'ER':          # At the end of a record (paper)
                identifier = cache['AU'][0].replace(",","") + ", " + cache['PY'][0] + ", " + cache['J9'][0]     # Create CR-like identifier for record
                identifier = identifier.upper()
                
                # TODO: Need to figure out why I did this....
                num_authors = 0
                authors = {}
                for au in cache['AU']:
                    num_authors += 1
                    found = 'false'
                    au_last = au.split(',')[0]
                    for af in cache['AF']:
                        af_last = af.split(',')[0]
                        if au_last.upper() == af_last.upper():
                            authors[au] = af
                            found = 'true'
                    if found != 'true':             # Maybe there is no AF entry
                        authors[au] = au
                cache['num_authors'] = num_authors
        
                title = ''
                for row in cache['TI']:             # Some titles bleed over into multiple rows
                    title += row
        
                self.library.append(wos_object(authors, int(cache['PY'][0]), identifier, cache['UT'][0], cache['SO'][0], cache['DT'][0], cache, title, cache['CR']))
        
                cache = {}              # Dump for next record
                cache['CR'] = None      # Prevents a KeyError if the record has no references.
            else:                   # We're still in the middle of a record...
                if (prefix != 'XX') and (prefix != ''):
                    if prefix == '  ':          # If there is no prefix, the line is part of the field to which the previous line belonged.
                        prefix = last_prefix
                    else:                       # If there is a prefix, the line is part of the next field.
                        cache[prefix] = []
                    if prefix != 'XX':          # XX means that the line was probably blank, above.
                        line_cache = line[3:].replace(".", "").upper()
                        
                        if prefix == 'CR':      # CR contains all of the paper's references
                            line_split = line_cache.split(",")
                            if len(line_split) > 3 :    # Only want author, year, journal/title, which are the first three comma-separated values
                                line_cache = line_split[0] + "," + line_split[1] + "," + line_split[2]                        
                        cache[prefix].append(line_cache)
            last_prefix = prefix
        return None
    
    def citationNetwork(self):
        """Create a NetworkX directed graph based on citation records. Returns both a global citation network (all citations), and an internal citation network (only where the cited papers are part of the data library)."""
        self.citation_network = nx.DiGraph()
        self.citation_network_internal = nx.DiGraph()
        for entry in self.library:
            if entry.citations is not None:
                for citation in entry.citations:
                    self.citation_network.add_edge(entry.identifier, citation,
                                                        rel="cites",
                                                        year=entry.year)
                    if (contains (self.library, lambda x: x.identifier == citation)):
                        self.citation_network_internal.add_edge(entry.identifier, citation,
                                                                    year=entry.year)
        return self.citation_network, self.citation_network_internal

    def authorPapers(self):
        """Generates an author-paper networka NetworkX directed graph."""
        self.author_paper = nx.DiGraph()
        for entry in self.library:
            for author in entry.authors:
                self.author_paper.add_edge(author, entry.identifier,
                                                rel="isAuthor",
                                                year=entry.year)
        return self.author_paper

    def coauthors(self):
        """Generates a co-author network, stored in self.coauthor_graph. Nodes are author names."""
        self.coauthor_graph = nx.Graph()
        for entry in self.library:
            for a in range(0, len(entry.authors)):       # Now all authors are indexed
                for b in range(a, len(entry.authors)):
                    if a is not b:
                        self.coauthor_graph.add_edge(a, b,
                                                        rel="coauthor",
                                                        year=entry.year,
                                                        paper=entry.identifier)
        return self.coauthor_graph

    def overlap(self,libObjA, libObjB):
        """Return number of shared objects between libObjA and libObjB; (e.g. references shared by two papers)."""
        if (libObjA.citations is None) or (libObjB.citations is None):
            return []
        else:
            return list(set(libObjA.citations) & set(libObjB.citations))

    def bibliographicCoupling(self, threshold):
        """Generates a bibliographic coupling network. Only couplings where the overlap is greater than or equal to the threshold will be included."""
        #subset = self.getAll(lambda x: start_year < int(x.year) < end_year)

        self.couplings = nx.Graph()
        for x in range(0, len(self.library)):
            for i in range(x, len(self.library)):
                if i != x:
                    overlap = self.overlap(self.library[x], self.library[i])
                    if len(overlap) >= threshold:
                        self.couplings.add_node(self.library[x].identifier,
                                                    wosid=self.library[x].wosid,
                                                    year=self.library[x].year)
                        self.couplings.add_node(self.library[i].identifier,
                                                    wosid=self.library[i].wosid,
                                                    year=self.library[i].year)
                        self.couplings.add_edge(self.library[x].identifier, self.library[i].identifier,
                                                    rel="overlap",
                                                    overlap=len(overlap),
                                                    i_overlap=1/len(overlap))
        return self.couplings

    def to_sif(self, graph, output_path):
        """Generates SIF output file from provided graph. 
        
output_path should be both path and a file prefix. E.g. if output_path = "./data/bob", then the main SIF file will be called "./data/bob.sif"."""
        f = open(output_path + ".sif", "w")
        att_files = {}
        natt_files = {}

        if 'edges' in dir(graph):   # If it quacks like a graph...
            edges = graph.edges(data=True)
            nodes = graph.nodes(data=True)
        else:
            return False
        
        for key, value in edges[0][2].iteritems():  # Generate an edge attribute file for each edge attribute.
            att_files[key] = open(output_path + "_" + key + ".eda", "w")
            att_files[key].write(key + "\n")

        for key, value in nodes[0][1].iteritems():
            natt_files[key] = open(output_path + "_" + key + ".noa", "w")
            natt_files[key].write(key + "\n")

        for edge in edges:
            f.write(str(edge[0]).replace(" ","_") + " " + edge[2]['rel'] + " " + str(edge[1]).replace(" ","_") + "\n")
            for key, value in edge[2].iteritems():
                att_files[key].write(str(edge[0]).replace(" ","_") + " (" + edge[2]['rel'] + ") " + str(edge[1]).replace(" ","_") + " = " + str(value) + "\n")
        for node in nodes:
            for key, value in node[1].iteritems():
                natt_files[key].write(str(node[0]).replace(" ","_") + " = " + str(value) + "\n")

        f.close()
        for key, value in att_files.iteritems():    # Close all of the edge attribute files.
            att_files[key].close()
        return None
        
    def to_xgmml (self, graph, name, output_path):
        """Generates dynamic XGMML output from provided graph."""
        
        f = open(output_path + ".xgmml", "w")
        f.write('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<graph directed="0"  xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:xlink="http://www.w3.org/1999/xlink" xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#" xmlns="http://www.cs.rpi.edu/XGMML">\n\t<att name="selected" value="1" type="boolean" />\n\t<att name="name" value="{0}" type="string"/>\n\t<att name="shared name" value="{0}" type="string"/>\n'.format(name))
        
        for node in graph.nodes(data=True):
            id = node[0]
            node_attributes = dict(node[1])
            if 'label' in node_attributes:
                label = node_attributes['label']
                del node_attributes['label']
            else:
                label = id
                
            if 'year' in node_attributes:
                start = node_attributes['year']
            
            f.write('\t<node id="{id}" label="{label}" start="{start}">\n'.format(id=id, label=label, start=start).replace('&','&amp;'))
            for key, value in node_attributes.iteritems():
                if (type (value).__name__ == "str"):
                    v_type = "string"
                elif (type (value).__name__ == "int"):
                    v_type = "integer"
                f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
            f.write('\t</node>\n')
            
        for edge in graph.edges(data=True):
            f.write ('\t<edge source="{}" target="{}">\n'.format(edge[0], edge[1]).replace('&','&amp;'))
            for key, value in edge[2].iteritems():
                if (type (value).__name__ == "str"):
                    v_type = "string"
                elif (type (value).__name__ == "int"):
                    v_type = "integer"

                f.write('\t\t<att name="{}" value="{}" type="{}" />\n'.format(key, value, v_type).replace('&','&amp;'))
            f.write('\t</edge>')
        f.write('</graph>')
        
        f.close()
        return None

    def to_gexf(self, graph, output_path):
        """Writes the provided graph to a GEXF-format network file."""

        nx.write_gexf(graph, output_path + ".gexf")
        return True

    def to_graphml(self, graph, output_path):
        """Writes the provided graph to a GraphML-format network file."""

        nx.write_graphml(graph, output_path + ".graphml")
        return True

    def export(self, file, format, delim):
        f = open(file, "w")
        if format is "csv":
            # Headers
            f.write( "Identifier" + delim + "Title" + delim + "Authors" + delim + "WoS Identifier" + delim + "Journal" + delim + "Volume" + delim + "Page" + delim + "DOI" + delim + "Num Authors\n" )
            for entry in self.library:
                # Authors are separated by a colon -> : <-
                authors = ""
                for author in entry.meta['AU']:
                    authors += ":" + author
                authors = authors[1:]
                datum = entry.identifier + delim + entry.meta['TI'][0] + delim + authors + delim + entry.wosid + delim + entry.meta['SO'][0]
                if 'VL' in entry.meta:
                    datum += delim + entry.meta['VL'][0]
                    if 'BP' in entry.meta:
                        datum += delim + entry.meta['BP'][0]
                    else:
                        datum += delim
                else:
                    datum += delim + delim
                if 'DI' in entry.meta:
                    datum += delim + entry.meta['DI'][0]
                else:
                    datum += delim
                datum += delim + str(entry.meta['num_authors'])
                f.write(datum + "\n")
        f.close()
        return None
            
    def dump (self, file):
        """Pickles the library."""
        f = open(file, 'wb')
        pickle.dump(self.library, f, -1)
        f.close()
        return True

    def undump (self, file):
        """This will load a pickled library from disk, and overwrite the current library."""
        f = open(file, 'rb')
        self.library = pickle.load(f)
        f.close()
        return True
    
    def authors_per_publication (self, file, start = 1900, end = datetime.datetime.now().year, slice = 1):
        """For Wes."""
        data = {}
        # TODO: should just return the data, rather than write it to file. Or have another method to do file-writing. Or something.
        f = open(file, 'w')
        f.write("\t".join(["Year","Mean","Variance","Min","Max","N"]) + "\n")
        
        for i in range (start, end):    # Populate fields for years
            data[i] = {}
            data[i]['values'] = []
        
        for entry in self.library:  # Add num_authors values to list for each year
            if start <= int(entry.year) <= end:
                data[int(entry.year)]['values'].append(entry.meta['num_authors'])

        for datum in data:          # Calculate average, min, max, variance
            data[datum]['n'] = float(len(data[datum]['values']))
            if data[datum]['n'] > 0:
                sum = 0             # Calculate the mean.
                for v in data[datum]['values']:
                    sum += v
                data[datum]['mean'] = sum/data[datum]['n']
            
                sum_diff2 = 0            # Calculate the variance.
                for v in data[datum]['values']:
                    diff = v - data[datum]['mean']
                    diff2 = diff*diff
                    sum_diff2 += diff2
                data[datum]['variance'] = sum_diff2/data[datum]['n']
            
                data[datum]['min'] = min(data[datum]['values'])
                data[datum]['max'] = max(data[datum]['values'])

                f.write("\t".join([str(datum), str(data[datum]['mean']), str(data[datum]['variance']), str( data[datum]['min']), str(data[datum]['max']), str(data[datum]['n'])]) + "\n")
        f.close()
        return None

def main():
    """Parses command-line options, and generates network output based on provided data."""
    
    parser = OptionParser()
    parser.add_option("-d", "--data-path", dest="data_path")
    parser.add_option("-n", "--network-type", dest="network_type")
    parser.add_option("-t", "--overlap-threshold", dest="overlap_threshold", type="int")
    parser.add_option("-o", "--output-path", dest="output_path")
    parser.add_option("-i", "--identifier", dest="identifier")
    parser.add_option("-f", "--network-format", dest="format")                    

    (options, args) = parser.parse_args()

    if (options.output_path[-1] != "/"):
        options.output_path += "/"

    if (options.data_path != ""):
        if (options.output_path != "" ):
            l = wos_library(options.data_path)
            if (options.network_type == "bc"):
                graph = l.bibliographicCoupling(options.overlap_threshold)
            elif (options.network_type == "dc"):
                graph = l.citationNetwork()
            elif (options.network_type == "ap"):
                graph = l.authorPapers()
            elif (options.network_type == "ca"):
                graph = l.coauthors()
            else:
                print "No network type specified. Use --network-type option."

            if (options.format == "sif"):
                l.to_sif(graph, options.output_path + options.identifier)
            elif (options.format == "xgmml"):
                l.to_xgmml(graph, identifier, options.output_path + options.identifier)
            elif (options.format == "gexf"):
                l.to_gexf(graph, options.output_path + options.identifier)
            elif (options.format == "graphml"):
                l.to_graphml(graph, options.output_path + options.identifier)
            else:
                print "No output format specified. Use --network-format."
        else:
            print "No output directory specified. Use --output-path."
    else:
        print "No data file specified. Use --data-path."

if __name__ == '__main__':
    status = main()
    sys.exit(status)
