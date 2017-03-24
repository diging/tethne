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

import re, os
from collections import defaultdict

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
        'D2': 'doi',
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

        Parameters
        ----------
        value : str

        Returns
        -------
        tuple
            Returns (aulast, auinit) 2-tuple.
        """
        tokens = tuple([t.upper().strip() for t in value.split(',')])
        if len(tokens) == 1:
            tokens = value.split(' ')
        if len(tokens) > 0:
            if len(tokens) > 1:
                aulast, auinit = tokens[0:2]    # Ignore JR, II, III, etc.
            else:
                tokens = tokens[0].split('.')
                if len(tokens) > 1:
                    aulast, auinit = tokens[0:2]
                else:
                    aulast = tokens[0]
                    auinit = ''
        else:
            aulast, auinit = tokens[0], ''
        aulast = _strip_punctuation(aulast).upper()
        auinit = _strip_punctuation(auinit).upper()
        return aulast, auinit

    def handle_AF(self, value):
        """
        Split an author name into last and first parts.

        Parameters
        ----------
        value : str

        Returns
        -------
        tuple
            Returns (aulast, auinit) 2-tuple.
        """
        return self.parse_author(value)

    def handle_PY(self, value):
        """
        WoS publication years are cast to integers.

        Parameters
        ----------
        value : str

        Returns
        -------
        int
        """
        return int(value)

    def handle_AU(self, value):
        """
        Sepearte author initials with spaces.

        Parameters
        ----------
        value : str

        Returns
        -------
        tuple
            Returns (aulast, auinit) 2-tuple.
        """
        aulast, auinit = self.parse_author(value)
        auinit = _space_sep(auinit)   # Separate author initials with spaces.
        return aulast, auinit

    def handle_TI(self, value):
        """
        Convert article's title to Title Case.

        Parameters
        ----------
        value : str

        Returns
        -------
        str
        """
        return unicode(value).title()

    def handle_VL(self, value):
        """
        Volume should be a unicode string, even if it looks like an integer.

        Parameters
        ----------
        value : str

        Returns
        -------
        str
            Unicode string representation of ``value``.
        """
        return unicode(value)

    def handle_CR(self, value):
        """
        Parses cited references.

        Parameters
        ----------
        value : str

        Returns
        -------
        :class:.`Paper`.
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

    def postprocess_WC(self, entry):
        """
        Parse WC keywords and update ``entry.WC``.

        Subject keywords are usually semicolon-delimited.

        Parameters
        ----------
        entry : :class:.`Paper`
        """

        if type(entry.WC) not in [str, unicode]:
            WC= u' '.join([unicode(k) for k in entry.WC])
        else:
            WC= entry.WC
        entry.WC= [k.strip().upper() for k in WC.split(';')]

    def postprocess_subject(self, entry):
        """
        Parse subject keywords and update ``entry.subject``.

        Subject keywords are usually semicolon-delimited.

        Parameters
        ----------
        entry : :class:.`Paper`
        """

        if type(entry.subject) not in [str, unicode]:
            subject = u' '.join([unicode(k) for k in entry.subject])
        else:
            subject = entry.subject
        entry.subject = [k.strip().upper() for k in subject.split(';')]

    def postprocess_authorAddress(self, entry):
        """
        Parses ``authorAddress`` field into ``entry.addresses``.

        :attr:`.Paper.addresses` will be a ``dict`` mapping author name-tuples
        (e.g. ``(u'PEROT', u'R')``) onto a list of (institution, country,
        [address, parts]) tuples. If it is not possible to determine an
        explicit mapping, then there will be only one key, ``__all__`` with a
        list of all (parsed) addresses in the record.

        Parameters
        ----------
        entry : :class:.`Paper`

        Examples
        --------

        .. code-block:: python

           >>> corpus[0].addresses
           {
                '__all__': [
                    (
                        u'CTR OCEANOG MURCIA',
                        u'SPAIN',
                        [u'Ctr Oceanog Murcia', u'Inst Espanol Oceanog', u'Murcia 30740', u'Spain.']
                    )
                ]
            }


        .. code-block:: python

           >>> corpus[0].addresses
           {
                (u'KLEINDIENST', u'SARA'): [
                    (
                        u'UNIV GEORGIA',
                        u'USA',
                        [u'Univ Georgia', u'Dept Marine Sci', u'Athens', u'GA 30602 USA.']
                    )
                ],
                (u'PAUL', u'JOHN H'): [
                    (
                        u'UNIV S FLORIDA',
                        u'USA',
                        [u'Univ S Florida', u'Coll Marine Sci', u'St Petersburg', u'FL 33701 USA.']
                    )
                ], (u'JOYE', u'SAMANTHA B'): [
                    (
                        u'UNIV GEORGIA',
                        u'USA',
                        [u'Univ Georgia', u'Dept Marine Sci', u'Athens', u'GA 30602 USA.']
                    )
                ]
            }

        """
        if not hasattr(entry, 'authorAddress'):
            return

        if not type(entry.authorAddress) is list:
            entry.authorAddress = [entry.authorAddress.strip()]

        _clean = lambda s: s.strip().upper().replace('.', '')

        def _process_address(address_part):
            address_parts = address_part.split(',')

            # The insitution --usually-- comes first.
            institution = _clean(address_parts[0])

            # The country --usually-- comes last.
            country = _clean(address_parts[-1])

            # USA addresses usually include the state, zip code, and country,
            usa_match = re.match('[A-Z]{2}\s+[0-9]{5}\s+(USA)', country)
            #  or sometimes just the state and country.
            usa_match_state = re.match('[A-Z]{2}\s+(USA)', country)
            if usa_match:
                country, = usa_match.groups()
            elif usa_match_state:
                country, = usa_match_state.groups()

            return institution, country, [a.strip() for a in address_parts]

        # We won't assume that there is only one address per author.
        addresses_final = defaultdict(list)
        # for addr in addresses + addresses_2:
        for addr in entry.authorAddress:
            # More recent WoS records have explicit author-address mappings.
            match = re.match('[[](.+)[]](.+)', addr)
            if match:
                name_part, address_part = match.groups()
                name_parts = [name.split(',') for name in name_part.split(';')]
                names = []
                for part in name_parts:
                    # We may encounter non-human names, or names that don't
                    #  follow western fore/surnmae conventions.
                    if len(part) == 2:
                        surname = _clean(part[0])
                        forename = _clean(part[1])
                        names.append((surname, forename))

                institution, country, address_parts = _process_address(address_part)
                for name in names:
                    addresses_final[name].append((institution, country, address_parts))
            else:
                addresses_final['__all__'].append(_process_address(addr))
        entry.addresses = dict(addresses_final)    # Keep it native.

    def postprocess_authorKeywords(self, entry):
        """
        Parse author keywords and update ``entry.authorKeywords``.

        Author keywords are usually semicolon-delimited.

        Parameters
        ----------
        entry : :class:.`Paper`
        """

        if type(entry.authorKeywords) not in [str, unicode]:
            aK = u' '.join([unicode(k) for k in entry.authorKeywords])
        else:
            aK = entry.authorKeywords
        entry.authorKeywords = [k.strip().upper() for k in aK.split(';')]

    def postprocess_keywordsPlus(self, entry):
        """
        Parse WoS "Keyword Plus" keywords and update ``entry.keywordsPlus``.

        Keyword Plus keywords are usually semicolon-delimited.

        Parameters
        ----------
        entry : :class:.`Paper`
        """

        if type(entry.keywordsPlus) in [str, unicode]:
            entry.keywordsPlus = [k.strip().upper() for k
                                  in entry.keywordsPlus.split(';')]

    def postprocess_funding(self, entry):
        """
        Separates funding agency from grant numbers and stores the same as a
        (agency, grant) 2-tuple in ``entry.funding`` list.

        Parameters
        ----------
        entry : :class:.`Paper`
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
        If only a single author was found, ensure that ``entity.authors_full``
        is nonetheless a list.

        Parameters
        ----------
        entry : :class:.`Paper`
        """
        if type(entry.authors_full) is not list:
            entry.authors_full = [entry.authors_full]

    def postprocess_authors_init(self, entry):
        """
        If only a single author was found, ensure that ``entity.authors_init`` is
        nonetheless a list.

        Parameters
        ----------
        entry : :class:.`Paper`
        """
        if type(entry.authors_init) is not list:
            entry.authors_init = [entry.authors_init]

    def postprocess_citedReferences(self, entry):
        """
        If only a single cited reference was found, ensure that
        ``entry.citedReferences`` is nonetheless a list.

        Parameters
        ----------
        entry : :class:.`Paper`
        """

        if type(entry.citedReferences) is not list:
            if not entry.citedReferences:
                entry.citedReferences = []
            else:
                entry.citedReferences = [entry.citedReferences]
        entry.citedReferences = [cr for cr in entry.citedReferences if cr]


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


