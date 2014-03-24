"""
"""

def to_documents(target, ngrams):
    """
    
    Parameters
    ----------
    target : str
        Target path for documents; e.g. './mycorpus' will result in 
        './mycorpus_docs.txt' and './mycorpus_meta.csv'.
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.
    
    Returns
    -------
    None : If all goes well.
    
    Raises
    ------
    ValueError
    """
    
    try:
        docFile = open(target + '_docs.txt', 'wb')
        metaFile = open(target + '_meta.csv', 'wb')
    except IOError:
        raise ValueError('Invalid target. Could not open files for writing.')
    
    metaFile.write('# doc\tdoi\n')
    
    d = 0   # Document index in _docs.txt file.
    try:
        for key,values in ngrams.iteritems():
            docFile.write(' '.join([ gram for gram,freq in values 
                                                for i in xrange(freq) ]) + '\n')
            metaFile.write('{0}\t{1}\n'.format(d, key))
            d += 1
    except AttributeError:  # .iteritems() raises an AttributeError if ngrams
                            #  is not dict-like.
        raise ValueError('Parameter \'ngrams\' must be dictionary-like.')
    
    docFile.close()
    metaFile.close()
    
    return