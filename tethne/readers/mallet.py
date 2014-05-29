# TODO: retire this.

"""
Reader for output from topic modeling with MALLET.
"""

import sys
sys.path.append('/Users/erickpeirson/tethne')

import csv
import numpy as np
from ..classes import Paper
from tethne.model import LDAModel
from tethne.utilities import Dictionary

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

