import sys
from optparse import OptionParser
import pickle
import datetime
import pprint

sys.path.append('/Users/erickpeirson/Dropbox/DigitalHPS/Scripts/Tethne/')
from tethne import wos_object
from tethne import triple
from tethne import wos_library


# ---------------------------------- SANDBOX --------------------------------- #

parser = OptionParser()
parser.add_option("-d", "--data-path", dest="data_path")                        # String: Path to WoS data file
parser.add_option("-n", "--network-type", dest="network_type")                  # String: Type of network: 'bc' or 'dc'
parser.add_option("-t", "--overlap-threshold", dest="overlap_threshold", type="int")        # Int: Overlap threshold for bibliographic coupling
parser.add_option("-o", "--output-path", dest="output_path")                    # String: Path to output directory
parser.add_option("-i", "--identifier", dest="identifier")

(options, args) = parser.parse_args()

if (options.data_path != ""):
    if (options.output_path != "" ):
        # Initialize WoS Library
        library = wos_library(options.identifier, options.data_path)
        library.buildLibrary()
        library.dump(options.output_path + "cache.pickle")          # !! Need to go back and make sure a following slash is present
        
        if (options.output_path[-1] != "/"):
            options.output_path += "/"
        
        if (options.network_type == 'bc'):
            print "Generating bibliographic coupling network, with overlap threshold of " + str(options.overlap_threshold) + "."
            library.compareAbsolute(options.overlap_threshold,options.output_path, 1940, 1950)
            print "Bibliographic coupling network and attributes saved to " + options.output_path
        elif (options.network_type == 'dc'):
            print "Generating direct-citation network..."
            library.citationNetwork()
            library.internalNetwork({'startPY':0, 'endPY':2012})                        # This should be an option at some point
            library.generateSIF(options.output_path + "dc_internal.sif", "internal")    #"/Users/erickpeirson/Desktop/bibliographic_output/je/output_internal_0-2012.sif"
            library.generateSIFNodes(options.output_path + "dc_internal-pub_year.noa")
            print "Direct-citation network saved to " + options.output_path
        elif (options.network_type == 'csv'):
            library.export(options.output_path + "/out.csv", "csv", "\t") ## needs to take user path
            print "Library exported to ./out.csv"
        elif (options.network_type == 'authors_per_publication'):
            library.export(options.output_path + "records.csv", "csv", "\t")
            library.authors_per_publication(options.output_path + "data.csv",1900,2013,1)
        else:
            print "No network type specified. Use --network-type option."
    else:
        print "No output directory specified. Use --output-path option."
else:
    print "No data file specified. Use --data-path option."