"""
Methods for parsing JSTOR Data-for-Research datasets.

.. autosummary::


"""

import os
import xml.etree.ElementTree as ET
import re
from collections import Counter
from tethne import Paper, Corpus, Feature, FeatureSet, StreamingCorpus, StreamingFeatureSet
from tethne.utilities import dict_from_node, strip_non_ascii, number
from tethne.readers.base import XMLParser
import iso8601
from io import BytesIO

from unidecode import unidecode
import codecs

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


class DfRParser(XMLParser):
    entry_class = Paper

    tags = {
        'type': 'documentType',
        'pubdate': 'date',
        'journaltitle': 'journal',
        'author': 'authors_full',
    }

    def open(self):
        with codecs.open(self.path, 'r', encoding="utf-8") as f:
            # JSTOR hasn't always represented ampersands correctly.
            contents = re.sub('(&)(?!amp;)', lambda match: '&amp;', f.read())
            # self.root = ET.fromstring(contents)
        # pattern = './/{elem}'.format(elem=self.entry_element)
        # self.elements = self.root.findall(pattern)
        self.iterator = ET.iterparse(BytesIO(contents.encode('utf-8')))

        self.at_start = False
        self.at_end = False
        self.children = []

    def handle_unicode(self, value):
        # if type(value) is not str:
        #     value = unidecode(value)
        return value

    def handle_journaltitle(self, value):
        return self.handle_unicode(value)

    def handle_title(self, value):
        return self.handle_unicode(value)

    def handle_author(self, value):
        # if type(value) is not str:
        #     value = unidecode(value)

        lname = value.split(' ')

        final = lname[-1].upper()
        if final in ['JR.', 'III']:
            aulast = lname[-2].upper() + " " + final.strip(".")
            auinit = ' '.join(lname[0:-2]).replace('.','').strip().upper()
        else:
            aulast = final
            auinit = ' '.join(lname[0:-1]).replace('.','').strip().upper()

        return aulast, auinit

    def handle_pubdate(self, value):
        return iso8601.parse_date(value).year

    def postprocess_authors_full(self, entry):
        if type(entry.authors_full) is not list:
            entry.authors_full = [entry.authors_full]


# TODO: retire this class.
class GramGenerator(object):
    """
    Yields N-gram data from on-disk dataset, to make loading big datasets a bit
    more memory-friendly.

    Reusable, in the sense that :func:`.items`\, :func:`.items`\,
    :func:`.keys`\, and :func:`.values` all return new :class:`.GramGenerator`
    instances with the same path. This allows a :class:`.GramGenerator` to
    sneakily pass as an ngrams dict in most practical situations.
    """

    def __init__(self, path, elem, values=False, keys=False, ignore_hash=True):
        """

        Parameters
        ----------
        path : str
            Path to unzipped JSTOR DfR folder containing N-grams (e.g.
            'bigrams').
        elem : str
            Element in DfR dataset containing data of interest. E.g. 'bigrams'.
        values : bool
            If True, :func:`.next` returns only values. Otherwise, returns
            (key,value) tuples.
        """

        if not os.path.exists(path):
            raise ValueError('No such file or directory')

        self.path = path
        self.elem = elem
        if elem.endswith('s'):
            self.elem_xml = elem[:-1]
        else:
            self.elem_xml = elem

        self.ignore_hash = ignore_hash

        self.files = os.listdir(os.path.join(path, elem))
        self.N = len([ d for d in self.files if d.split('.')[-1] == 'XML' ])
        self.i = 0

        self.V = values
        self.K = keys

        if self.V and self.K:
            raise ValueError('values and keys cannot both be true.')

    def __len__(self):
        return self.N

    def __iter__(self):
        return self

    def __next__(self):
        return self.next()

    def next(self):
        if self.i < self.N:
            cur = int(self.i)
            self.i += 1
            return self._get(cur)
        else:
            raise StopIteration()

    def items(self):
        """
        Returns a :class:`GramGenerator` that produces key,value tuples.
        """
        return GramGenerator(self.path, self.elem,
                             ignore_hash=self.ignore_hash)

    def values(self):
        """
        Returns a :class:`GramGenerator` that produces only values.
        """
        return GramGenerator(self.path, self.elem, values=True,
                             ignore_hash=self.ignore_hash)

    def keys(self):
        """
        Returns a :class:`GramGenerator` that produces only keys.
        """
        return GramGenerator(self.path, self.elem, keys=True,
                             ignore_hash=self.ignore_hash)

    def __getitem__(self, key):
        return self._get(key)

    def _get(self, i):
        """
        Retrieve data for the ith file in the dataset.
        """
        with codecs.open(os.path.join(self.path, self.elem, self.files[i]), 'rb', encoding='utf-8') as f:
            # JSTOR hasn't always produced valid XML.
            contents = re.sub('(&)(?!amp;)', lambda match: '&amp;', f.read())

            # ElementTree does not support unicode strings.
            root = ET.fromstring(contents.encode('utf-8'))

        doi = root.attrib['id']

        if self.K:  # Keys only.
            return doi

        grams = []
        for gram in root.findall(self.elem_xml):
            text = gram.text.strip()
            if type(text) is str:
                text = text.decode('utf-8')

            if ( not self.ignore_hash or '#' not in list(text) ):
                c = ( text, number(gram.attrib['weight']) )
                grams.append(c)

        if self.V:  # Values only.
            return grams

        return doi, grams   # Default behavior.


