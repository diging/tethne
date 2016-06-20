"""
Classes and methods related to the :class:`.MALLETModelManager`\.
"""

import os
import re
import shutil
import tempfile
import subprocess
import csv
import platform
from collections import defaultdict

from networkx import Graph

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str

import logging
logging.basicConfig()
logger = logging.getLogger('mallet')
logger.setLevel('ERROR')

from tethne import write_documents, Feature, FeatureSet
from tethne.model import Model
import tethne

# Determine path to MALLET.
TETHNE_PATH = os.path.split(os.path.abspath(tethne.__file__))[0]
MALLET_PATH = os.path.join(TETHNE_PATH, 'bin', 'mallet-2.0.7')

import sys
if sys.version_info[0] > 2:
    xrange = range


class LDAModel(Model):
    """
    Generates a :class:`.LDAModel` from a :class:`.Corpus` using
    `MALLET <http://mallet.cs.umass.edu/>`_.

    The :class:`.Corpus` should already contain at least one featurset,
    indicated by the `feature` parameter, such as wordcounts. You may
    specify two working directories: `temppath` should be a working
    directory that will contain intermediate files (e.g. documents, data
    files, metadata), while `outpath` will contain the final model and any
    plots generated during the modeling process. If `temppath` is not
    provided, generates and uses a system temporary directory.

    Tethne comes bundled with a recent version of MALLET. If you would
    rather use your own install, you can do so by providing the
    `mallet_path` parameter. This should point to the directory containing
    ``/bin/mallet``.

    .. autosummary::
       :nosignatures:

       topic_over_time

    Parameters
    ----------
    D : :class:`.Corpus`
    feature : str
        Key from D.features containing wordcounts (or whatever
        you want to model with).
    outpath : str
        Path to output directory.
    temppath : str
        Path to temporary directory.
    mallet_path : str
        Path to MALLET install directory (contains bin/mallet).

    Examples
    --------

    Starting with some JSTOR DfR data (with wordcounts), a typical workflow
    might look something like this:

    .. code-block:: python

       >>> from nltk.corpus import stopwords                 #  1. Get stoplist.
       >>> stoplist = stopwords.words()

       >>> from tethne.readers import dfr                    #  2. Build Corpus.
       >>> C = dfr.corpus_from_dir('/path/to/DfR/datasets', 'uni', stoplist)

       >>> def filt(s, C, DC):                           # 3. Filter wordcounts.
       ...     if C > 3 and DC > 1 and len(s) > 3:
       ...         return True
       ...     return False
       >>> C.filter_features('wordcounts', 'wc_filtered', filt)

       >>> from tethne.model import MALLETModelManager       #   4. Get Manager.
       >>> outpath = '/path/to/my/working/directory'
       >>> mallet = '/Applications/mallet-2.0.7'
       >>> M = MALLETModelManager(C, 'wc_filtered', outpath, mallet_path=mallet)

       >>> M.prep()                                          #    5. Prep model.

       >>> model = M.build(Z=50, max_iter=300)               #   6. Build model.
       >>> model                                             # (may take awhile)
       <tethne.model.corpus.ldamodel.LDAModel at 0x10bfac710>

    A plot showing the log-likelihood/topic over modeling iterations should be
    generated in your `outpath`. For example:

    .. figure:: _static/images/ldamodel_LL.png
       :width: 400
       :align: center

    Behind the scenes, the :func:`.prep` procedure generates a plain-text corpus
    file at `temppath`, along with a metadata file. MALLET's ``import-file``
    procedure is then called, which translates the corpus into MALLET's internal
    format (also stored at the `temppath`).

    The :func:`.build` procedure then invokes MALLET's ``train-topics``
    procedure. This step may take a considerable amount of time, anywhere from
    a few minutes (small corpus, few topics) to a few hours (large corpus, many
    topics).

    For a :class:`.Corpus` with a few thousand :class:`.Paper`\s, 300 - 500
    iterations is often sufficient to achieve convergence for 20-100 topics.

    Once the :class:`.LDAModel` is built, you can access its methods directly.
    See full method descriptions in :class:`.LDAModel`\.

    For more information about topic modeling with MALLET see
    `this tutorial <http://programminghistorian.org/lessons/topic-modeling-and-mallet>`_.

    """

    mallet_path = MALLET_PATH

    def __init__(self, *args, **kwargs):
        self.mallet_bin = os.path.join(self.mallet_path, "bin", "mallet")

        if platform.system() == 'Windows':
            self.mallet_bin += '.bat'
        os.putenv('MALLET_HOME', self.mallet_path)
        super(LDAModel, self).__init__(*args, **kwargs)

    def prep(self):
        self.dt = os.path.join(self.temp, "dt.dat")
        self.wt = os.path.join(self.temp, "wt.dat")
        self.om = os.path.join(self.temp, "model.mallet")

        self._generate_corpus()

    def _generate_corpus(self):
        """
        Writes a corpus to disk amenable to MALLET topic modeling.
        """

        target = self.temp + 'mallet'
        paths = write_documents(self.corpus, target, self.featureset_name,
                                ['date', 'title'])
        self.corpus_path, self.metapath = paths

        self._export_corpus()

    def _export_corpus(self):
        """
        Calls MALLET's `import-file` method.
        """
        # bin/mallet import-file --input /Users/erickpeirson/mycorpus_docs.txt
        #     --output mytopic-input.mallet --keep-sequence --remove-stopwords

        if not os.path.exists(self.mallet_bin):
            raise IOError("MALLET path invalid or non-existent.")
        self.input_path = os.path.join(self.temp, "input.mallet")

        exit = subprocess.call([
                self.mallet_bin,
                'import-file',
                '--input', self.corpus_path,
                '--output', self.input_path,
                '--keep-sequence',          # Required for LDA.
                '--remove-stopwords'])      # Probably redundant.

        if exit != 0:
            msg = "MALLET import-file failed with exit code {0}.".format(exit)
            raise RuntimeError(msg)

    def run(self, **kwargs):
        """
        Calls MALLET's `train-topic` method.
        """
        #$ bin/mallet train-topics --input mytopic-input.mallet
        #> --num-topics 100
        #> --output-doc-topics /Users/erickpeirson/doc_top
        #> --word-topic-counts-file /Users/erickpeirson/word_top
        #> --output-topic-keys /Users/erickpeirson/topic_keys

        if not os.path.exists(self.mallet_bin):
            raise IOError("MALLET path invalid or non-existent.")

        for attr in ['Z', 'max_iter']:
            if not hasattr(self, attr):
                raise AttributeError('Please set {0}'.format(attr))

        self.ll = []
        self.num_iters = 0
        logger.debug('run() with k={0} for {1} iterations'.format(self.Z, self.max_iter))

        prog = re.compile(u'\<([^\)]+)\>')
        ll_prog = re.compile(r'(\d+)')
        p = subprocess.Popen([
                    self.mallet_bin,
                    'train-topics',
                    '--input', self.input_path,
                    '--num-topics', unicode(self.Z),
                    '--num-iterations', unicode(self.max_iter),
                    '--output-doc-topics', self.dt,
                    '--word-topic-counts-file', self.wt,
                    '--output-model', self.om],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE)

        # Handle output of MALLET in real time.
        while p.poll() is None:
            l = p.stderr.readline()

            # Keep track of LL/topic.
            try:
                this_ll = float(re.findall(u'([-+]\d+\.\d+)', l)[0])
                self.ll.append(this_ll)
            except IndexError:  # Not every line will match.
                pass

            # Keep track of modeling progress.
            try:
                this_iter = float(prog.match(l).groups()[0])
                progress = int(100. * this_iter/self.max_iter)
                print 'Modeling progress: {0}%.\r'.format(progress),
            except AttributeError:  # Not every line will match.
                pass

        self.num_iters += self.max_iter
        self.load()

    def load(self, **kwargs):
        self._read_theta(kwargs.get('dt', self.dt))
        self._read_phi(kwargs.get('wt', self.wt))

    def _read_theta(self, dt):
        """
        Used by :func:`.from_mallet` to reconstruct theta posterior
        distributions.

        Returns
        -------
        td : Numpy array
            Rows are documents, columns are topics. Rows sum to ~1.
        """

        self.theta = FeatureSet()

        with open(dt, "rb") as f:
            i = -1
            reader = csv.reader(f, delimiter='\t')
            for line in reader:
                i += 1
                if i == 0:
                    continue     # Avoid header row.

                d, id, t = int(line[0]), unicode(line[1]), line[2:]
                feature = Feature([(int(t[i]), float(t[i + 1]))
                                   for i in xrange(0, len(t) - 1, 2)])
                self.theta.add(id, feature)

        self.corpus.features['topics'] = self.theta
        return self.theta

    def _read_phi(self, wt):
        """
        Used by :func:`.from_mallet` to reconstruct phi posterior distributions.

        Returns
        -------
        wt : Numpy array
            Rows are topics, columns are words. Rows sum to ~1.
        """

        self.vocabulary = {}
        phi_features = {}

        # TODO: make this encoding-safe.
        with open(wt, "r") as f:
            reader = csv.reader(f, delimiter=' ')
            topics = defaultdict(list)
            for line in reader:
                w, term = int(line[0]), unicode(line[1])
                self.vocabulary[w] = term

                for l in line[2:]:
                    k, c = l.split(':')    # Topic and assignment count.
                    topics[int(k)].append((w, int(c)))

        for k, data in topics.iteritems():
            nfeature = Feature(data).norm

            phi_features[k] = nfeature
        self.phi = FeatureSet(phi_features)

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
                in self.phi.features[k].top(Nwords)]

    def list_topics(self, Nwords=10):
        """
        List the top ``Nwords`` words for each topic.
        """
        return [(k, self.list_topic(k, Nwords)) for k in xrange(len(self.phi))]


    def print_topics(self, Nwords=10):
        """
        Print the top ``Nwords`` words for each topic.
        """
        print('Topic\tTop %i words' % 10)
        for k, words in self.list_topics(Nwords):
            print(unicode(k).ljust(3) + '\t' + ' '.join(list(zip(*words))[0]))


    def topic_over_time(self, k, mode='counts', slice_kwargs={}):
        """
        Calculate the representation of topic ``k`` in the corpus over time.
        """

        return self.corpus.feature_distribution('topics', k, mode=mode,
                                                **slice_kwargs)
