"""
"""

from collections import Counter
from itertools import repeat
import codecs
import os
import csv

from tethne import FeatureSet, StructuredFeatureSet

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


def write_documents(corpus, target, featureset_name, metadata_fields=[]):
    """
    Parameters
    ----------


    """

    docpath = target + '_docs.txt'
    metapath = target + '_meta.csv'

    features = corpus.features[featureset_name].features
    ftype = type(corpus.features[featureset_name])
    index = corpus.features[featureset_name].index

    try:
        docFile = open(docpath, 'wb')
    except IOError:
        raise IOError('Invalid target. Could not open files for writing.')

    # Generate metadata.
    with codecs.open(metapath, 'w', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([corpus.index_by] + list(metadata_fields))
        for i, p in corpus.indexed_papers.iteritems():
            getter = lambda m: getattr(p, m) if hasattr(p, m) else None
            writer.writerow([i] + list(map(getter, metadata_fields)))

    # Write documents content.
    with codecs.open(docpath, 'w', encoding='utf-8') as f:
        for i, p in corpus.indexed_papers.iteritems():
            if i in features:
                row = [i, u'en']
                if ftype is FeatureSet:
                    row += [u' '.join(repeat(e, c)) for e, c in features[i]]
                elif ftype is StructuredFeatureSet:
                    row += features[i]
                f.write(u'\t'.join(row) + u'\n')

    return docpath, metapath


def write_documents_dtm(corpus, target, featureset_name, slice_kwargs={},
                        metadata_fields=['date','title']):
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

    metapath = target + '-meta.dat'
    multpath = target + '-mult.dat'
    seqpath = target + '-seq.dat'
    vpath = target + '-vocab.dat'

    lookup = corpus.features[featureset_name].lookup
    index = corpus.features[featureset_name].index
    features = corpus.features[featureset_name].features

    # Generate -mult.dat file (wordcounts for each document).
    #   From the DTM example:
    #
    #     one-doc-per-line, each line of the form
    #         unique_word_count index1:count1 index2:count2 ... indexn:counnt
    #     The docs in foo-mult.dat should be ordered by date, with the first
    #     docs from time1, the next from time2, ..., and the last docs from
    #     timen.
    #
    N = Counter()
    for date, subcorpus in corpus.slice(**slice_kwargs):
        with codecs.open(multpath, 'w', encoding='utf-8') as f:
            for p in subcorpus.papers:
                i = getattr(p, subcorpus.index_by)
                N[date] += 1
                docLine = [u':'.join([unicode(lookup[e]), unicode(c)])
                           for e,c in features[i]]
                unique = unicode(len(features[i]))
                f.write(u' '.join([unique] + docLine) + '\n')

    # And -meta.dat file (with DOIs).
    #
    #       a file with information on each of the documents, arranged in
    #           the same order as the docs in the mult file.
    #
    with codecs.open(metapath, 'w', encoding='utf-8') as f:
        writer = csv.writer(f, delimiter='\t')
        writer.writerow(['id'] + list(metadata_fields))
        for date, subcorpus in corpus.slice(**slice_kwargs):
            for p in subcorpus.papers:
                getter = lambda m: getattr(p, m) if hasattr(p, m) else None
                fieldData = map(getter, metadata_fields)
                writer.writerow([getattr(p, corpus.index_by)] + list(fieldData))

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
    with open(seqpath, 'w') as f:
        for date in sorted(N.keys()):
            f.write(u'{date}\n'.format(date=N[date]))

    #       a file with all of the words in the vocabulary, arranged in
    #       the same order as the word indices
    with codecs.open(vpath, 'w', encoding='utf-8') as f:
        f.write(u'\n'.join([index[i] for i in sorted(index.keys())]))
