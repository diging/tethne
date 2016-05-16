"""
Parser for Web of Science field-tagged bibliographic data.

Tethne parsers Web of Science field-tagged data into a set of
:class:`.Paper`\s, which are then encapsulated in a :class:`.Corpus`\. The
:class:`.WoSParser` can be instantiated directly, or you can simply use
:func:`.read` to parse a single file or a directory containing several data
files.

.. code-block:: python

   >>> from tethne.readers import wos
   >>> corpus = wos.read("/path/to/some/wos/data")
   >>> corpus
   <tethne.classes.corpus.Corpus object at 0x10057c2d0>

"""

import re
import os

from tethne.readers.base import FTParser
from tethne import Corpus, Paper, StreamingCorpus
from tethne.utilities import _strip_punctuation, _space_sep, strip_tags, is_number

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str


class WoSParser(FTParser):
    """
    Parser for Web of Science field-tagged data.

    .. code-block:: python

       >>> from tethne.readers.wos import WoSParser
       >>> parser = WoSParser("/path/to/download.txt")
       >>> papers = parser.read()

    """

    start_tag = 'PT'
    """
    Field-tag used to mark the start of a record.
    """

    end_tag = 'ER'
    """
    Field-tag used to mark the end of a record.
    """

    concat_fields = ['abstract', 'keywords', 'funding', 'title', 'references',
                     'journal']
    """
    Fields that span multiple lines that should be concatenated into a single
    value.
    """

    entry_class = Paper
    """
    The class that should be used to represent a single bibliographic record.
    This can be changed to support more sophisticated data models.
    """

    tags = {
        'PY': 'date',
        'SO': 'journal',
        'AB': 'abstract',
        'TI': 'title',
        'AF': 'authors_full',
        'AU': 'authors_init',
        'ID': 'authorKeywords',
        'DE': 'keywordsPlus',
        'DI': 'doi',
        'BP': 'pageStart',
        'EP': 'pageEnd',
        'VL': 'volume',
        'IS': 'issue',
        'CR': 'citedReferences',
        'DT': 'documentType',
        'CA': 'groupAuthors',
        'ED': 'editors',
        'SE': 'bookSeriesTitle',
        'BS': 'bookSeriesSubtitle',
        'LA': 'language',
        'DT': 'documentType',
        'CT': 'conferenceTitle',
        'CY': 'conferenceDate',
        'HO': 'conferenceHost',
        'CL': 'conferenceLocation',
        'SP': 'conferenceSponsors',
        'C1': 'authorAddress',
        'RP': 'reprintAddress',
        'EM': 'emailAddress',
        'FU': 'funding',
        'NR': 'citationCount',
        'TC': 'timesCited',
        'PU': 'publisher',
        'PI': 'publisherCity',
        'PA': 'publisherAddress',
        'SC': 'subject',
        'SN': 'ISSN',
        'BN': 'ISSN',
        'UT': 'wosid',
        'JI': 'isoSource',
    }
    """
    Maps field-tags onto field names.
    """

    def parse_author(self, value):
        """
        Attempts to split an author name into last and first parts.
        """
        tokens = tuple([t.upper().strip() for t in value.split(',')])
        if len(tokens) == 1:
            tokens = value.split(' ')
        if len(tokens) > 0:
            if len(tokens) > 1:
                aulast, auinit = tokens[0:2]    # Ignore JR, II, III, etc.
            else:
                aulast = tokens[0]
                auinit = ''
        else:
            aulast, auinit = tokens[0], ''
        aulast = _strip_punctuation(aulast).upper()
        auinit = _strip_punctuation(auinit).upper()
        return aulast, auinit

    def handle_AF(self, value):
        return self.parse_author(value)

    def handle_PY(self, value):
        """
        WoS publication years are cast to integers.
        """
        return int(value)

    def handle_AU(self, value):
        aulast, auinit = self.parse_author(value)
        auinit = _space_sep(auinit)   # Separate author initials with spaces.
        return aulast, auinit

    def handle_TI(self, value):
        """
        Convert article titles to Title Case.
        """
        return unicode(value).title()

    def handle_VL(self, value):
        """
        Volume should be a unicode string, even if it looks like an integer.
        """
        return unicode(value)

    def handle_CR(self, value):
        """
        Parses cited references.
        """
        citation = self.entry_class()

        value = strip_tags(value)

        # First-author name and publication date.
        ptn = '([\w\s\W]+),\s([0-9]{4}),\s([\w\s]+)'
        ny_match = re.match(ptn, value, flags=re.U)
        nj_match = re.match('([\w\s\W]+),\s([\w\s]+)',
                            value, flags=re.U)
        if ny_match is not None:
            name_raw, date, journal = ny_match.groups()
        elif nj_match is not None:
            name_raw, journal = nj_match.groups()
            date = None
        else:
            return

        datematch = re.match('([0-9]{4})', value)
        if datematch:
            date = datematch.group(1)
            name_raw = None

        if name_raw:
            name_tokens = [t.replace('.', '') for t in name_raw.split(' ')]
            if len(name_tokens) > 4 or value.startswith('*'):    # Probably not a person.
                proc = lambda x: _strip_punctuation(x)
                aulast = ' '.join([proc(n) for n in name_tokens]).upper()
                auinit = ''
            elif len(name_tokens) > 0:
                aulast = name_tokens[0].upper()
                proc = lambda x: _space_sep(_strip_punctuation(x))
                auinit = ' '.join([proc(n) for n in name_tokens[1:]]).upper()
            else:
                aulast = name_tokens[0].upper()
                auinit = ''

            setattr(citation, 'authors_init', [(aulast, auinit)])

        if date:
            date = int(date)
        setattr(citation, 'date', date)
        setattr(citation, 'journal', journal)

        # Volume.
        v_match = re.search('\,\s+V([0-9A-Za-z]+)', value)
        if v_match is not None:
            volume = v_match.group(1)
        else:
            volume = None
        setattr(citation, 'volume', volume)

        # Start page.
        p_match = re.search('\,\s+[Pp]([0-9A-Za-z]+)', value)
        if p_match is not None:
            page = p_match.group(1)
        else:
            page = None
        setattr(citation, 'pageStart', page)

        # DOI.
        doi_match = re.search('DOI\s(.*)', value)
        if doi_match is not None:
            doi = doi_match.group(1)
        else:
            doi = None
        setattr(citation, 'doi', doi)
        return citation

    def postprocess_authorKeywords(self, entry):
        """
        Parse author keywords.

        Author keywords are usually semicolon-delimited.
        """

        if type(entry.authorKeywords) not in [str, unicode]:
            aK = u' '.join([unicode(k) for k in entry.authorKeywords])
        else:
            aK = entry.authorKeywords
        entry.authorKeywords = [k.strip().upper() for k in aK.split(';')]

    def postprocess_keywordsPlus(self, entry):
        """
        Parse WoS "Keyword Plus" keywords.

        Keyword Plus keywords are usually semicolon-delimited.
        """

        if type(entry.keywordsPlus) in [str, unicode]:
            entry.keywordsPlus = [k.strip().upper() for k
                                  in entry.keywordsPlus.split(';')]

    def postprocess_funding(self, entry):
        """
        Separates funding agency from grant numbers.
        """

        if type(entry.funding) not in [str, unicode]:
            return

        sources = [fu.strip() for fu in entry.funding.split(';')]
        sources_processed = []
        for source in sources:
            m = re.search('(.*)?\s+\[(.+)\]', source)
            if m:
                agency, grant = m.groups()
            else:
                agency, grant = source, None
            sources_processed.append((agency, grant))
        entry.funding = sources_processed

    def postprocess_authors_full(self, entry):
        """
        If only a single author was found, ensure that ``authors_full`` is
        nonetheless a list.
        """
        if type(entry.authors_full) is not list:
            entry.authors_full = [entry.authors_full]

    def postprocess_authors_init(self, entry):
        """
        If only a single author was found, ensure that ``authors_init`` is
        nonetheless a list.
        """
        if type(entry.authors_init) is not list:
            entry.authors_init = [entry.authors_init]

    def postprocess_citedReferences(self, entry):
        """
        If only a single cited reference was found, ensure that
        ``citedReferences`` is nonetheless a list.
        """
        if type(entry.citedReferences) is not list:
            entry.citedReferences = [entry.citedReferences]