def read(path, corpus=True, index_by='wosid', streaming=False, parse_only=None,
         corpus_class=Corpus, **kwargs):
    """
    Parse one or more WoS field-tagged data files.

    Examples
    --------
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
        (default: True) If True, returns a :class:`.Corpus`\. If False, will
        return only a list of :class:`.Paper`\s.
    index_by : str
        (default: 'wosid') Controls which field is used for indexing.
    streaming : bool
        (default: False) If True, returns a :class:`.StreamingCorpus`\.
    parse_only : iterable
        (default: None) Parse only the specified fields. If None, all fields
        are parsed and processed.

    Returns
    -------
    :class:`.Corpus` or :class:`.Paper` or :class:`.StreamingCorpus`
    """

    if not os.path.exists(path):
        raise ValueError('No such file or directory')

    # We need the primary index field in the parse results.
    if parse_only:
        parse_only.append(index_by)

    if streaming:
        return streaming_read(path, corpus=corpus, index_by=index_by,
                              parse_only=parse_only, **kwargs)

    if os.path.isdir(path):    # Directory containing 1+ WoS data files.
        papers = []
        for sname in os.listdir(path):
            if sname.endswith('txt') and not sname.startswith('.'):
                papers += read(os.path.join(path, sname),
                               corpus=False,
                               parse_only=parse_only)
    else:   # A single data file.
        papers = WoSParser(path).parse(parse_only=parse_only)

    if corpus:
        return corpus_class(papers, index_by=index_by, **kwargs)
    return papers


def streaming_read(path, corpus=True, index_by='wosid', parse_only=None,
                   **kwargs):
    """
    Use memory-friendly :class:.`StreamingCorpus` while reading the dataset.
    For parameter description, refer to :meth:.`read`.
    """
    return read(path, corpus=corpus, index_by=index_by, parse_only=parse_only,
                corpus_class=StreamingCorpus, **kwargs)
    # corpus = StreamingCorpus(index_by=index_by, **kwargs)

    # if os.path.isdir(path):    # Directory containing 1+ WoS data files.
    #     papers = []
    #     for sname in os.listdir(path):
    #         if sname.endswith('txt') and not sname.startswith('.'):
    #             corpus.add_papers(read(os.path.join(path, sname),
    #                                    corpus=False,
    #                                    parse_only=parse_only))
    # else:   # A single data file.
    #     corpus.add_papers(WoSParser(path).parse(parse_only=parse_only))
    #
    # return corpus
