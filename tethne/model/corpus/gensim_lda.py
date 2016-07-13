"""
Interface for topic modeling with Gensim.
"""

from tethne import Feature, FeatureSet
from tethne.model import Model
from tethne.model.corpus import LDAMixin


class BaseGensimModel(Model):
    def __init__(self, *args, **kwargs):
        try:
            import gensim
        except ImportError:
            raise RuntimeError('This class requires the gensim package.')
        super(BaseGensimModel, self).__init__(*args, **kwargs)

    def prep(self, *args, **kwargs):
        if all([getattr(self, 'corpus', None),
                not getattr(self, 'featureset', None),
                getattr(self, 'featureset_name', None)]):
            self.featureset = self.corpus.features[self.featureset_name]
        if getattr(self, 'featureset', None):
            self.gcorpus, self.vocabulary = self.featureset.to_gensim_corpus()


class GensimLDAModel(BaseGensimModel, LDAMixin):
    @staticmethod
    def from_gensim(model, gcorpus, corpus=None):
        ldaModel = GensimLDAModel(model=model,
                                  gcorpus=gcorpus,
                                  corpus=corpus,
                                  vocabulary=dict(model.id2word),
                                  Z=int(model.num_topics))
        ldaModel.read()
        return ldaModel

    def run(self, Z=20, **kwargs):
        import gensim
        self.Z = Z
        # Since we are setting num_topics explicitly, we want to prevent the
        #  caller from setting it twice.
        kwargs.pop('num_topics', None)
        self.model = gensim.models.LdaModel(self.gcorpus,
                                            id2word=self.vocabulary,
                                            num_topics=Z,
                                            **kwargs)

        self.read()

    def read(self):
        self._read_theta()
        self._read_phi()

    def _read_theta(self):
        """
            Rows are documents, columns are topics. Rows sum to ~1.
        """
        if getattr(self, 'corpus', None):
            identifiers = self.corpus.indexed_papers.keys()
        else:
            identifiers = range(len(self.gcorpus))

        self.theta = gensim_to_theta_featureset(self.model, self.gcorpus, identifiers)

        if getattr(self, 'corpus', None):
            self.corpus.features['topics'] = self.theta
        return self.theta

    def _read_phi(self):
        """
            Rows are topics, columns are words. Rows sum to ~1.
        """

        self.phi = gensim_to_phi_featureset(self.model, as_idx=True)


def gensim_to_theta_featureset(model, corpus, identifiers):
    """
    Generate a :class:`.FeatureSet` describing document-topic assignments in a
    :class:`gensim.models.LdaModel`\.

    Parameters
    ----------
    model : :class:`gensim.models.LdaModel`
    corpus : iterable
        The bag-of-words corpus used to generate ``model``.
    identifiers : iterable
        Identifiers for the documents in ``corpus``. Must have the same shape
        as ``corpus``.

    Returns
    -------
    theta : :class:`.FeatureSet`
    """
    theta = FeatureSet()
    for idx, doc in zip(identifiers, corpus):
        theta.add(idx, Feature(model[doc]))
    return theta


def gensim_to_phi_featureset(model, Nwords=200, as_idx=False):
    """
    Generate a :class:`.FeatureSet` describing word-topic assignments in a
    :class:`gensim.models.LdaModel`\.

    Parameters
    ----------
    model : :class:`gensim.models.LdaModel`
    Nwords : int
        (default: 200) Number of words to include in each :class:`.Feature`\.
    as_idx : bool
        (default: False) If True, tokens in each :class:`.Feature` will be
        given as their integer representation.

    Returns
    -------
    phi : :class:`.FeatureSet`
    """
    if as_idx:
        lookup = {t: i for i, t in model.id2word.iteritems()}
    tx = lambda t: lookup[t] if as_idx else t

    phi = FeatureSet()
    for k in range(model.num_topics):
        term, value = zip(*model.show_topic(k, Nwords))
        phi.add(k, Feature(list(zip([tx(t) for t in term], value))))

    return phi
