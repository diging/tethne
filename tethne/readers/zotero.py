import os
import iso8601
import logging
import rdflib
import nltk
import codecs
import magic as magic   # To detect file mime-type.
from io import StringIO
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser
import chardet  # Detect character encodings.

import warnings
warnings.simplefilter('always', UserWarning)

from math import log
logging.basicConfig(level=40)
logging.getLogger('iso8601').setLevel(40)

from datetime import datetime

from tethne import Paper, Corpus, StructuredFeature, StructuredFeatureSet
from tethne.readers.base import RDFParser
from tethne.utilities import _strip_punctuation, mean


# RDF terms.
RDF = 'http://www.w3.org/1999/02/22-rdf-syntax-ns#'
DC = 'http://purl.org/dc/elements/1.1/'
FOAF = 'http://xmlns.com/foaf/0.1/'
PRISM = 'http://prismstandard.org/namespaces/1.2/basic/'
RSS = 'http://purl.org/rss/1.0/modules/link/'

URI_ELEM = rdflib.URIRef("http://purl.org/dc/terms/URI")
TYPE_ELEM = rdflib.term.URIRef(RDF + 'type')
VALUE_ELEM = rdflib.URIRef(RDF + 'value')
LINK_ELEM = rdflib.URIRef(RSS + "link")
FORENAME_ELEM = rdflib.URIRef(FOAF + 'givenname')
SURNAME_ELEM = rdflib.URIRef(FOAF + 'surname')
VOL = rdflib.term.URIRef(PRISM + 'volume')
IDENT = rdflib.URIRef(DC + "identifier")
TITLE = rdflib.term.URIRef(DC + 'title')


# Build a cost dictionary, assuming Zipf's law and cost = -math.log(probability).
from tethne.readers._rankedwords import WORDS
WORDCOST = dict((k, log((i+1)*log(len(WORDS)))) for i, k in enumerate(WORDS))
MAXWORD = max(len(x) for x in WORDS)

def _infer_spaces(s):
    """
    Uses dynamic programming to infer the location of spaces in a string
    without spaces.
    """
    s = s.lower()

    # Find the best match for the i first characters, assuming cost has
    # been built for the i-1 first characters.
    # Returns a pair (match_cost, match_length).
    def best_match(i):
        candidates = enumerate(reversed(cost[max(0, i - MAXWORD):i]))
        return min((c + WORDCOST.get(s[i-k-1: i], 9e999), k + 1)
                    for k, c in candidates)

    # Build the cost array.
    cost = [0]
    for i in range(1, len(s) + 1):
        c, k = best_match(i)
        cost.append(c)

    # Backtrack to recover the minimal-cost string.
    out = []
    i = len(s)
    while i > 0:
        c, k = best_match(i)
        assert c == cost[i]
        out.append(s[i-k:i])
        i -= k

    return " ".join(reversed(out))


def extract_text(fpath):
    """
    Extracts structured text content from a plain-text file at ``fpath``.

    Parameters
    ----------
    fpath : str
        Path to the text file..

    Returns
    -------
    :class:`.StructuredFeature`
        A :class:`.StructuredFeature` that contains sentence context.
    """
    with codecs.open(fpath, 'r') as f:  # Determine the encoding of the file.
        document = f.read()
    encoding = chardet.detect(document)['encoding']
    document = document.decode(encoding)

    tokens = []
    sentences = []

    i = 0
    for sentence in nltk.tokenize.sent_tokenize(document):
        sentences.append(i)

        for word in nltk.tokenize.word_tokenize(sentence):
            tokens.append(word)
            i += 1

    contexts = [('sentence', sentences)]
    return StructuredFeature(tokens, contexts)


