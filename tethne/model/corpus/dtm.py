"""
Fit the DTM topic model.
"""

from tethne.model import Model

import os, sys, re, shutil, tempfile, subprocess, csv, platform, inspect
from collections import defaultdict

TETHNE_PATH = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[0][1])), '..', '..')
DTM_PATH = os.path.join(TETHNE_PATH, 'bin', 'dtm')


def _to_dtm_input(corpus, target, featureset_name, fields=['date','atitle'], **slice_kwargs):
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
        vocab = corpus.features[featureset_name].index
        lookup = corpus.features[featureset_name].lookup
        features = corpus.features[featureset_name].features
    except KeyError:
        raise KeyError('No featureset found with name %s' % featureset_name)

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
    seq = defaultdict(list)
    try:
        metaFile = open(target + '-meta.dat', 'wb')     # Metadata.
        multFile = open(target + '-mult.dat', 'wb')
    except IOError:
        raise IOError('Invalid target. Could not open files for writing.')

    metaFile.write('\t'.join(['id'] + fields ) + '\n')    # Header row.
    for year, papers in corpus.slice(**slice_kwargs):
        for paper in papers:
            ident = getattr(paper, corpus.index_by)
            if ident not in features:
                continue

            grams = features[ident]
            seq[year].append(ident)
            wordcount = str(len(grams))  # Number of unique words.

            # Write data.
            mdat = ['{0}:{1}'.format(lookup[g], c) for g, c in grams]
            multFile.write(' '.join([wordcount] + mdat) + '\n')

            # Write metadata.
            meta = [ident] + [unicode(getattr(paper, f, u'')) for f in fields]
            metaFile.write('\t'.join(meta) + '\n')

    metaFile.close()
    multFile.close()

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
        for index, word in sorted(vocab.items()):
            vocabFile.write('{0}\n'.format(word))

    return len(seq)


