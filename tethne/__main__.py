if __name__ == "__main__":
    
    import csv
    import sys
    import os
    import time
    import math
    import pickle
    from optparse import OptionParser, OptionGroup
    
    import tethne.readers as rd
    import tethne.networks as nt
    from tethne.data import DataCollection, GraphCollection
    from tethne.builders import authorCollectionBuilder, paperCollectionBuilder
    
    parser = OptionParser()

    # Only one of the following workflow steps will be carried out per 
    #  script execution.
    workflowGroup = OptionGroup(parser, "Workflow Steps",
                            "Choose one workflow step per script execution."+ \
                            " Each workflow step requires a different set of"+ \
                            " additional options.")

    workflowGroup.add_option("--read-file",
                             action="store_true", dest="read_f", default=False,
                             help="Read from a single data file. Requires" +\
                                  " --data-path and --data-format.")
    workflowGroup.add_option("--read-dir",
                             action="store_true", dest="read_d", default=False,
                             help="Read from a directory containing multiple"+\
                                  " data files. Requires --data-path and" +\
                                  " --data-format.")
    workflowGroup.add_option("--slice",
                             action="store_true", dest="slice", default=False,
                             help="Slice your dataset for comparison along a" +\
                                  " key axis. Requires --slice-axis. If" +\
                                  " --outpath is set, produces a table with" +\
                                  " binned paper frequencies in [OUTPATH]/" +\
                                  "[DATASET_ID]_slices.csv.")
    workflowGroup.add_option("--graph",
                             action="store_true", dest="graph", default=False,
                            help="Generate a graph (or collection of graphs).")
    
    parser.add_option("-I", "--dataset-id", dest="dataset_id",
                      help="Unique ID (required).")
    parser.add_option("-t", "--temp-dir", dest="temp_dir", default="/tmp",
                      help="Directory for storing temporary files.")
    parser.add_option("-O", "--outpath", dest="outpath",
                      help="Path to save workflow output. Some workflow steps"+\
                           " will generate summary statistics or other output.")

    # Options for read workflow step.
    readGroup = OptionGroup(parser, "Options for read workflow step")
    
    readGroup.add_option("-P", "--data-path", dest="datapath",
                      help="Full path to dataset.")
                      
    readGroup.add_option("-F", "--data-format", dest="dataformat",
                      help="Format of input dataset (WOS, DFR).")

    # Options for slice workflow step.
    sliceGroup = OptionGroup(parser, "Options for slice workflow step")
    
    sliceGroup.add_option("-S", "--slice-axis", dest="slice_axis",
                      help="Key along which to slice the dataset. This can be"+\
                           " one of any of the fields listed in the API " + \
                           " documentation: " + \
                           "./doc/api/tethne.html#tethne.data.Paper .")
                           
    sliceGroup.add_option("-M", "--slice-method", dest="slice_method",
               default="time_period",
               help="Method used to slice DataCollection. Available methods:" +\
                    " time_window, time_period, cumulative. For details, see" +\
                    " ./doc/api/tethne.html#tethne.data.DataCollection.slice."+\
                    " Default is time_period.")
                    
    sliceGroup.add_option("--slice-window-size", dest="window_size", default=1,
                        help="Size of slice time-window or period, in years." +\
                             " Default is 1.")
                             
    sliceGroup.add_option("--slice-step-size", dest="step_size",
                          help="Amount to advance time-window in each step" +\
                               " (ignored for time-period).")

    # Required arguments for network-building.
    graphReqGroup = OptionGroup(parser, "Required options for graph workflow" +\
                                        " step.")
                                    
    graphReqGroup.add_option("-N", "--node-type", dest="node_type",
                      help="Must be one of: author, paper, term.")
                      
    graphReqGroup.add_option("-T", "--graph-type", dest="graph_type",
                      help="Name of a network-builing method. Can be one of " +\
                           "any of the methods listed in the API " + \
                           "documentation: " + \
                           "./doc/api/tethne.networks.html#module-tethne."+\
                           "networks. e.g. if '-n' is 'author', '-t' could be"+\
                           " 'coauthors'")

    # Optional arguments for network-building, for setting keyword arguments of
    #  methods in tethne.networks.
    graphGroup = OptionGroup(parser, "Optional network-building arguments",
                             "Each network-building method takes some"+\
                             " optional arguments to control its output. See"+\
                             " ./doc/api/tethne.networks.html for "+\
                             " a complete description of each method and"+\
                             " available arguments. If the selected method"+\
                             " does not accept an argument from the list"+\
                             " below, it will be ignored.")

    graphGroup.add_option("--merged",
                          action="store_true", dest="merged", default=False,
                          help="Ignore DataCollection slicing, and build" +\
                               " a single graph from all Papers.")
                             
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
    parser.add_option_group(readGroup)
    parser.add_option_group(sliceGroup)
    parser.add_option_group(graphReqGroup)
    parser.add_option_group(graphGroup)
    
    (options, args) = parser.parse_args()
    
    
    if options.dataset_id is None:
        sys.exit('Must specify --dataset-id')
    
    #############################
    #   Workflow step: Read     #
    #############################
    if options.read_f or options.read_d:
    
        # Must specify path.
        if options.datapath is None:    
            sys.exit('Specify path to data with --data-path')
            
        # Must specify format.
        if options.dataformat is None:      
            sys.exit('Specify data format with --format argument.')
        
        # Must select a supported format.
        if options.dataformat not in ['WOS', 'DFR']:
            sys.exit('Data format must be one of: WOS, DFR.')
        
        sys.stdout.write("Reading {0} data from file {1}..."
                                  .format(options.dataformat, options.datapath))

        start_time = time.time()

        if options.dataformat == 'WOS':
            if options.read_f:
                papers = rd.wos.read(options.datapath)
            if options.read_d:
                papers = rd.wos.from_dir(options.datapath)
        elif options.dataformat == 'DFR':
            if options.read_f:
                papers = rd.dfr.read(options.datapath)
            if options.read_d:
                papers = rd.dfr.from_dir(options.datapath)

        N = len(papers)
        a = papers[0]['accession']

        t = time.time() - start_time

        sys.stdout.write("done.\n")
        sys.stdout.write("Read {0} papers in {1} seconds. Accession: {2}.\n"
                                                               .format(N, t, a))

        sys.stdout.write("Generating a new DataCollection...")
        if options.dataformat == 'WOS':
            index_by = 'wosid'
        elif options.dataformat == 'DFR':
            index_by = 'doi'
        D = DataCollection(papers, index_by=index_by)
        sys.stdout.write("done.\n")

        # Save DataCollection for next workflow step.
        savepath = options.temp_dir + "/" + \
                   options.dataset_id + "_DataCollection.pickle"
        sys.stdout.write("Saving DataCollection to {0}...".format(savepath))
        pickle.dump(D, open(savepath, 'wb'))
        sys.stdout.write("done.\n")
        
    #############################
    #   Workflow step: Slice    #
    #############################
    elif options.slice:
    
        # Must specify a slice axis.
        if options.slice_axis is None:
            sys.exit('Must specifify a slice axis with --slice-axis.')
        
        # Load DataCollection.
        loadpath = options.temp_dir + "/" + \
                   options.dataset_id + "_DataCollection.pickle"
        sys.stdout.write("Loading DataCollection from {0}...".format(loadpath))
        D = pickle.load(open(loadpath, 'rb'))
        sys.stdout.write("done.\n")
        
        # Slice DataCollection
        axes = options.slice_axis.split(',')
        for a in axes:
            sys.stdout.write("Slicing DataCollection by {0}...".format(a))
            if a == 'date':
                D.slice(a, method=options.slice_method, 
                           window_size=options.window_size,
                           step_size=options.step_size)
            else:
                D.slice(a)
            sys.stdout.write("done.\n")
        
        # Generate binned data. For now, only uses first two axes.
        if options.outpath is not None:
            summarypath = options.outpath + "/" + \
                          options.dataset_id + "_sliceDistribution.csv"
            sys.stdout.write("Saving slice distribution to {0}..."
                                                           .format(summarypath))
            with open(summarypath, 'wb') as f:
                writer = csv.writer(f, delimiter=',')
                if len(axes) == 2:  # 2-dimensional slice binning.
                    A_indices = D.axes[axes[0]].keys()
                    B_indices = D.axes[axes[1]].keys()
                    writer.writerow([''] + A_indices)
                    dist = D.distribution_2d(axes[0], axes[1])
                    for i in xrange(dist.shape[1]):
                        writer.writerow([B_indices[i]] + list(dist[:,i]))
                elif len(axes) == 1:    # 1-dimensional slice binning.
                    dist = D.distribution()
                    A_indices = D.axes[axes[0]].keys()
                    for i in xrange(dist.shape[0]):
                        writer.writerow([A_indices[i], dist[i]])
            sys.stdout.write("done.\n")
        
        # Save sliced DataCollection for next workflow step.
        savepath = options.temp_dir + "/" + \
                   options.dataset_id + "_DataCollection_sliced.pickle"
        sys.stdout.write("Saving sliced DataCollection to {0}..."
                                                              .format(savepath))
        pickle.dump(D, open(savepath, 'wb'))
        sys.stdout.write("done.\n")
        
    #############################
    #   Workflow step: Graph    #
    #############################
    elif options.graph:
    
        # Must specifiy node type.
        if options.node_type is None:
            sys.exit('Must specify node type with --node-type.')
        
        # Must specify graph type.
        if options.graph_type is None:
            sys.exit('Must specifiy a graph type with --graph-type.')
        
        if options.merged:
            loadpath = options.temp_dir + "/" + \
                       options.dataset_id + "_DataCollection.pickle"
            sys.stdout.write("Loading DataCollection without slices from {0}..."
                                                    .format(loadpath))                       
        else:
            loadpath = options.temp_dir + "/" + \
                       options.dataset_id + "_DataCollection_sliced.pickle"
            sys.stdout.write("Loading DataCollection from {0}..."
                                                    .format(loadpath))
        
        D = pickle.load(open(loadpath, 'rb'))
        sys.stdout.write("done.\n")

        if not options.merged:
            # Uses the first axis only!
            a = D.get_axes()[0]
            sys.stdout.write("Using first slice in DataCollection: {0}.\n"
                                                                     .format(a))
                                                                 
        # Build kwargs.
        kwargs = {}
        if options.threshold is not None:
            kwargs['threshold'] = options.threshold
        if options.topn is not None:
            kwargs['topn'] = options.topn
        if options.node_attr is not None:
            kwargs['node_attribs'] = options.node_attr.split(',')
        if options.edge_attr is not None:
            kwargs['edge_attribs'] = options.edge_attr.split(',')
        if options.node_id is not None:
            kwargs['node_id'] = options.node_id
        kwargs['weighted'] = options.weighted
        
        # Build the graph(s).
        sys.stdout.write("Building {0} graph using {1} method..."
                                 .format(options.node_type, options.graph_type))

        start_time = time.time()        
        
        if not options.merged:  # Generate GraphCollection from DataCollection.
            if options.node_type == 'paper':
                builder = paperCollectionBuilder(D)
                
            elif options.node_type == 'author':
                builder = authorCollectionBuilder(D)

            C = builder.build(a, options.graph_type, **kwargs)
        else:   # Generate a single Graph from all of the papers in 
                #  DataCollection, D.
            method = nt.__dict__[options.node_type+'s'] \
                       .__dict__[options.graph_type]
            
            G = method(D.papers(), **kwargs)
        
        sys.stdout.write("done in {0} seconds.\n"
                                                .format(time.time()-start_time))
        
        if options.node_type == 'term':
            sys.exit('Term graphs not yet implemented. Coming soon!\n')