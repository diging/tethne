"""
Plain text corpus reader.
"""

import nltk

from tethne import Paper, Corpus, StructuredFeature, StructuredFeatureSet, Feature, FeatureSet


def read(path, pattern='.+\.txt', extractor=lambda fid: {}, index_by='fileid',
         structured=True, corpus=True, **kwargs):
    """
    Generate a :class:`.Corpus` from a collection of plain-text files.

    Plain-text content will be available as a feature set called "plain_text".

    Uses :class:`nltk.corpus.reader.plaintext.PlaintextCorpusReader`\.

    Parameters
    ----------
    path : str
        Path to a directory containing plain text files.
    pattern : str
        (default: '.+\.txt') A RegEx pattern used to select texts for inclusion
        in the corpus. By default will select any file ending in `.txt`.
    extractor : function
        This function can be used to parse the name of each file for additional
        metadata. It should accept a single string (the filename), and return
        a dictionary of fields and values. These fields will be added to the
        resulting :class:`.Paper` instance.
    index_by : str
        (default: 'fileied') Field on :class:`.Paper` to use as the primary
        index.
    structured : bool
        (default: True) If True, the contents of the document collection will be
        represented by a :class:`.StructuredFeatureSet`\. If False, a
        :class:`.FeatureSet` will be used instead. Setting ``structured=False``
        is appropriate if word-order does not matter (e.g. topic modeling).
    corpus : bool
        (default: True) If False, will return a list of :class:`.Paper`
        instances rather than a :class:`.Corpus`\.
    kwargs : kwargs
        Any additional kwargs will be passed to the
        :class:`nltk.corpus.reader.plaintext.PlaintextCorpusReader` constructor.
        Refer to the `NLTK documentation
        <http://www.nltk.org/api/nltk.corpus.reader.html#nltk.corpus.reader.plaintext.PlaintextCorpusReader>`_
        for details.

    Returns
    -------
    :class:`.Corpus`

    """

    if structured:
        featureset_class = StructuredFeatureSet
        feature_class = StructuredFeature
    else:
        featureset_class = FeatureSet
        feature_class = Feature

    documents = nltk.corpus.PlaintextCorpusReader(path, pattern, **kwargs)

    papers = []
    features = {}
    for fileid in documents.fileids():
        paper = Paper()
        for key, value in extractor(fileid).iteritems():
            setattr(paper, key, value)
        paper.fileid = fileid
        papers.append(paper)

        # PlaintextCorpusReader doesn't read from disk until we iterate over
        #  its words.
        feature = feature_class([w for w in documents.words(fileids=[fileid])])
        features[getattr(paper, index_by)] = feature

    featureset = featureset_class(features)
    if corpus:
        corpus = Corpus(papers, index_by=index_by)
        corpus.features['plain_text'] = featureset
        return corpus
    return papers, featureset
