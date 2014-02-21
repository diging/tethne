"""
Methods for parsing JSTOR Data-for-Research datasets.

.. autosummary::

   ngrams
   read

"""

import tethne.data as dt
import os
import xml.etree.ElementTree as ET
import re
from tethne.utilities import dict_from_node, strip_non_ascii
from nltk.corpus import stopwords
import uuid

def read(datapath):
    """
    Yields :class:`.Paper` s from JSTOR DfR package.
    
    Each :class:`.Paper` is tagged with an accession id for this 
    read/conversion.    

    Parameters
    ----------
    filepath : string
        Filepath to unzipped JSTOR DfR folder containing a citations.XML file.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.dfr.read("/Path/to/DfR")        
    """

    try:
        root = ET.parse(datapath + "/citations.XML").getroot()
    except IOError:
        raise IOError(datapath+"citations.XML not found.")

    accession = str(uuid.uuid4())

    papers = []
    for article in root:
        paper = _handle_paper(article)
        paper['accession'] = accession
        papers.append(paper)

    return papers

def ngrams(datapath, N='bi', ignore_hash=True, apply_stoplist=False):
    """
    Yields N-grams from a JSTOR DfR dataset.

    Parameters
    ----------
    filepath : string
        Filepath to unzipped JSTOR DfR folder containing N-grams (e.g.
        'bigrams').
    N : string
        'bi', 'tri', or 'quad'
    ignore_hash : bool
        If True, will exclude all N-grams that contain the hash '#' character.
    apply_stoplist : bool
        If True, will exclude all N-grams that contain words in the NLTK
        stoplist.

    Returns
    -------
    ngrams : dict
        Keys are paper DOIs, values are lists of (Ngram, frequency) tuples.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> trigrams = rd.dfr.ngrams("/Path/to/DfR", N='tri')        
    """

    gram_path = datapath + "/" + N + "grams"
    ngrams = {}

    for file in os.listdir(gram_path):
        if file.split('.')[-1] == 'XML':
            root = ET.parse(gram_path + "/" + file).getroot()
            doi = root.attrib['id']
            grams = [ (gram.text.strip(), int(gram.attrib['weight']) )
                       for gram in root.findall(N + 'gram') # v Hashes v
                       if not ignore_hash or '#' not in list(gram.text) ]

            if apply_stoplist:
                stoplist = stoplist.words()
                grams_ = []
                for g,c in grams:
                    for w in g.split():
                        if w not in stoplist:
                            grams_.append( (g,c) )
                grams = grams_

            ngrams[doi] = grams

    return ngrams

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
    paper = dt.Paper()
    pdata = dict_from_node(article)

    # Direct mappings.
    translator = _dfr2paper_map()
    for key, value in translator.iteritems():
        try:
            paper[value] = str(pdata[key]).upper()
        except KeyError:    # Article may not have all keys of interest.
            pass

    # Handle author names.
    paper['aulast'], paper['auinit'] = _handle_authors(pdata['author'])

    # Handle pubdate.
    paper['date'] = _handle_pubdate(pdata['pubdate'])

    # Handle pagerange.
    paper['spage'], paper['epage'] = _handle_pagerange(pdata['pagerange'])

    # Generate ayjid.
    try:
        paper['ayjid'] = _create_ayjid(paper['aulast'][0], paper['auinit'][0], \
                                       paper['date'], paper['jtitle'])
    except IndexError:  # Article may not have authors.
        pass

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

    return str(start), str(end)

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
            author = str(strip_non_ascii(author))
            try:
                l,i = _handle_author(author)
                aulast.append(l)
                auinit.append(i)
            except ValueError:
                pass
    elif type(authors) is str or type(authors) is unicode:
        author = str(strip_non_ascii(authors))
        try:
            l,i = _handle_author(author)
            aulast.append(l)
            auinit.append(i)
        except ValueError:
            pass
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

    return str(aulast), str(auinit)

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

    ayj = aulast + ' ' + auinit + ' ' + str(date) + ' ' + jtitle

    if ayj == '   ':
        ayj = 'Unknown paper'

    return ayj.upper()