def _get_citation_filename(basepath):
    for fname in ["citations.xml", "citations.XML"]:
        if os.path.exists(os.path.join(basepath, fname)):
            return fname


# TODO: this seems like a waste of space.
def streaming_read(path, corpus=True, index_by='doi', parse_ngrams=['wordcount'],
         parse_only=None, **kwargs):
    return read(path, corpus, index_by, parse_ngrams, parse_only,
                corpus_class=StreamingCorpus,
                ngram_class=StreamingFeatureSet,
                streaming=True)


def read(path, corpus=True, index_by='doi', parse_ngrams=['wordcounts'],
         parse_only=None, corpus_class=Corpus, ngram_class=FeatureSet,
         streaming=True, **kwargs):
    """
    Yields :class:`.Paper` s from JSTOR DfR package.

    Each :class:`.Paper` is tagged with an accession id for this
    read/conversion.

    Parameters
    ----------
    filepath : string
        Filepath to unzipped JSTOR DfR folder containing a citations.xml file.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.

    Examples
    --------

    .. code-block:: python

       >>> from tethne.readers import dfr
       >>> papers = dfr.read("/Path/to/DfR")
    """
    # TODO: this needs a serious refactor.
    if not os.path.exists(path):
        raise ValueError('No such file or directory')

    if streaming:
        corpus_class = StreamingCorpus
        ngram_class = StreamingFeatureSet

    citationfname = _get_citation_filename(path)
    features = {}
    featureset_types = {}

    # We need the primary index field in the parse results.
    if parse_only:
        parse_only.append(index_by)

    papers = []
    if citationfname:   # Valid DfR dataset.
        parser = DfRParser(os.path.join(path, citationfname))
        papers += parser.parse(parse_only=parse_only)

    else:   # Possibly a directory containing several DfR datasets?
        papers = []

        # Search for DfR datasets in subdirectories.
        for dirpath, dirnames, filenames in os.walk(path):
            citationfname = _get_citation_filename(dirpath)
            if citationfname:
                parser = DfRParser(dirpath)
                papers += parser.parse(parse_only=parse_only)
                for featureset_name, featureset in subcorpus.features.iteritems():
                    if featureset_name not in features:
                        features[featureset_name] = {}
                    features[featureset_name].update(featureset.items())
                    featureset_types[featureset_name] = type(featureset)
        load_ngrams = False

    if len(papers) == 0:
        raise ValueError('No DfR datasets found at %s' % path)

    if corpus:
        corpus = corpus_class(papers, index_by=index_by, **kwargs)

        if len(parse_ngrams) > 0:
            for tag in parse_ngrams:
                features[tag] = ngrams(path, tag, streaming=streaming)

        for featureset_name, featureset_values in features.iteritems():
            if type(featureset_values) is dict:
                fclass = featureset_types[featureset_name]
                featureset_values = fclass(featureset_values)
            corpus.features[featureset_name] = featureset_values

        return corpus
    return papers


def ngrams(path, elem, ignore_hash=True, streaming=False):
    """
    Yields N-grams from a JSTOR DfR dataset.

    Parameters
    ----------
    path : string
        Path to unzipped JSTOR DfR folder containing N-grams.
    elem : string
        Name of subdirectory containing N-grams. (e.g. 'bigrams').
    ignore_hash : bool
        If True, will exclude all N-grams that contain the hash '#' character.

    Returns
    -------
    ngrams : :class:`.FeatureSet`

    """
    default_filter = lambda f, c, C=None, DC=None: c if '#' not in f else None
    if streaming:
        if elem.endswith('s'):
            elem = elem[:-1]
        token_filter = default_filter if ignore_hash else None
        return StreamingFeatureSet(path, StreamingParser, token_filter=token_filter, tag=elem)
    else:   # TODO: clean this up, it's pretty gross.
        grams = GramGenerator(path, elem, ignore_hash=ignore_hash)
        return FeatureSet({k: Feature(f) for k, f in grams})


