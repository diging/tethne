"""
Reader for output from LDA modeling with MALLET.


"""
import csv
import numpy as np
from tethne.data import LDAModel


def read(top_doc, word_top, topic_keys, Z, metadata=None, metadata_key='doi'):
    """
    Parse results from LDA modeling with MALLET.
    
    MALLET's LDA topic modeling algorithm produces a collection of output files.
    :func:`.read` takes the topic-document and (sparse) word-topic matrices, as
    tab-separated value files, along with a metadata file that maps
    each MALLET document id to a :class:`.Paper`\, using the `metadata_key`.
    
    Parameters
    ----------
    top_doc : string
        Path to topic-document datafile generated with --output-doc-topics.
    word_top : string
        Path to word-topic datafile generated with --word-topic-counts-file.
    topic_keys : string
        Path to topic-keys datafile generated with --output-topic-keys.
    Z : int
        Number of topics.
    metadata : string (optional)
        Path to tab-separated metadata file with IDs and :class:`.Paper` keys.
        
    Returns
    -------
    ldamodel : :class:`.LDAModel`
        
    """
    
    td = _handle_top_doc(top_doc, Z)
    wt = _handle_word_top(word_top, Z)
    tk = _handle_topic_keys(topic_keys, Z)
    
    if metadata is not None:
        md = _handle_metadata(metadata)
    else:
        md = None

    ldamodel = LDAModel(dt, wt, tk, md)
    
    return document_topic, topic_word, metadata

def _handle_top_doc(path, Z):
    documents = {}

    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [ line for line in reader ][1:] # Discard header row.
        for line in lines:
            t = line[2:]
            tops = []
            for i in xrange(0,len(t)-1,2):
                tops.append( (int(t[i]), float(t[i+1])) )
                topics.add(int(t[i]))
            documents[int(line[0])] = (line[1], tops)
    
    dt = np.zeros( (len(documents), Z) )
            
    for d, value in documents.iteritems():
        for t,p in value[1]:
            dt[d,t] = p

    return dt

def _handle_word_top(path, Z):
    topics = set()
    
    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter=' ')
        for line in reader:
            tc = { int(tuple(l.split(':'))[0]):float(tuple(l.split(':'))[1]) for l in line[2:] }
            words[int(line[0])] = ( line[1], tc )

    wt = np.zeros((Z, len(words)))

    for w, values in words.iteritems():
        for t,p in values[1].iteritems():
            wt[t,w] = p
    
    # Normalize
    for t in xrange(Z):
        wt[t,:] /= np.sum(wt[t,:])
    
    retun wt
        
def _handle_topic_keys(path):

    return tk
    
def _handle_metadata(path):

    return md