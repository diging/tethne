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

    docpath = target + '_docs.txt'
    metapath = target + '_meta.csv'

    try:
        docFile = open(docpath, 'wb')
    except IOError:
        raise IOError('Invalid target. Could not open files for writing.')
    
    if metadata is not None:
        metakeys, metadict = metadata
        metaFile = open(metapath, 'wb')
        metaFile.write('{0}\n'.format('\t'.join(['id'] + metakeys)))
    
    # MALLET expects strings; if `vocab` is provided, assumes that ngrams
    #   in `ngrams` are keys into `vocab`.
    if vocab is None:
        def word(s):
            return s    # unidecode(unicode(s))
    else:
        def word(s):
            return vocab[s] # unidecode(unicode(vocab[s]))
    
    try:
        for p,grams in ngrams.iteritems():
            # Write documents.
            m = [ p, 'en' ] # Add doc name and language before data.
            dat = [ word(gram) for gram,freq in grams for i in xrange(freq) ]
            docFile.write(' '.join( m + dat) + '\n')
            
            # Write metadata.
            meta = [ str(p) ]
            if metadata is not None:
                if p in metadict:
                    for f in metakeys:
                        if f in metadict[p]:    meta.append(str(metadict[p][f]))
                        else:                   meta.append('')

                metaFile.write('\t'.join(meta) + '\n')

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
    D : :class:`.Corpus`
        Contains :class:`.Paper` objects generated from the same DfR dataset
        as t_ngrams, indexed by doi and sliced by date.
    feature : str
        (default: 'unigrams') Features in :class:`.Corpus` to use for
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
        metaFile.write('\t'.join(['id'] + fields ) + '\n')
    
        with open(target + '-mult.dat', 'wb') as multFile:
            for year in D.axes['date'].keys():
                papers = D.axes['date'][year]
                
                seq[year] = []
                for id in papers:
                    try:
                        grams = features[id]
                        seq[year].append(id)
                        wordcount = len(grams)  # Number of unique words.
                        
                        # Write data.
                        mdat = [ '{0}:{1}'.format(g,c) for g,c in grams ]
                        mdat_string = ' '.join([ str(wordcount) ] + mdat) + '\n'
                        multFile.write(mdat_string)
                        
                        # Write metadata.
                        meta = [ str(id) ]
                        if papers:
                            p = D.papers[id]
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
    