def tokenize(ngrams, min_tf=2, min_df=2, min_len=3, apply_stoplist=False):
    """
    Builds a vocabulary, and replaces words with vocab indices.

    Parameters
    ----------
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.
    apply_stoplist : bool
        If True, will exclude all N-grams that contain words in the NLTK
        stoplist.

    Returns
    -------
    t_ngrams : dict
        Tokenized ngrams, as doi:{i:count}.
    vocab : dict
        Vocabulary as i:term.
    token_tf : :class:`.Counter`
        Term counts for corpus, as i:count.
    """

    vocab = {}
    vocab_ = {}
    word_tf = Counter()
    word_df = Counter()
    token_tf = Counter()
    token_df = Counter()
    t_ngrams = {}

    # Get global word counts, first.
    for grams in ngrams.values():
        for g,c in grams:
            word_tf[g] += c
            word_df[g] += 1

    if apply_stoplist:
        stoplist = stopwords.words()

    # Now tokenize.
    for doi, grams in ngrams.iteritems():
        t_ngrams[doi] = []
        for g,c in grams:
            ignore = False

            # Ignore extremely rare words (probably garbage).
            if word_tf[g] < min_tf or word_df[g] < min_df or len(g) < min_len:
                ignore = True

            # Stoplist.
            elif apply_stoplist:
                for w in g.split():
                    if w in stoplist:
                        ignore = True

            if not ignore:

                # Coerce unicode to string.
                # if type(g) is str:
                g = g.decode('utf-8')
                # g = unidecode(g)

                if g not in vocab.values():
                    i = len(vocab)
                    vocab[i] = g
                    vocab_[g] = i
                else:
                    i = vocab_[g]
                token_tf[i] += c
                token_df[i] += 1

                t_ngrams[doi].append( (i,c) )

    return t_ngrams, vocab, token_tf

def _handle_paper(article):
    """
    Yields a :class:`.Paper` from an article ET node.

    Parameters
    ----------
    article : Element
        ElementTree Element 'article'.

    Returns
    -------
    paper : :class:`.Paper`
    """
    paper = Paper()
    pdata = dict_from_node(article)

    for key, value in pdata.iteritems():

        datum = pdata[key]
        if type(datum) is str:
            datum = datum.decode('utf-8')
        if type(datum) is unicode:
            datum = datum.upper()
            # datum = unidecode(datum).upper()

        paper[key] = datum

    # Handle author names.
    adata = _handle_authors(pdata['author'])
    paper.authors_init = zip(adata[0], adata[1])

    # Handle pubdate.
    paper['date'] = _handle_pubdate(pdata['pubdate'])

    # Handle pagerange.
    paper['spage'], paper['epage'] = _handle_pagerange(pdata['pagerange'])

    return paper

def _handle_pagerange(pagerange):
    """
    Yields start and end pages from DfR pagerange field.

    Parameters
    ----------
    pagerange : str or unicode
        DfR-style pagerange, e.g. "pp. 435-444".

    Returns
    -------
    start : str
        Start page.
    end : str
        End page.
    """

    try:
        pr = re.compile("pp\.\s([0-9]+)\-([0-9]+)")
        start, end = re.findall(pr, pagerange)[0]
    except IndexError:
        start = end = 0

    return unicode(start), unicode(end)

def _handle_pubdate(pubdate):
    """
    Yields a date integer from DfR pubdate field.
    """

    return int(pubdate[0:4])

def _handle_authors(authors):
    """
    Yields aulast and auinit lists from value of authors node.

    Parameters
    ----------
    authors : list, str, or unicode
        Value or values of 'author' element in DfR XML.

    Returns
    -------
    aulast : list
        A list of author surnames (string).
    auinit : list
        A list of author first-initials (string).
    """

    aulast = []
    auinit = []
    if type(authors) is list:
        for author in authors:
            if type(author) is str:
                author = author.decode('utf-8')

            # try:
            l,i = _handle_author(author)
            aulast.append(l)
            auinit.append(i)
            # except ValueError:
            #     pass
    elif type(authors) in [str, unicode]:
        if type(authors) is str:
            authors = authors.decode('utf-8')
        # try:
        l,i = _handle_author(authors)
        aulast.append(l)
        auinit.append(i)
        # except ValueError:
        #     pass
    else:
        raise ValueError("authors must be a list or a string")

    return aulast, auinit