def from_dir(path, corpus=True, **kwargs):
    raise DeprecationWarning("from_dir() is deprecated. Use read() instead.")
    papers = []
    for sname in os.listdir(path):
        if sname.endswith('txt') and not sname.startswith('.'):
            papers += read(os.path.join(path, sname), corpus=False)
    if corpus:
        return Corpus(papers, **kwargs)
    return papers


def corpus_from_dir(path, **kwargs):
    raise DeprecationWarning("corpus_from_dir is deprecated in v0.8, use" +
                             " read directly, instead.")
    return read(path, corpus=True, **kwargs)


def read_corpus(path, **kwargs):
    """
    .. DANGER::
       read_corpus is deprecated in v0.8, use :func:`.read` instead.
    """
    raise DeprecationWarning("read_corpus is deprecated in v0.8, use" +
                             " read directly, instead.")
    return read(path, corpus=True, **kwargs)


def read(path, corpus=True, index_by='wosid', streaming=False, **kwargs):
    """
    Parse one or more WoS field-tagged data files.

    Example
    -------
    .. code-block:: python

       >>> from tethne.readers import wos
       >>> corpus = wos.read("/path/to/some/wos/data")
       >>> corpus
       <tethne.classes.corpus.Corpus object at 0x10057c2d0>

    Parameters
    ----------
    path : str
        Path to WoS field-tagged data. Can be a path directly to a single data
        file, or to a directory containing several data files.
    corpus : bool
        If True (default), returns a :class:`.Corpus`\. If False, will return
        only a list of :class:`.Paper`\s.

    Returns
    -------
    :class:`.Corpus` or :class:`.Paper`
    """

    if not os.path.exists(path):
        raise ValueError('No such file or directory')

    if streaming:
        return streaming_read(path, corpus=corpus, index_by=index_by, **kwargs)

    if os.path.isdir(path):    # Directory containing 1+ WoS data files.
        papers = []
        for sname in os.listdir(path):
            if sname.endswith('txt') and not sname.startswith('.'):
                papers += read(os.path.join(path, sname), corpus=False)
    else:   # A single data file.
        papers = WoSParser(path).parse()

    if corpus:
        return Corpus(papers, index_by=index_by,  **kwargs)
    return papers


def streaming_read(path, corpus=True, index_by='wosid', **kwargs):

    corpus = StreamingCorpus(index_by=index_by, **kwargs)

    if os.path.isdir(path):    # Directory containing 1+ WoS data files.
        papers = []
        for sname in os.listdir(path):
            if sname.endswith('txt') and not sname.startswith('.'):
                corpus.add_papers(read(os.path.join(path, sname), corpus=False))
    else:   # A single data file.
        corpus.add_papers(WoSParser(path).parse())

    return corpus