class DTMModel(Model):
    dtm_path = DTM_PATH

    def prep(self, **slice_kwargs):
        self.slice_kwargs = slice_kwargs
        self.outname = '{0}/model_run'.format(self.temp)

        self.mult_path = '{0}/tethne-mult.dat'.format(self.temp)
        self.seq_path = '{0}/tethne-seq.dat'.format(self.temp)
        self.vocab_path = '{0}/tethne-vocab.dat'.format(self.temp)
        self.meta_path = '{0}/tethne-meta.dat'.format(self.temp)
        self._generate_corpus(**slice_kwargs)

    def run(self, **kwargs):
        ## Run the dynamic topic model.
        #./main \
        #  --ntopics=20 \
        #  --mode=fit \
        #  --rng_seed=0 \
        #  --initialize_lda=true \
        #  --corpus_prefix=example/test \
        #  --outname=example/model_run \
        #  --top_chain_var=0.005 \
        #  --alpha=0.01 \
        #  --lda_sequence_min_iter=6 \
        #  --lda_sequence_max_iter=20 \
        #  --lda_max_em_iter=10
        if not hasattr(self, 'll'):
            self.ll = []
        if not hasattr(self, 'll_iters'):
            self.ll_iters = []

        top_chain_var = kwargs.get('top_chain_var', 0.005)
        lda_seq_min_iter = kwargs.get('lda_seq_min_iter', 3)
        lda_seq_max_iter = kwargs.get('lda_seq_max_iter', 10)
        lda_max_em_iter = kwargs.get('lda_max_em_iter', 5)
        alpha = kwargs.get('alpha', 0.01)

        max_iter = getattr(self, 'max_iter', 100)
        Z = getattr(self, 'Z', 20)

        max_v = lda_seq_min_iter * lda_max_em_iter * self.N

        self.conv = []
        i = 1

        corpus_prefix = '{0}/tethne'.format(self.temp)

        FNULL = open(os.devnull, 'w')

        p = subprocess.Popen( [ self.dtm_path,
                    '--ntopics={0}'.format(Z),
                    '--mode=fit',
                    '--rng_seed=0',
                    '--initialize_lda=true',
                    '--corpus_prefix={0}'.format(corpus_prefix),
                    '--outname={0}'.format(self.outname),
                    '--top_chain_var={0}'.format(top_chain_var),
                    '--alpha={0}'.format(alpha),
                    '--lda_sequence_min_iter={0}'.format(lda_seq_min_iter),
                    '--lda_sequence_max_iter={0}'.format(lda_seq_max_iter),
                    '--lda_max_em_iter={0}'.format(lda_max_em_iter) ],
                stderr=subprocess.PIPE,
                stdout=subprocess.PIPE)

        while p.poll() is None:
            l = p.stderr.readline()
            print l
            try:    # Find the LL
                this_ll = float(re.findall(r'^lhood\s+=\s+([-]?\d+\.\d+)', l)[0])
                self.ll.append(this_ll)

                self.ll_iters.append(i)
                i += 1
            except IndexError:
                pass

            try:    # Find conv
                conv = re.findall(r'conv\s+=\s+([-]?\d+\.\d+e[-]\d+)', l)
                self.conv.append(float(conv[0]))

                progress = int(100 * float(len(self.conv))/float(max_v))

            except IndexError:
                pass
        self.load()

        # self.max_iter += lda_max_em_iter   # TODO: does this make sense?


    def _generate_corpus(self, **slice_kwargs):
        """
        Writes a corpus to disk amenable to DTM.
        """

        self.N = _to_dtm_input(self.corpus, self.temp+'/tethne', featureset_name=self.featureset_name)

    def load(self):
        """Load and return a :class:`.DTMModel`\."""

        self.e_theta, self.phi, self.metadata, self.vocabulary = from_gerrish(self.outname, self.meta_path, self.vocab_path)

        self.Z = e_theta.shape[0]   # Number of topics.
        self.M = e_theta.shape[1]   # Number of documents.

        self.W = phi.shape[1]    # Number of words.
        self.T = phi.shape[2]    # Number of time periods.

        self.lookup = { v['id']:k for k,v in metadata.iteritems() }

        logging.debug('DTMModel.__init__(): loaded model with' + \
                   ' {0} topics, {1} documents,'.format(self.Z, self.M) + \
                   ' {0} words, {1} time periods.'.format(self.W, self.T))



    def _item_description(self, i, **kwargs):
        """
        Proportion of each topic in document.
        """

        return [ (k, self.e_theta[k, i])
                    for k in xrange(self.e_theta[:, i].size) ]

    def _dimension_description(self, k, t=0, **kwargs):
        """
        Yields probability distribution over terms.
        """

        return [ (w, self.phi[k, w, t])
                    for w in xrange(self.phi[k, :, t].size) ]

    def _dimension_items(self, k, threshold, **kwargs):
        """
        Returns items that contain ``k`` at or above ``threshold``.

        Parameters
        ----------
        k : int
            Topic index.
        threshold : float
            Minimum representation of ``k`` in document.

        Returns
        -------
        description : list
            A list of ( item, weight ) tuples.
        """

        description = [ (self.metadata[i]['id'], self.e_theta[k,i])
                            for i in xrange(self.e_theta[k,:].size)
                            if self.e_theta[k,i] >= threshold ]
        return description

    def topic_evolution(self, k, Nwords=5):
        """
        Generate a plot that shows p(w|z) over time for the top ``Nwords``
        terms.

        Parameters
        ----------
        k : int
            A topic index.
        Nwords : int
            Number of words to return.

        Returns
        -------
        keys : list
            Start-date of each time-period.
        t_series : list
            Array of p(w|t) for Nwords for each time-period.
        """

        t_keys = range(self.T)
        t_values = {}
        for t in t_keys:
            dim = self.dimension(k, t=t, top=Nwords)
            for w,p in dim:
                if w not in t_values:
                    t_values[w] = {}
                t_values[w][t] = p

        t_series = {}
        for w, values in t_values.iteritems():
            word = self.vocabulary[w]
            series = []
            for t in t_keys:
                if t in values:
                    series.append(values[t])
                else:   # No value for that time-period.
                    series.append(0.)
            t_series[word] = series

        return t_keys, t_series

    def list_topic(self, k, t, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.

        Parameters
        ----------
        k : int
            A topic index.
        t : int
            A time index.
        Nwords : int
            Number of words to return.

        Returns
        -------
        as_list : list
            List of words in topic.
        """
        words = self.dimension(k, t=t, top=Nwords)
        as_list = [ self.vocabulary[w] for w,p in words ]

        return as_list

    def list_topic_diachronic(self, k, Nwords=10):
        as_dict = { t:self.list_topic(k, t, Nwords)
                        for t in xrange(self.T) }
        return as_dict

    def print_topic_diachronic(self, k, Nwords=10):
        as_dict = self.list_topic_diachronic(k, Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)

        print as_string

    def print_topic(self, k, t, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.

        Parameters
        ----------
        k : int
            A topic index.
        t : int
            A time index.
        Nwords : int
            Number of words to return.

        Returns
        -------
        as_string : str
            Joined list of words in topic.
        """

        as_string = ', '.join(self.list_topic(k, t=t, Nwords=Nwords))

        print as_string

    def list_topics(self, t, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.

        Parameters
        ----------
        t : int
            A time index.
        Nwords : int
            Number of words to return for each topic.

        Returns
        -------
        as_dict : dict
            Keys are topic indices, values are list of words.
        """

        as_dict = {}
        for k in xrange(self.Z):
            as_dict[k] = self.list_topic(k, t, Nwords)

        return as_dict

    def print_topics(self, t, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.

        Parameters
        ----------
        t : int
            A time index.
        Nwords : int
            Number of words to return for each topic.

        Returns
        -------
        as_string : str
            Newline-delimited lists of words for each topic.
        """

        as_dict = self.list_topics(t, Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)

        print as_string



def from_gerrish(target, metadata, vocabulary, metadata_key='doi'):
    """
    Generate a :class:`.DTMModel` from the output of `S. Gerrish's C++ DTM
    implementation <http://code.google.com/p/princeton-statistical-learning/downloads/detail?name=dtm_release-0.8.tgz>`_.

    The Gerrish DTM implementation generates a large number of data files
    contained in a directory called ``lda-seq``. The ``target`` parameter
    should be the path to that directory.

    ``metadata`` should be the path to a tab-delimted metadata file. Those
    records should occur in the same order as in the corpus data files used
    to generate the model. For example::

       id	date	atitle
       10.2307/2437162	1945	SOME ECOTYPIC RELATIONS OF DESCHAMPSIA CAESPITOSA
       10.2307/4353229	1940	ENVIRONMENTAL INFLUENCE AND TRANSPLANT EXPERIMENTS
       10.2307/4353158	1937	SOME FUNDAMENTAL PROBLEMS OF TAXONOMY AND PHYLOGENETICS

    ``vocabulary`` should be the path to a file containing the words used to
    generate the model, one per line.

    Parameters
    ----------
    target : str
        Path to ``lda-seq`` output directory.
    metadata : str
        Path to metadata file.
    vocabulary : str
        Path to vocabulary file.

    Returns
    -------
    :class:`.DTMModel`
    """

    e_log_prob = 'topic-{0}-var-e-log-prob.dat'
    info = 'topic-{0}-info.dat'
    obs = 'topic-{0}-obs.dat'

    reader = GerrishLoader(target, metadata, vocabulary)#, metadata, vocabulary)
    return reader.load()


class GerrishLoader(object):
    """
    Helper class for parsing results from `S. Gerrish's C++ implementation <http://code.google.com/p/princeton-statistical-learning/downloads/detail?name=dtm_release-0.8.tgz>`_
    Parameters
    ----------
    target : str
        Path to ``lda-seq`` output directory.
    metadata : str
        Path to metadata file.
    vocabulary : str
        Path to vocabulary file.

    Returns
    -------
    :class:`.DTMModel`
    """

    def __init__(self, target, metadata_path, vocabulary_path):
        self.target = target
        self.metadata_path = metadata_path
        self.vocabulary_path = vocabulary_path

        self.handler = { 'prob': self._handle_prob,
                         'info': self._handle_info,
                         'obs': self._handle_obs     }

        self.tdict = {}

    def load(self):
        try:
            contents = os.listdir(self.target)
            lda_seq_dir = os.listdir('{0}/lda-seq'.format(self.target))
        except OSError:
            raise OSError("Invalid target path.")

        # Metadata.
        self._handle_metadata()
        self._handle_vocabulary()

        # Meta-parameters.
        self._handle_metaparams()

        # Topic proportions.
        self._handle_gammas()

        # p(w|z)
        for fname in lda_seq_dir:
            fs = re.split('-|\.', fname)

            if fs[0] == 'topic':
                z_s = fs[1]
                z = int(z_s)
                self.handler[fs[-2]](fname, z)

        tkeys = sorted(self.tdict.keys())
        self.phi = np.array( [ self.tdict[z] for z in tkeys ])

        return self.e_theta, self.phi, self.metadata, self.vocabulary

    def _handle_metaparams(self):
        # Read metaparameters.
        with open('{0}/lda-seq/info.dat'.format(self.target), 'rb') as f:
            for line in f.readlines():
                ls = line.split()
                if ls[0] == 'NUM_TOPICS':
                    self.N_z = int(ls[1])

                elif ls[0] == 'NUM_TERMS':
                    self.N_w = int(ls[1])

                elif ls[0] == 'SEQ_LENGTH':
                    self.N_t = int(ls[1])

                elif ls[0] == 'ALPHA':
                    self.A = np.array(ls[2:])

    def _handle_gammas(self):
        # Read gammas -> e_theta
        with open('{0}/lda-seq/gam.dat'.format(self.target), 'rb') as f:
            data = np.array(f.read().split())
            self.N_d = data.shape[0]/self.N_z
            b = data.reshape((self.N_d, self.N_z)).astype('float32')
            rs = np.sum(b, axis=1)
            self.e_theta = np.array([ b[:,z]/rs for z in xrange(self.N_z) ])

    def _handle_prob(self, fname, z):
        """
        - topic-???-var-e-log-prob.dat: the e-betas (word distributions) for
        topic ??? for all times.  This is in row-major form,
        """
        with open('{0}/lda-seq/{1}'.format(self.target, fname), 'rb') as f:
            data = np.array(f.read().split()).reshape((self.N_w, self.N_t))
            self.tdict[z] = np.exp(data.astype('float32'))

    def _handle_info(self, fname, z):
        """
        No need to do anything with these yet.
        """
        pass

    def _handle_obs(self, fname, z):
        """
        TODO: Figure out what, if anything, this is good for.
        """
        pass

    def _handle_metadata(self):
        """

        Returns
        -------
        metadata : dict
            Keys are document indices, values are identifiers from a
            :class:`.Paper` property (e.g. DOI).
        """

        if self.metadata_path is None:
            self.metadata = None
            return

        self.metadata = {}

        with open(self.metadata_path, "rU") as f:
            reader = csv.reader(f, delimiter='\t')

            all_lines = [ l for l in reader ]
            keys = all_lines[0]
            lines = all_lines[1:]

            i = 0
            for l in lines:
                self.metadata[i] = { keys[i]:l[i] for i in xrange(0, len(l)) }
                i += 1

        return self.metadata

    def _handle_vocabulary(self):
        """

        Returns
        -------
        vocabulary : dict
            Keys are word indices, values are word strings.
        """
        if self.vocabulary_path is None:
            raise RuntimeError("No vocabulary provided.")

        # Build vocabulary
        self.vocabulary = {}
        with open(self.vocabulary_path, 'rU') as f:
            i = 0
            for v in f.readlines():
                self.vocabulary[i] = v.strip('\n')
                i += 1

        return self.vocabulary
