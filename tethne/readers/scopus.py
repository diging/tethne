"""
Reader for Scopus CSV data files.
"""

import csv
import re
import os
import uuid

from unidecode import unidecode

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str
    xrange = range

from tethne import Paper, Corpus

def read_corpus(path):
    """

    """

    papers = read(path)
    return Corpus(papers, index_by='eid')

def corpus_from_dir(path):
    """

    Parameters
    ----------
    path : string
        Path to directory of Scopus CSV data files.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.
    """

    papers = from_dir(path)
    return Corpus(papers, index_by='eid')

def from_dir(path):
    """
    Convenience function for generating a list of :class:`.Paper` from a
    directory of Scopus CSV data files.

    Parameters
    ----------
    path : string
        Path to directory of Scopus CSV data files.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.

    Raises
    ------
    IOError
        Invalid path.

    Examples
    --------

    .. code-block:: python

       >>> from  tethne.readers as rd
       >>> papers = rd.scopus.from_dir("/Path/to/datadir")

    """

    papers = []

    try:
        files = os.listdir(path)
    except IOError:
        raise IOError("Invalid path.")

    for f in files:
        if not f.startswith('.') and f.endswith('csv'): # Ignore hidden files.
            try:
                papers += read('{0}/{1}'.format(path, f))
            except (IOError,UnboundLocalError): # Ignore files that don't
                pass                            #  contain Scopus data.

    return papers

def read(datapath, **kwargs):
    """
    Yields a list of :class:`.Paper` instances from a Scopus CSV data file.

    Parameters
    ----------
    datapath : string
        Filepath to the Web of Science field-tagged data file.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` instances.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.scopus.read("/Path/to/scopus.csv")

    """

    accession = unicode(uuid.uuid4())   # Accession ID.

    papers = kwargs.get('papers', [])   # Can provide an alternate container.

    rawdata = []
    with open(datapath, 'rb') as f:
        reader = csv.reader(f)
        for row in reader:
            rawdata.append([ unidecode(r.decode('UTF-8')) for r in row ])

    headers = rawdata[0]    # First row is header.
    for datum in rawdata[1:]:
        p = Paper()

        rawdatum = { headers[i]:datum[i] for i in xrange(len(headers)) }
        p['aulast'], p['auinit'] = _handle_authors( rawdatum['Authors'] )
        p['date'] = int(rawdatum['Year'].strip())
        p['ayjid'] = _create_ayjid(
                        p['aulast'], p['auinit'], p['date'], p['jtitle'])

        p['institutions'] = _handle_affiliations(
                rawdatum['Authors with affiliations'], p['aulast'], p['auinit'])
        p['atitle'] = rawdatum['Title'].strip().upper()
        p['jtitle'] = rawdatum['Source title'].strip().upper()
        p['volume'] = rawdatum['Volume'].strip()
        p['issue'] = rawdatum['Issue'].strip()
        p['spage'] = rawdatum['Page start'].strip()
        p['epage'] = rawdatum['Page end'].strip()

        p['abstract'] = rawdatum['Abstract'].strip().upper()
        p['citations'] = _handle_references(rawdatum['References'])
        p['accession'] = accession

        # DOI and PMID are not always present, but must be unique. If they are
        #  not provided, should be set to None so that they can be handled
        #  appropriately downstream. EID should always be present.
        doi = rawdatum['DOI'].strip()
        if doi == '': doi = None
        p['doi'] = doi
        pmid = rawdatum['PubMed ID'].strip()
        if pmid == '': pmid = None
        p['pmid'] = pmid
        p['eid'] = rawdatum['EID'].strip()

        papers.append(p)

    return papers

def _handle_authors(authordata):
    aulast = []
    auinit = []

    for author in authordata.split(', '):
        try:
            a = [a_.strip().upper().replace('.','') for a_ in author.split()]
            aulast.append(' '.join(a[0:-1]))
            auinit.append(a[-1])
        except IndexError:  # Empty record; stray delimiter.
            pass

    return aulast, auinit

