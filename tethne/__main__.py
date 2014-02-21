if __name__ == "__main__":
    
    import sys
    import os
    import time
    import math
    from optparse import OptionParser, OptionGroup
    
    import tethne.readers as rd
    
    parser = OptionParser()
    
    workflowGroup = OptionGroup(parser, "Workflow Steps",
                            "Choose one workflow step per script execution."+ \
                            " Each workflow step requires a different set of"+ \
                            " additional options.")

    workflowGroup.add_option("--read-file",
                             action="store_true", dest="read_f", default=False,
                             help="Read from a single data file.")
    workflowGroup.add_option("--read-dir",
                             action="store_true", dest="read_d", default=False,
                             help="Read from a directory containing multiple "+\
                                  "data files.")
    workflowGroup.add_option("--slice",
                             action="store_true", dest="slice", default=False,
                             help="Slice your dataset for comparison along a "+\
                                  "key axis.")
    workflowGroup.add_option("--graph",
                             action="store_true", dest="graph", default=False,
                            help="Generate a graph (or collection of graphs).")
                
    
    parser.add_option("-P", "--data-path", dest="datapath",
                      help="Full path to dataset.")
                      
    parser.add_option("-F", "--format", dest="format",
                      help="Format of input dataset (WOS, DFR).")
                      
    parser.add_option("-S", "--slice-axis", dest="slice_axis",
                      help="Key along which to slice the dataset. This can be"+\
                           " one of any of the fields listed in the API " + \
                           " documentation: " + \
                           "./doc/api/tethne.html#tethne.data.Paper .")
    parser.add_option("-N", "--node-type", dest="node_type",
                      help="Must be one of: author, paper, term.")
    parser.add_option("-T", "--graph-type", dest="graph_type",
                      help="Name of a network-builing method. Can be one of " +\
                           "any of the methods listed in the API " + \
                           "documentation: " + \
                           "./doc/api/tethne.networks.html#module-tethne."+\
                           "networks. e.g. if '-n' is 'author', '-t' could be"+\
                           " 'coauthors'")    
    
    graphGroup = OptionGroup(parser, "Optional network-building arguments",
                             "Each network-building method takes some"+\
                             " optional arguments to control its output. See"+\
                             " ./doc/api/tethne.networks.html for "+\
                             " a complete description of each method and"+\
                             " available arguments. If the selected method"+\
                             " does not accept an argument from the list"+\
                             " below, it will be ignored.")
    graphGroup.add_option("--threshold", dest="threshold",
                          help="Set the 'threshold' argument.")
    graphGroup.add_option("--topn", dest="topn",
                          help="Set the 'topn' argument.")
    graphGroup.add_option("--node-attr", dest="node_attr",
                          help="List of attributes to include for each node." +\
                               " e.g. --node-attr=date,atitle,jtitle")
    graphGroup.add_option("--edge-attr", dest="edge_attr",
                          help="List of attributes to include for each edge." +\
                               " e.g. --edge-attr=ayjid,atitle,date")
    graphGroup.add_option("--node-id", dest="node_id",
                          help="Field to use as node id (for papers graphs)." +\
                               " e.g. --node-id=ayjid")
    graphGroup.add_option("--weighted", dest="weighted", action="store_true",
                          default=False,
                          help="Trigger the 'weighted' argument.")
    
                                                
    parser.add_option_group(workflowGroup)
    parser.add_option_group(graphGroup)
    
    (options, args) = parser.parse_args()
    
    # Read data from file or directory.
    if options.read_f or options.read_d:
    
        # Must specify path.
        if options.datapath is None:    
            sys.exit('Specify path to data with --data-path')
            
        # Must specify format.
        if options.format is None:      
            sys.exit('Specify data format with --format argument.')
        
        # Must select a supported format.
        if options.format not in ['WOS', 'DFR']:
            sys.exit('Data format must be one of: WOS, DFR.')
        
        sys.stdout.write("Reading {0} data from file {1}..."
                                      .format(options.format, options.datapath))

        start_time = time.time()

        if options.format == 'WOS':
            if options.read_f:
                papers = rd.wos.read(options.datapath)
            if options.read_d:
                papers = rd.wos.from_dir(options.datapath)
        elif options.format == 'DFR':
            if options.read_f:
                papers = rd.dfr.read(options.datapath)
            if options.read_d:
                papers = rd.dfr.from_dir(options.datapath)

        N = len(papers)
        a = papers[0]['accession']

        t = time.time() - start_time

        sys.stdout.write("Done.\n")
        sys.stdout.write("Read {0} papers in {1} seconds. Accession: {2}.\n"
                                                               .format(N, t, a))

            
        
        