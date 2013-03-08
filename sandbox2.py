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

identifier = "eco01"
#data_path = "/Users/erickpeirson/Dropbox/collins_project/ecology/ecology_complete.txt"
data_path = "/Users/erickpeirson/Dropbox/DigitalHPS/Student Researcher/Eric Davidson/WoS-combined.txt"
out_file = "Davidson-CoAuthors.xgmml"
threshold = 1

library = wos_library(identifier, data_path)
library.buildLibrary()
library.coauthors()



