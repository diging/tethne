"""
Reader for output from topic modeling with MALLET.
"""

import sys
sys.path.append('/Users/erickpeirson/Dropbox/DigitalHPS/Scripts/tethne')

import csv
import numpy as np
from tethne.data import LDAModel, Paper
from tethne.utilities import Dictionary


def load(top_doc, word_top, topic_keys, Z, metadata=None, metadata_key='doi'):
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
    wt,vocabulary = _handle_word_top(word_top, Z)
    tk = _handle_topic_keys(topic_keys)

    if metadata is not None:
        md = _handle_metadata(metadata)
    else:
        md = None

    ldamodel = LDAModel(td, wt, tk, md, vocabulary)

    return ldamodel

def read(top_doc, word_top, topic_keys, Z, metadata=None, metadata_key='doi'):
    """
    Generates :class:`.Paper` objects from Mallet output.

    Each :class:`.Paper` is assigned a topic vector.

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
    papers : list
        List of :class:`.Paper`
    """

    ldamodel = load(top_doc, word_top, topic_keys, Z, metadata, metadata_key)
    D = ldamodel.doc_topic.shape[0]

    papers = []

    for d in xrange(D):
        p = Paper()
        p[metadata_key] = ldamodel.metadata[d]  # e.g. doi, wosid
        p['topics'] = (ldamodel.doc_topic[d,:], ldamodel.top_keys)
        papers.append(p)

    return papers

def _handle_top_doc(path, Z):
    """
    Returns
    -------
    td : Numpy array
        Rows are documents, columns are topics. Rows sum to ~1.
    """
    documents = {}

    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [ line for line in reader ][1:] # Discard header row.
        for line in lines:
            t = line[2:]
            tops = []
            for i in xrange(0,len(t)-1,2):
                tops.append( (int(t[i]), float(t[i+1])) )
                #topics.add(int(t[i]))
            documents[int(line[0])] = (line[1], tops)

    td = np.zeros( (len(documents), Z) )

    for d, value in documents.iteritems():
        for t,p in value[1]:
            td[d,t] = p

    return td

def _handle_word_top(path, Z):
    """
    Returns
    -------
    wt : Numpy array
        Rows are topics, columns are words. Rows sum to ~1.
    vocabulary : :class:`.Dictionary`
        Maps words to word-indices in wt.
    """
    words = {}
    topics = set()

    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter=' ')
        for line in reader:
            tc = { int(tuple(l.split(':'))[0]):float(tuple(l.split(':'))[1]) \
                    for l in line[2:] }
            words[int(line[0])] = ( line[1], tc )

    wt = np.zeros((Z, len(words)))

    for w, values in words.iteritems():
        for t,p in values[1].iteritems():
            wt[t,w] = p

    # Normalize
    for t in xrange(Z):
        wt[t,:] /= np.sum(wt[t,:])

    # Build vocabulary
    vocabulary = Dictionary()
    for k,v in words.iteritems():
        vocabulary[k] = v[0]

    return wt, vocabulary

def _handle_topic_keys(path):
    """
    Returns
    -------
    tk : dict
        Keys are topic indices, values are (P, terms) tuples, where terms is a
        list of strings and P is float.
    """
    tk = {}

    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter='\t')
        for l in reader:
            tk[int(l[0])] = (float(l[1]), l[2].split())

    return tk

def _handle_metadata(path):
    """
    Returns
    -------
    md : dict
        Keys are document indices, values are identifiers from a :class:`.Paper`
        property.
    """
    md = {}

    with open(path, "rU") as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [ l for l in reader ][1:]
        for l in lines:
            md[int(l[0])] = l[1]

    return md
