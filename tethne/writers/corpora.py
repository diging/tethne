"""
"""

from collections import Counter

def to_documents(target, ngrams, metadata=None, vocab=None):
    """
    
    Parameters
    ----------
    target : str
        Target path for documents; e.g. './mycorpus' will result in 
        './mycorpus_docs.txt' and './mycorpus_meta.csv'.
    ngrams : dict
        Keys are paper identifiers, values are lists of (ngram, frequency)
        tuples. If `vocab` is provided, assumes that `ngram` is an index into
        `vocab`.
    metadata : tuple
        (`keys`, dict): `keys` is a list of metadata keys, and dict contains
        metadata values dict for each paper. ( [ str ], { str(p) : dict } ) 
    
    Raises
    ------
    IOError
    """

    try:
        docFile = open(docpath, 'wb')
    except IOError:
        raise IOError('Invalid target. Could not open files for writing.')
    
    if metadata is not None:
        metakeys, metadict = metadata
        metaFile = open(metapath, 'wb')
        metaFile.write('# {0}\n'.format('\t'.join(metakeys)))
    
    # MALLET expects strings; if `vocab` is provided, assumes that ngrams
    #   in `ngrams` are keys into `vocab`.
    if vocab is None:
        def word(s):
            return s    # unidecode(unicode(s))
    else:
        def word(s):
            return vocab[s] # unidecode(unicode(vocab[s]))
    
    d = 0   # Document index in _docs.txt file.
    try:
        for p,grams in ngrams.iteritems():
            docFile.write(' '.join([ word(gram) for gram,freq in grams 
                                                for i in xrange(freq) ]) + '\n')

            meta = [ str(d), str(p) ]
            if metadata is not None:
                meta += [ str(metadict[p][f]) for f in metakeys ]
                metaFile.write('\t'.join(meta) + '\n')
            d += 1
    except AttributeError:  # .iteritems() raises an AttributeError if ngrams
                            #  is not dict-like.
        raise ValueError('Parameter \'ngrams\' must be a dict.')
    
    docFile.close()
    
    if metadata is not None:
        metaFile.close()
    
    return docpath, metapath

def to_dtm_input(target, D, feature='unigrams', fields=['date','atitle']):
    """
    
    Parameters
    ----------
    target : str
        Target path for documents; e.g. './mycorpus' will result in 
        './mycorpus-mult.dat', './mycorpus-seq.dat', 'mycorpus-vocab.dat', and
        './mycorpus-meta.dat'.    
    D : :class:`.DataCollection`
        Contains :class:`.Paper` objects generated from the same DfR dataset
        as t_ngrams, indexed by doi and sliced by date.
    feature : str
        (default: 'unigrams') Features in :class:`.DataCollection` to use for
        modeling.
    fields : list
        (optional) Fields in :class:`.Paper` to include in the metadata file.
        
    Returns
    -------
    None : If all goes well.
    
    Raises
    ------
    IOError
    """

    try:
        metaFile = open(target + '-meta.dat', 'wb')
    except IOError:
        raise IOError('Invalid target. Could not open files for writing.')

    vocab = D.features[feature]['index']
    features = D.features[feature]['features']

    seq = {}
    # Generate -mult.dat file (wordcounts for each document).
    #   From the DTM example:
    #
    #     one-doc-per-line, each line of the form
    #         unique_word_count index1:count1 index2:count2 ... indexn:counnt
    #     The docs in foo-mult.dat should be ordered by date, with the first
    #     docs from time1, the next from time2, ..., and the last docs from
    #     timen.
    #
    # And -meta.dat file (with DOIs).
    #
    #       a file with information on each of the documents, arranged in
    #           the same order as the docs in the mult file.
    #
    with open(target + '-meta.dat', 'wb') as metaFile:
        with open(target + '-mult.dat', 'wb') as multFile:
            for year in D.axes['date'].keys():
                papers = D.axes['date'][year]
                
                seq[year] = []
                for doi in papers:  # D must be indexed by doi.
                    try:
                        grams = features[doi]
                        seq[year].append(doi)
                        wordcount = len(grams)  # Number of unique words.
                        multFile.write(' '.join([ str(wordcount) ] + \
                                                [ '{0}:{1}'.format(g,c)
                                                    for g,c in grams ] + \
                                                ['\n']))
                        meta = [ str(doi) ]
                        if papers:
                            p = D.papers[doi]
                            meta += [ str(p[f]) for f in fields ]
                        metaFile.write('\t'.join(meta) + '\n')
                        
                    except KeyError:    # May not have data for each Paper.
                        pass

    # Generate -seq.dat file (number of papers per year).
    #   From the DTM example:
    #
    #       Number_Timestamps
    #       number_docs_time_1
    #       ...
    #       number_docs_time_i
    #       ...
    #       number_docs_time_NumberTimestamps
    #
    with open(target + '-seq.dat', 'wb') as seqFile:
        seqFile.write(str(len(seq)) + '\n')
        for year, papers in sorted(seq.items()):
            seqFile.write('{0}\n'.format(len(papers)))

    #       a file with all of the words in the vocabulary, arranged in
    #       the same order as the word indices
    with open(target + '-vocab.dat', 'wb') as vocabFile:
        for index,word in sorted(vocab.items()):
            vocabFile.write('{0}\n'.format(word))

    return None

if __name__ == '__main__':
    import sys
    sys.path.append("/Users/erickpeirson/Dropbox/DigitalHPS/Scripts/tethne")

    datapath = "/Users/erickpeirson/Genecology Project Archive/JStor DfR Datasets/2013.5.3.cHrmED8A/"
    datapath2 = "/Users/erickpeirson/Genecology Project Archive/JStor DfR Datasets/2013.5.3.k2HUvXh9/"
    datapath3 = "/Users/erickpeirson/Genecology Project Archive/JStor DfR Datasets/2013.5.3.W8mEeULy/"

    import tethne.readers as rd
    from tethne.data import DataCollection
    papers = rd.dfr.read(datapath) + rd.dfr.read(datapath2) + rd.dfr.read(datapath3)

    D = DataCollection(papers, 'doi')
    D.slice('date', 'time_period', window_size=8)
    
    ngrams = rd.dfr.ngrams(datapath, 'uni', apply_stoplist=True)
    print len(ngrams)
    ngrams.update(rd.dfr.ngrams(datapath2, 'uni', apply_stoplist=True))
    print len(ngrams)
    ngrams.update(rd.dfr.ngrams(datapath3, 'uni', apply_stoplist=True))
    print len(ngrams)
    t_ngrams, vocab, counts = rd.dfr.tokenize(ngrams)
    
    to_dtm_input("/Users/erickpeirson/Desktop/dtm_test", D, t_ngrams, vocab)
    