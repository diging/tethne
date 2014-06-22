# Profiling.
from pycallgraph import PyCallGraph
from pycallgraph.output import GraphvizOutput

profile = False
datapath = './tests/data'
picklepath = './tests/data/pickles'
cg_path = './tests/callgraphs/'

temppath = './tests/sandbox/temp'
outpath = './tests/sandbox/out'
mallet_path = '/Applications/mallet-2.0.7'
dtm_path = '/Users/erickpeirson/tethne/tethne/model/bin/main'

import sys
sys.path.append('/Users/erickpeirson/tethne')

class Profile(object):

    def __init__(self, pcgpath):
        if profile:
            self.p = PyCallGraph(output=GraphvizOutput(output_file=pcgpath))
    
    def __enter__(self):
        if profile:
            self.p.start()

    def __exit__(self, *args):
        if profile:
            self.p.done()
            del self.p