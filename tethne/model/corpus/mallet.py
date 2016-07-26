"""
Fit the vanilla LDA topic model with MALLET.
"""

import os, sys, re, shutil, tempfile, subprocess, csv, platform, inspect
from collections import defaultdict
from networkx import Graph

PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str

import logging
logging.basicConfig()
logger = logging.getLogger('mallet')
logger.setLevel('ERROR')

from tethne import write_documents, Feature, FeatureSet
from tethne.model import Model
from tethne.model.corpus import LDAMixin
from tethne.utilities import is_int, is_float, is_number

# Determine path to MALLET.

TETHNE_PATH = os.path.join(os.path.dirname(os.path.abspath(inspect.stack()[0][1])), '..', '..')
MALLET_PATH = os.path.join(TETHNE_PATH, 'bin', 'mallet-2.0.7')

import sys
if sys.version_info[0] > 2:
    xrange = range


class LDAModel(Model, LDAMixin):
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

    @staticmethod
    def from_mallet(wt_path, dt_path, model_path, corpus=None,
                    featureset_name=None):
        model = LDAModel(corpus=corpus, featureset_name=featureset_name,
                         nodelete=True,    # So that it doesn't discard your files when you're done.
                         prep=False,       # Skips building the corpus and calling MALLET's import function.
                         wt=wt_path,
                         dt=dt_path,
                         om=model_path)
        model.load()
        return model

    def __init__(self, *args, **kwargs):
        self.mallet_bin = os.path.join(self.mallet_path, "bin", "mallet")

        if platform.system() == 'Windows':
            self.mallet_bin += '.bat'
        os.environ['MALLET_HOME'] = self.mallet_path

        super(LDAModel, self).__init__(*args, **kwargs)

        if not hasattr(self, 'dt'):
            self.dt = os.path.join(self.temp, "dt.dat")
        if not hasattr(self, 'wt'):
            self.wt = os.path.join(self.temp, "wt.dat")
        if not hasattr(self, 'om'):
            self.om = os.path.join(self.temp, "model.mallet")

    def prep(self):
        self._generate_corpus()

    def _generate_corpus(self):
        """
        Writes a corpus to disk amenable to MALLET topic modeling.
        """

        if not self.corpus:
            raise RuntimeError('Must set model.corpus before external' \
                             + ' documents can be generated')
        if self.verbose:
            print 'LDAModel: Write corpus for topic modeling'
        sys.stdout.flush()
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
        if self.verbose:
            print 'LDAModel: Import corpus into MALLET'
        sys.stdout.flush()
        exit = subprocess.call([
                self.mallet_bin,
                'import-file',
                '--input', self.corpus_path,
                '--output', self.input_path,
                '--keep-sequence',          # Required for LDA.
                '--remove-stopwords'],      # Probably redundant.
            env={"MALLET_HOME": self.mallet_path})

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

        if self.verbose:
            print 'LDAModel: Start MALLET topic modeling'
        sys.stdout.flush()
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
                stderr=subprocess.PIPE,
            env={"MALLET_HOME": self.mallet_path})

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
                if self.verbose:
                    print 'Modeling progress: {0}%.\r'.format(progress),
            except AttributeError:  # Not every line will match.
                pass

        self.num_iters += self.max_iter
        self.load()

    def load(self, **kwargs):
        if self.verbose:
            print 'LDAModel: Load MALLET results'
        sys.stdout.flush()
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

        self.theta = mallet_to_theta_featureset(dt)
        if self.corpus:
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

        self.phi, self.vocabulary = mallet_to_phi_featureset(wt)
        self.Z = len(self.phi)


def mallet_to_theta_featureset(dt_path):
    """
    Generate a :class:`.FeatureSet` describing document-topic assignments from a
    MALLET document-topic output file.

    Parameters
    ----------
    dt_path : str
        Full path to the document-topic data file created by MALLET.

    Returns
    -------
    theta : :class:`.FeatureSet`
    """
    theta = FeatureSet()

    def _handle_with_name(line):
        d, ident, t = int(line[0]), unicode(line[1]), line[2:]
        return ident, Feature([(int(t[i]), float(t[i + 1])) for i in xrange(0, len(t) - 1, 2)])

    def _handle_without_name(line):
        d, t = int(line[0]), line[1:]
        return d, Feature([(int(t[i]), float(t[i + 1])) for i in xrange(0, len(t) - 1, 2)])

    line_handler = _handle_with_name
    with open(dt_path, "rb") as f:
        i = -1
        for raw_line in f:
            line = raw_line.split()
            i += 1
            if i == 0:
                continue     # Avoid header row.
            elif i == 1:
                if not is_int(line[2]) and is_float(line[2]):
                    line_handler = _handle_without_name
            theta.add(*line_handler(line))
    return theta


def mallet_to_phi_featureset(wt_path):
    """
    Generate a :class:`.FeatureSet` describing word-topic assignments from a
    MALLET word-topic output file.

    Parameters
    ----------
    wt_path : str
        Full path to the word-topic data file created by MALLET.

    Returns
    -------
    phi : :class:`.FeatureSet`
    """
    vocabulary = {}
    phi_features = {}

    # TODO: make this encoding-safe.
    with open(wt_path, "r") as f:
        # reader = csv.reader(f, delimiter=' ')
        topics = defaultdict(list)
        for raw_line in f:
            line = raw_line.split()
            w, term = int(line[0]), unicode(line[1])
            vocabulary[w] = term

            for l in line[2:]:
                k, c = l.split(':')    # Topic and assignment count.
                topics[int(k)].append((w, int(c)))

    for k, data in topics.iteritems():
        nfeature = Feature(data).norm

        phi_features[k] = nfeature
    return FeatureSet(phi_features), vocabulary
