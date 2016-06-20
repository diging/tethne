"""
Methods for parsing bibliographic datasets.

.. autosummary::

   merge
   dfr
   wos
   zotero
   scopus

Each module in :mod:`tethne.readers` provides a ``read`` function that yields
a :class:`.Corpus` instance.

"""

from tethne import Paper, Corpus

class DataError(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

# TODO: merge FeatureSets.
def merge(corpus_1, corpus_2, match_by=['ayjid'], match_threshold=1.,
          index_by='ayjid'):
    """
    Combines two :class:`.Corpus` instances.

    The default behavior is to match :class:`.Paper`\s using the fields in
    ``match_by``\. If several fields are specified, ``match_threshold`` can be
    used to control how well two :class:`.Paper`\s must match to be combined.

    Alternatively, ``match_by`` can be a callable object that accepts two
    :class:`.Paper` instances, and returns bool. This allows for more complex
    evaluations.

    Where two matched :class:`.Paper`\s have values for the same field, values
    from the :class:`.Paper` instance in ``corpus_1`` will always be  preferred.

    Parameters
    ----------
    corpus_1 : :class:`.Corpus`
        Values from this :class:`.Corpus` will always be preferred in cases of
        conflict.
    corpus_2 : :class:`.Corpus`
    match_by : list or callable
        Either a list of fields used to evaluate whether or not two
        :class:`.Paper`\s should be combined, **OR** a callable that accepts
        two :class:`.Paper` instances and returns bool.
    match_threshold : float
        if ``match_by`` is a list containing more than one field, specifies the
        proportion of fields that must match for two :class:`.Paper` instances
        to be combined.
    index_by : str
        The field to use as the primary indexing field in the new
        :class:`.Corpus`\. Default is `ayjid`, since this is virtually always
        available.

    Returns
    -------
    combined : :class:`.Corpus`

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers import wos, dfr, merge
       >>> wos_corpus = wos.read("/Path/to/data1.txt")
       >>> dfr_corpus = dfr.read("/Path/to/DfR")
       >>> corpus = merge(wos_corpus, dfr_corpus)

    """

    def norm(value):
        if type(value) in [str, unicode]:
            return value.strip().lower()
        return value


    combined = []
    exclude_1 = []
    exclude_2 = []

    # Attempt to match Papers
    for paper_1 in corpus_1:
        for paper_2 in corpus_2:
            # The user can provide their own matching logic. In this case,
            #  match_threshold is ignored.
            if callable(match_by):
                match = match_by(paper_1, paper_2)

            # Otherwise we match using the fields in ``match_by``.
            else:
                matches = 0.
                for field in match_by:
                    if hasattr(paper_1, field) and hasattr(paper_2, field):
                        value_1 = norm(getattr(paper_1, field))
                        value_2 = norm(getattr(paper_2, field))
                        if value_1 == value_2:
                            matches += 1.
                match = matches/len(match_by) >= match_threshold

            # Not every field needs to match precisely;
            if match:
                paper_new = Paper()
                # We add values from paper_2 first, so that...
                for key, value in paper_2.__dict__.iteritems():
                    if value not in ['', [], None]:
                        paper_new[key] = value

                # ...values from paper_1 will override values from paper_2.
                for key, value in paper_1.__dict__.iteritems():
                    if value not in ['', [], None]:
                        paper_new[key] = value

                # We assemble all papers before creating a new Corpus, so that
                #  indexing happens all in one shot.
                combined.append(paper_new)

                # Flag matched papers for exclusion.
                exclude_1.append(corpus_1._generate_index(paper_1))
                exclude_2.append(corpus_2._generate_index(paper_2))


    # Include papers that were not matched.
    combined += [paper for paper in corpus_1
                 if corpus_1._generate_index(paper) not in exclude_1]
    combined += [paper for paper in corpus_2
                 if corpus_2._generate_index(paper) not in exclude_2]

    # Here indexing happens all at once, with the new ``index_by`` field.
    corpus = Corpus(combined, index_by=index_by)

    featuresets = {}
    for featureset_name, featureset_1 in corpus_1.features.iteritems():
        # We avoid FeatureSets that were generated during the indexing process
        #  (e.g. 'citations', 'authors').
        if featureset_name in featuresets or featureset_name in corpus.features:
            continue

        features = {}

        # Can be FeatureSet or StructuredFeatureSet.
        fclass = type(featureset_1)
        if featureset_name in corpus_2.features:
            featureset_2 = corpus_2.features[featureset_name]
            for index, feature in featureset_2.iteritems():
                features[getattr(corpus_2[index], index_by)] = feature

        # Features from corpus_1 will be preferred over those from corpus_2.
        for index, feature in featureset_1.iteritems():
            features[getattr(corpus_1[index], index_by)] = feature

        featuresets[featureset_name] = fclass(features)

    # FeatureSets unique to corpus_2.
    for featureset_name, featureset_2 in corpus_2.features.iteritems():
        # We avoid FeatureSets that were generated during the indexing process
        #  (e.g. 'citations', 'authors').
        if featureset_name in featuresets or featureset_name in corpus.features:
            continue

        features = {}

        # Can be FeatureSet or StructuredFeatureSet.
        fclass = type(featureset_2)
        for index, feature in featureset_2.iteritems():
            features[getattr(corpus_2[index], index_by)] = feature

        featuresets[featureset_name] = fclass(features)

    corpus.features.update(featuresets)

    return corpus