def _handle_author(author):
    """
    Yields aulast and auinit from an author's full name.

    Parameters
    ----------
    author : str or unicode
        Author fullname, e.g. "Richard L. Nixon".

    Returns
    -------
    aulast : str
        Author surname.
    auinit : str
        Author first-initial.
    """

    lname = author.split(' ')

    try:
        auinit = lname[0][0]
        final = lname[-1].upper()
        if final in ['JR.', 'III']:
            aulast = lname[-2].upper() + " " + final.strip(".")
        else:
            aulast = final
    except IndexError:
        raise ValueError("malformed author name")

    return aulast, auinit

def _dfr2paper_map():
    """
    Defines the direct relationships between DfR article elements and
    :class:`.Paper` fields.

    Returns
    -------
    translator : dict
        A 'translator' dictionary.
    """

    translator = {  'doi': 'doi',
                    'title': 'atitle',
                    'journaltitle': 'jtitle',
                    'volume': 'volume',
                    'issue': 'issue'    }

    return translator

def _create_ayjid(aulast=None, auinit=None, date=None, jtitle=None, **kwargs):
    """
    Convert aulast, auinit, and jtitle into the fuzzy identifier ayjid
    Returns 'Unknown paper' if all id components are missing (None).

    Parameters
    ----------
    Kwargs : dict
        A dictionary of keyword arguments.
    aulast : string
        Author surname.
    auinit: string
        Author initial(s).
    date : string
        Four-digit year.
    jtitle : string
        Title of the journal.

    Returns
    -------
    ayj : string
        Fuzzy identifier ayjid, or 'Unknown paper' if all id components are
        missing (None).

    """
    if aulast is None:
        aulast = ''
    elif isinstance(aulast, list):
        aulast = aulast[0]

    if auinit is None:
        auinit = ''
    elif isinstance(auinit, list):
        auinit = auinit[0]

    if date is None:
        date = ''

    if jtitle is None:
        jtitle = ''

    ayj = aulast + ' ' + auinit + ' ' + unicode(date) + ' ' + jtitle

    if ayj == '   ':
        ayj = 'Unknown paper'

    return ayj.upper()


def _fast_iter(context, func, tag, *extra):
    while True:
        try:
            event, elem = context.next()
        except StopIteration:
            break
        if event != "end":
            continue

        if elem.tag == tag:
            yield func(elem, *extra)
            elem.clear()
    del context


def _ngram_getter(elem):
    text = elem.text.strip()
    # Why, oh why, of why does ElementTree not yield consistent output?
    if type(text) is not unicode:
        text = text.decode('utf-8')
    return text,  float(elem.attrib['weight'])

import sys


class StreamingParser(object):
    def __init__(self, path, identifier=None, tag='wordcount'):
        self.path = path
        self.identifier = identifier
        self.tag = tag

    def __len__(self):
        return len(os.listdir(self._get_full_path(self.path, tag=self.tag)))

    def keys(self):
        path = self._get_full_path(self.path, tag=self.tag)
        return [_filename_to_identifier(fn) for fn in os.listdir(path)
                if fn.lower().endswith('.xml')]

    def _filename_to_identifier(self, filename, tag):
        return filename.replace('%ss_' % tag, '').replace('_', '/').replace('.XML', '')

    def _dataset_iterator(self, path, tag):

        fnames = os.listdir(path)
        i = 0
        while len(fnames) > 0:
            fname = fnames.pop()
            if not fname.endswith('XML'):
                continue

            identifier = self._filename_to_identifier(fname, tag)
            ident_path = os.path.join(path, fname)
            sys.stdout.flush()
            i += 1
            yield identifier, _fast_iter(ET.iterparse(ident_path), _ngram_getter, tag)

    def _identifier_iterator(self, path, identifier, tag):

        identifier = identifier.replace('/', '_')

        ident_path = os.path.join(path, '%ss_%s.XML' % (tag, identifier))
        if not os.path.exists(ident_path):
            raise KeyError('No such document')

        return _fast_iter(ET.iterparse(ident_path), _ngram_getter, tag)


    def _get_full_path(self, path, tag=None):
        tag = tag if tag else self.tag

        path = os.path.join(path, '%ss' % tag)
        if not os.path.exists(path):
            raise RuntimeError('No such path: %s' % path)
        return path


    def parse(self, path=None, identifier=None, tag='wordcount'):
        """
        Parameters
        ----------
        path : str
            Path to folder containing N-gram XML.
        identifier : str
            Identifier for a specific document. If provided, returns only the
            inner iterator.
        """
        path = path if path else self.path
        identifier = identifier if identifier else self.identifier
        tag = tag if tag else self.tag

        path = self._get_full_path(path, tag=tag)

        if identifier:
            return self._identifier_iterator(path, identifier, tag)
        return self._dataset_iterator(path, tag)