def _handle_affiliations(affiliationsdata, aulast, auinit):
    def matching_author(last, init, instcleaned):
        au_parts = [last, init]
        matching = 0
        for x in xrange(len(au_parts)):
            if au_parts[x] == instcleaned[x]:
                matching += 1
        if matching > 1:
            return True, matching
        return False, 0

    institutions = {}

    aff_split = affiliationsdata.split(';')
    A = len(aff_split)
    for i in xrange(A):
        aff = aff_split[i]
        a = aff.split(', ')

        try:
            cleaned = [ a_.strip().upper().replace('.','') for a_ in a ]

            # First work on the assumption that affiliations are in the same
            #  order as author names.
            aul = aulast[i]
            aui = auinit[i]
            match, overlap = matching_author(aul, aui, cleaned)
            if match:
                aname = ' '.join([aul, aui])

            # That might not always be true, so we'll try the other authors
            #  just in case.
            else:
                found = False
                for x in xrange(len(aulast)):
                    aul = aulast[x]
                    aui = auinit[x]

                    match, overlap = matching_author(aul, aui, cleaned)
                    if match:
                        aname = ' '.join([aul, aui])
                        found = True
                        break
                if not found:   # If the author can't be identified, discard.
                    break

            institution = a[match+1:] # The remainder is the institution name.
            l = len(institution)

            if l == 0:
                continue
            if l == 1:
                nation = institution[0].split()[-1].upper()
                inst = ' '.join(institution[0].split()[0:-1]).upper()
            elif l == 2:
                nation = institution[1].upper()
                inst = institution[0].upper()
            else:
                nation = institution[-1].upper()
                inst = ', '.join(institution[0:2]).upper()

            institutions[aname] = [', '.join([inst, nation])]
        except IndexError:  # Blank record part (stray delimiter).
            pass

    # inst_list should be a list of lists, ordered by aulast/auinit.
    authors = [ ' '.join(a) for a in zip(aulast, auinit) ]  # To use as keys.
    inst_list = []
    for au in authors:
        if au in institutions:      # Data available.
            inst_list.append(institutions[au])
        else:
            inst_list.append([])    # No data for that author.

    return inst_list

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
    if aulast is None or len(aulast) == 0:
        aulast = ''
    elif isinstance(aulast, list):
        aulast = aulast[0]

    if auinit is None or len(auinit) == 0:
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

def _handle_references(referencesdata):
    """
    Use a series of RegEx patterns to (roughly) parse references into
    :class:`.Paper` objects.
    """

    references = [] # A list of Papers.

    for r in referencesdata.strip().split(';'): # Each cited reference.

        # Split at date first, e.g. ' ... (1995) ... '
        m = re.search('(.*)\((?P<date>[0-9]{4})\)(.*)', r)
        if m is not None:
            date = int(m.group('date'))

            pre_date = m.group(1).strip() # Authors, title (unless it's a book).
            post_date = m.group(3).strip() # Journal, volume, pages, etc.

            # Handle authors and title.
            #  Looks for one or more like 'Author, J.K.L., '
            m_ = re.findall('([a-zA-Z]*,\s[A-Z\.]*,[\s]*)', pre_date)

            if m_ is not None:  # Books will pass, but we won't use title.

                # Remove commas between surnames and initials.
                a_ref = ', '.join([ ' '.join(a.split(', ')) for a in m_ ])
                aulast, auinit = _handle_authors(a_ref)

                # Remainder is title.
                l = len(''.join(m_))
                title = pre_date[l:].upper().strip()

            else:   # Let the rest go for now.
                continue

            # Handle journal, volume, issue, pages.
            m_ = re.search('(.*)[p]{1,2}\.(.*)', post_date)

            if m_ is not None:  # Books will fail here.
                pages = m_.group(2).strip()
                pre_pp = m_.group(1)

                # Get start (and end) page number(s).
                if len(pages.split('-')) == 2:  # Both start and end.
                    spage = pages.split('-')[0]
                    epage = pages.split('-')[1]
                else:   # Only one page.
                    spage = pages
                    epage = pages

                # Get journal details.
                jtitle = pre_pp.split(', ')[0].strip().upper()
                issue_volume = pre_pp.split(', ')[1].strip()

                # Look for an issue number, in parentheses.
                j = re.search('([a-z0-9]*) \(([a-z0-9]*)\)', issue_volume)
                if j is not None:
                    volume = j.group(1)
                    issue = j.group(2)

                else:   # No issue number.
                    volume = issue_volume
                    issue = ''

            else:   # Probably a book.
                # TODO: Make this better.
                title = post_date.strip()   # Includes publisher, etc.
                jtitle = ''
                issue = ''
                volume = ''
                spage = ''
                epage = ''

        else:   # Let the rest go for now.
            continue

        # Populate the Paper object.
        p = Paper()
        p['atitle'] = title
        p['aulast'] = aulast
        p['auinit'] = auinit
        p['issue'] = issue
        p['date'] = date
        p['volume'] = volume
        p['jtitle'] = jtitle
        p['spage'] = spage
        p['epage'] = epage
        p['ayjid'] = _create_ayjid(
                            p['aulast'], p['auinit'], p['date'], p['jtitle'])

        references.append(p)

    return references