def extract_pdf(fpath):
    """
    Extracts structured text content from a PDF at ``fpath``.

    Parameters
    ----------
    fpath : str
        Path to the PDF.

    Returns
    -------
    :class:`.StructuredFeature`
        A :class:`.StructuredFeature` that contains page and sentence contexts.
    """

    tokens = []
    pages = []
    sentences = []

    with open(fpath, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        tokenizer = nltk.tokenize.TextTilingTokenizer()

        i = 0
        for page in PDFPage.create_pages(doc):
            pages.append(i)
            
            # PDFMiner for parsing the page
            output_string = StringIO()
            device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            interpreter.process_page(page)
            output = output_string.getvalue()
            
            # `output` --> extracted text for the `page`

            for sentence in nltk.tokenize.sent_tokenize(output):
                sentences.append(i)

                for word in nltk.tokenize.word_tokenize(sentence):
                    if len(word) > 15:
                        words = nltk.tokenize.word_tokenize(_infer_spaces(word))
                        if mean([len(w) for w in words]) > 2:
                            for w in words:
                                tokens.append(w)
                                i += 1
                            continue

                    tokens.append(word)
                    i += 1     

    contexts = [('page', pages), ('sentence', sentences)]
    return StructuredFeature(tokens, contexts)


class ZoteroParser(RDFParser):
    """
    Reads Zotero RDF files.
    """

    entry_class = Paper
    entry_elements = ['bib:Illustration', 'bib:Recording', 'bib:Legislation',
                      'bib:Document', 'bib:BookSection', 'bib:Book', 'bib:Data',
                      'bib:Letter', 'bib:Report', 'bib:Article',
                      'bib:Manuscript', 'bib:Image',
                      'bib:ConferenceProceedings', 'bib:Thesis']
    tags = {
        'isPartOf': 'journal'
    }

    meta_elements = [
        ('date', rdflib.URIRef("http://purl.org/dc/elements/1.1/date")),
        ('identifier',
         rdflib.URIRef("http://purl.org/dc/elements/1.1/identifier")),
        ('abstract', rdflib.URIRef("http://purl.org/dc/terms/abstract")),
        ('authors_full', rdflib.URIRef("http://purl.org/net/biblio#authors")),
        ('link', rdflib.URIRef("http://purl.org/rss/1.0/modules/link/link")),
        ('title', rdflib.URIRef("http://purl.org/dc/elements/1.1/title")),
        ('isPartOf', rdflib.URIRef("http://purl.org/dc/terms/isPartOf")),
        ('pages', rdflib.URIRef("http://purl.org/net/biblio#pages")),
        ('documentType',
         rdflib.URIRef("http://www.zotero.org/namespaces/export#itemType"))]

    def __init__(self, path, **kwargs):
        if os.path.isdir(path):    # Preserve the old behavior.
            name = os.path.split(path)[1]
            path = os.path.join(path, '{0}.rdf'.format(name))

        super(ZoteroParser, self).__init__(path, **kwargs)

        self.full_text = {}     # Collect StructuredFeatures until finished.
        self.follow_links = kwargs.get('follow_links', False) # Boolean switch to follow links associated with a paper

    def open(self):
        """
        Fixes RDF validation issues. Zotero incorrectly uses ``rdf:resource`` as
        a child element for Attribute; ``rdf:resource`` should instead be used
        as an attribute of ``link:link``.
        """

        with open(self.path, 'r') as f:
            corrected = f.read().replace('rdf:resource rdf:resource',
                                         'link:link rdf:resource')
        with open(self.path, 'w') as f:
            f.write(corrected)

        super(ZoteroParser, self).open()

    def handle_identifier(self, value):
        """

        """

        identifier = str(self.graph.value(subject=value, predicate=VALUE_ELEM))
        ident_type = self.graph.value(subject=value, predicate=TYPE_ELEM)
        if ident_type == URI_ELEM:
            self.set_value('uri', identifier)


    def handle_link(self, value):
        """
        rdf:link rdf:resource points to the resource described by a record.
        """
        for s, p, o in self.graph.triples((value, None, None)):
            if p == LINK_ELEM:
                return str(o).replace('file://', '')

    def handle_date(self, value):
        """
        Attempt to coerced date to ISO8601.
        """
        try:
            return iso8601.parse_date(str(value)).year
        except iso8601.ParseError:
            for datefmt in ("%B %d, %Y", "%Y-%m", "%Y-%m-%d", "%m/%d/%Y"):
                try:
                    # TODO: remove str coercion.
                    return datetime.strptime(str(value), datefmt).date().year
                except ValueError:
                    pass

    def handle_documentType(self, value):
        """

        Parameters
        ----------
        value

        Returns
        -------
        value.toPython()
        Basically, RDF literals are casted to their corresponding Python data types.
        """
        return value.toPython()

    def handle_authors_full(self, value):
        authors = [self.handle_author(o) for s, p, o
                   in self.graph.triples((value, None, None))]
        return [a for a in authors if a is not None]

    def handle_abstract(self, value):
        """
        Abstract handler.

        Parameters
        ----------
        value

        Returns
        -------
        abstract.toPython()
        Basically, RDF literals are casted to their corresponding Python data types.
        """
        return value.toPython()

    def handle_title(self, value):
        """
        Title handler
        Parameters
        ----------
        value

        Returns
        -------
        title.toPython()

        """
        return value.toPython()


    def handle_author(self, value):
        forename_iter = self.graph.triples((value, FORENAME_ELEM, None))
        surname_iter = self.graph.triples((value, SURNAME_ELEM, None))
        norm = lambda s: str(s).upper().replace('.', '')

        # TODO: DRY this out.
        try:
            forename = norm([e[2] for e in forename_iter][0])
        except IndexError:
            forename = ''

        try:
            surname = norm([e[2] for e in surname_iter][0])
        except IndexError:
            surname = ''

        if surname == '' and forename == '':
            return
        return surname, forename

    def handle_isPartOf(self, value):
        journal = None
        for s, p, o in self.graph.triples((value, None, None)):

            if p == VOL:        # Volume number
                self.set_value('volume', str(o))
            elif p == TITLE:
                journal = str(o)    # Journal title.
        return journal

    def handle_pages(self, value):
        return tuple(value.split('-'))

    def postprocess_pages(self, entry):
        if len(entry.pages) < 2:
            start, end = entry.pages, None
        else:
            try:
                start, end = entry.pages
            except ValueError:
                start, end = entry.pages, None

        setattr(entry, 'pageStart', start)
        setattr(entry, 'pageEnd', end)
        del entry.pages

    def postprocess_link(self, entry):
        """
        Attempt to load full-text content from resource.
        """

        if not self.follow_links:
            return

        if type(entry.link) is not list:
            entry.link = [entry.link]

        for link in list(entry.link):
            if not os.path.exists(link):
                continue

            mime_type = magic.from_file(link, mime=True)
            if mime_type == 'application/pdf':
                structuredfeature = extract_pdf(link)
            elif mime_type == 'text/plain':
                structuredfeature = extract_text(link)
            else:
                structuredfeature = None

            if not structuredfeature:
                continue

            fset_name = mime_type.split('/')[-1] + '_text'
            if not fset_name in self.full_text:
                self.full_text[fset_name] = {}

            if hasattr(self, 'index_by'):
                ident = getattr(entry, self.index_by)
                if type(ident) is list:
                    ident = ident[0]
            else:   # If `index_by` is not set, use `uri` by default.
                ident = entry.uri

            self.full_text[fset_name][ident] = structuredfeature


def read(path, corpus=True, index_by='uri', follow_links=False, **kwargs):
    """
    Read bibliographic data from Zotero RDF.

    Examples
    --------
    Assuming that the Zotero collection was exported to the directory
    ``/my/working/dir`` with the name ``myCollection``, a subdirectory should
    have been created at ``/my/working/dir/myCollection``, and an RDF file
    should exist at ``/my/working/dir/myCollection/myCollection.rdf``.

    .. code-block:: python

       >>> from tethne.readers.zotero import read
       >>> myCorpus = read('/my/working/dir/myCollection')
       >>> myCorpus
       <tethne.classes.corpus.Corpus object at 0x10047e350>


    Parameters
    ----------
    path : str
        Path to the output directory created by Zotero. Expected to contain a
        file called ``[directory_name].rdf``.
    corpus : bool
        (default: True) If True, returns a :class:`.Corpus`\. Otherwise,
        returns a list of :class:`.Paper`\s.
    index_by : str
        (default: ``'identifier'``) :class:`.Paper` attribute name to use as
        the primary indexing field. If the field is missing on a
        :class:`.Paper`\, a unique identifier will be generated based on the
        title and author names.
    follow_links : bool
        If ``True``, attempts to load full-text content from attached files
        (e.g. PDFs with embedded text). Default: False.
    kwargs : kwargs
        Passed to the :class:`.Corpus` constructor.

    Returns
    -------
    corpus : :class:`.Corpus`
    """
    # TODO: is there a case where `from_dir` would make sense?

    parser = ZoteroParser(path, index_by=index_by, follow_links=follow_links)
    papers = parser.parse()

    if corpus:
        c = Corpus(papers, index_by=index_by, **kwargs)
        if c.duplicate_papers:
            warnings.warn("Duplicate papers detected. Use the 'duplicate_papers' attribute of the corpus to get the list", UserWarning)

        for fset_name, fset_values in parser.full_text.items():
            c.features[fset_name] = StructuredFeatureSet(fset_values)
        return c
    return papers
