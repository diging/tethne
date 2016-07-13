"""
Corpus models describe latent topics (dimensions) that explain the
distribution of features (eg words) among documents in a :class:`.Corpus`\.

Tethne presently represents two corpus models:

.. autosummary::
   :nosignatures:

   ldamodel.LDAModel
   dtmmodel.DTMModel

Most model classes are subclasses of :class:`.BaseModel`\. It is assumed that
each model describes a set of items (eg :class:`.Paper`\s or authors), a set
of dimensions that describe those items (eg topics), and a set of features
that comprise those dimensions (eg words).
"""


class LDAMixin(object):
    def topics_in(self, d, topn=5):
        """
        List the top ``topn`` topics in document ``d``.
        """
        return self.theta.features[d].top(topn)

    def list_topic(self, k, Nwords=10):
        """
        List the top ``topn`` words for topic ``k``.


        Examples
        --------

        .. code-block:: python

           >>> model.list_topic(1, Nwords=5)
           [ 'opposed', 'terminates', 'trichinosis', 'cistus', 'acaule' ]

        """

        return [(self.vocabulary[w], p) for w, p
                in self.phi[k].top(Nwords)]

    def list_topics(self, Nwords=10):
        """
        List the top ``Nwords`` words for each topic.
        """
        return [(k, self.list_topic(k, Nwords)) for k in xrange(len(self.phi))]


    def print_topics(self, Nwords=10):
        """
        Print the top ``Nwords`` words for each topic.
        """
        print('Topic\tTop %i words' % Nwords)
        for k, words in self.list_topics(Nwords):
            print(unicode(k).ljust(3) + '\t' + ' '.join(list(zip(*words))[0]))


    def topic_over_time(self, k, mode='counts', slice_kwargs={}):
        """
        Calculate the representation of topic ``k`` in the corpus over time.
        """

        return self.corpus.feature_distribution('topics', k, mode=mode,
                                                **slice_kwargs)
