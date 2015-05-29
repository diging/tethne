"""
Reader for Web of Science field-tagged bibliographic data.

Tethne parses Web of Science field-tagged data into a list of :class:`.Paper`
objects. This is a two-step process: data are first parsed into a list of
dictionaries with field-tags as keys, and then each dictionary is converted to a
:class:`.Paper` . :func:`.readers.wos.read` performs both steps in sequence.

One-step Parsing
````````````````

The method :func:`.readers.wos.read` performs both :func:`.readers.wos.parse`
and :func:`.readers.wos.convert` . This is the preferred (simplest) approach in
most cases.

.. code-block:: python

   >>> papers = rd.wos.read("/Path/to/savedrecs.txt")
   >>> papers[0]
   <tethne.data.Paper instance at 0x101b575a8>

Alternatively, if you have many data files saved in the same directory, you can
use :func:`.readers.wos.from_dir` :

.. code-block:: python

   >>> papers = rd.wos.parse_from_dir("/Path/to")

Two-step Parsing
````````````````

Use the two-step approach if you need to access fields not included in
:class:`.Paper`\, or if you wish to perform some intermediate manipulation on
the raw parsed data.

First import the :mod:`.readers.wos` module:

.. code-block:: python

   >>> import tethne.readers as rd

Then parse the WoS data to a list of field-tagged dictionaries using
:func:`.readers.wos.parse` :

.. code-block:: python

   >>> papers = rd.wos.parse("/Path/to/savedrecs.txt")
   >>> papers[0].keys()
   ['EM', '', 'CL', 'AB', 'WC', 'GA', 'DI', 'IS', 'DE', 'VL', 'CY', 'AU', 'JI',
    'AF', 'CR', 'DT', 'TC', 'EP', 'CT', 'PG', 'PU', 'PI', 'RP', 'J9', 'PT',
    'LA', 'UT', 'PY', 'ID', 'SI', 'PA', 'SO', 'Z9', 'PD', 'TI', 'SC', 'BP',
    'C1', 'NR', 'RI', 'ER', 'SN']

Convert those field-tagged dictionaries to :class:`.Paper` objects using
:func:`.readers.wos.convert` :

.. code-block:: python

   >>> papers = rd.wos.convert(papers)
   >>> papers[0]
   <tethne.data.Paper instance at 0x101b575a8>

Methods
```````

.. autosummary::

   convert
   from_dir
   parse
   read

"""

import xml.etree.ElementTree as ET
from ..utilities import *
from ..classes import Corpus, Paper
import os
import re
import uuid

import logging
logging.basicConfig(filename=None,
                    format=''.join(['%(asctime)-6s: %(name)s - %(levelname)s',
                                    ' - %(module)s - %(funcName)s - ',
                                    '%(lineno)d - %(message)s']))
logger = logging.getLogger(__name__)
logger.setLevel('INFO')


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

    ayj = ' '.join([aulast, auinit, str(date), jtitle]).upper().strip()

    if ayj == '':
        ayj = 'None'

    return ayj

def _create_ainstid(aulast=None, auinit=None, addr1=None, addr2=None,
                    country=None, **kwargs):
    """
    This function is to create an fuzzy identifier ainstid.
    Convert aulast, auinit, and jtitle into the fuzzy identifier ainstid.
    Returns 'Unknown Institution' if all id components are missing (None).

    Parameters
    ----------
    Kwargs : dict
        A dictionary of keyword arguments.
    aulast : string
        Author surname.
    auinit : string
        Author initial(s).
    address1 : string
        Address of the Institution.
    address2 : string
        Address of the Institution.
    country : string
        Country of affiliation

    Returns
    -------
    ainstid : string
        Fuzzy identifier ainstid, or 'Unknown Institution' if all id components
        are missing (None).

    """
    if aulast is None:
        aulast = ''
    elif isinstance(aulast, list):
        aulast = aulast[0]

    if auinit is None:
        auinit = ''
    elif isinstance(auinit, list):
        auinit = auinit[0]

    if addr1 is None:
        addr1 = ''
    if  addr2 is None:
        addr2 = ''
    if  country is None:
        country = ''

    ainstid = ' '.join([aulast, auinit, addr1, addr2, country]).upper().strip()

    if ainstid == '':
        ainstid = 'None'

    return ainstid


def parse(filepath):
    """
    Parse Web of Science field-tagged data.

    Parameters
    ----------
    filepath : string
        Filepath to the Web of Science plain text file.

    Returns
    -------
    papers : list
        A list of dictionaries each associated with a paper from the Web of
        Science with keys from docs/fieldtags.txt as encountered in the file;
        most values associated with keys are strings with special exceptions
        defined by the list_keys and int_keys variables.

    Raises
    ------
    KeyError
        Key value which needs to be converted to an 'int' is not present.
    AttributeError
    IOError
        File at filepath not found, not readable, or empty.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.wos.parse("/Path/to/data.txt")

    Notes
    -----
    Unknown keys: RI, OI, Z9

    """

    def _set_singleValue(p, k, v):
        p[k] = v

    def _set_listValue(p, k, v):
        if p[k] is None:
            p[k] = []
        p[k].append(v)

    def _handle_author(p, k, v):
        tokens = tuple([t.upper().strip() for t in v.split(',')])
        if len(tokens) > 0:
            aulast, auinit = tokens
        else:
            aulast, auinit = tokens[0], ''
        _set_listValue(p, 'aulast', aulast)
        _set_listValue(p, 'auinit', auinit)

    def _handle_groupAuthor(p, v):
        _set_listValue(p, 'aulast', v)
        _set_listValue(p, 'auinit', '')
        _set_listValue(p, 'aufull', v)

    def _handle_date(p, v):
        _set_singleValue(p, 'date', int(v))


    translator = {
                'AU': 'aulast',
                'AI': 'auinit',
                'AF': 'aufull',
                'CA': _handle_groupAuthor,
                'DI':'doi',
                'TI':'atitle',
                'SO':'jtitle',
                'VL':'volume',
                'IS':'issue',
                'BP':'spage',
                'EP':'epage',
                'PY':'date',
                'UT':'wosid',
                'AB':'abstract',
                'PT': None,   }

    papers = []

    startKey = 'PT'
    endKey = 'ER'

    try:
        with open(filepath,'r') as f:
            lines = f.read().splitlines()
    except IOError: # File does not exist, or couldn't be read.
        raise IOError("File does not exist, or cannot be read.")

    if len(lines) == 0:
        raise IOError("File at {0} is empty".format(filepath))

    # Convert the data in the file to a usable list of dictionaries.
    # Note: first two lines of file are not related to any paper therein.
    lastTag = startKey #initialize to something.
    for line in lines[2:]:
        line = strip_non_ascii(line)
        fieldTag, value = line[:2].strip(), line[3:].strip()
        field = translator[fieldTag]

        if fieldTag == startKey:
            paper = Paper()
        if fieldTag == endKey:
            papers.append(paper)

        # Handle keys like AU,AF,CR that continue over many lines.
        if len(fieldTag) == 0:
            fieldTag = lastTag

        # Add value for the key to the paper: the rest of the line.
        if fieldTag in ['AU', 'AF', 'CR', 'C1', 'CA']:
            if paper[field] is None:
                paper[field] = []
            paper[field].append(value)
        elif fieldTag in ['DE', 'ID']:
            paper[field] = value.split(';')
        elif fieldTag in ['PY']:
            paper[field] = int(value)
        else:
            if paper[field] is None:
                paper[field] = ''
            paper[fieldTag] += ' ' + line[3:]

        lastTag = fieldTag

    return papers

def _parse_cr(ref):

    """
    Supports the Web of Science reader by converting the strings found
    at the CR field tag of a record into a minimum :class:`.Paper` instance.

    Parameters
    ----------
    ref : str
        CR field tag data from a plain text Web of Science file.

    Returns
    -------
    paper : :class:`.Paper`
        A :class:`.Paper` instance.

    Raises
    ------
    IndexError
        When input 'ref' has less number of tokens than necessary ones.
    ValueError
        Gets input with mismacthed inputtype. Ex: getting no numbers for a date
        field.

    Notes
    -----
    Needs a sophisticated name parser, would like to use an open source resource
    for this.

    If WoS is missing a field in the middle of the list there are NOT commas
    indicating that; the following example does NOT occur:

        Doe J, ,, Some Journal

    instead

        Doe J, Some Journal

    This threatens the integrity of WoS data; should we address it?

    Another threat: if WoS is unsure of the DOI number there will be multiple
    DOI numbers in a list of form [doi1, doi2, ...], address this?

    """
    paper = Paper()
    #tokens of form: aulast auinit, date, jtitle, volume, spage, doi
    tokens = ref.split(',')
    try:
        #FIXME: needs better name parser
        # Checking for few parsers, in the meantime trying out few things.
        name = tokens[0]
        # Temp Solution for #62809724
        pattern = re.compile(r'\[(.*?)\]')
        match = pattern.search(name)
        if match:
            # remove the [] and make it a proper one.
            name = name[match.start()+1:match.end()-1]

        name_tokens = name.split(' ')
        if len(name_tokens) < 2:
            # name_tokens.append('None')
            name_tokens.append(' ')

        paper['aulast'] = [name_tokens[0]]
        paper['auinit'] = [''.join(name_tokens[1:]).replace('.','')]

        # Temp Solution for #62809724
        if paper['auinit'] == 'None' or paper['aulast'] == 'None' :
            raise ("The Cited References field is not in the expeceted format")

        #strip initial characters based on the field (spaces, 'V', 'DOI')
        paper['date'] = int(tokens[1][1:])
        paper['jtitle'] = tokens[2][1:]
        paper['volume'] = tokens[3][2:]
        paper['spage'] = tokens[4][2:]
        paper['doi'] = tokens[5][5:]
    except IndexError as E:     # ref did not have the full set of tokens
        pass
    except ValueError as E:     # This occurs when the program expects a date
        pass                    #  but gets a string with no numbers. We leave
                                #  the field incomplete because chances are the
                                #  CR string is too sparse to use anyway.

    ayjid = _create_ayjid(paper['aulast'], paper['auinit'],
                         paper['date'], paper['jtitle'])
    paper['ayjid'] = ayjid

    return paper

def convert(wos_data, **kwargs):
    """
    Convert parsed field-tagged data to :class:`.Paper` instances.

    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a :class:`.Paper` instance or list of
    :class:`.Paper` instances, the standard for Tethne.

    Each :class:`.Paper` is tagged with an accession id for this conversion.

    Parameters
    ----------
    wos_data : list
        A list of dictionaries with keys from the WoS field tags.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` instances.

    Examples
    --------

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.wos.parse("/Path/to/data.txt")
       >>> papers = rd.wos.convert(papers)

    Notes
    -----
    Need to handle author name anomolies (case, blank spaces, etc.) that may
    make the same author appear to be two different authors in Networkx; this is
    important for any graph with authors as nodes.

    """

    accession = str(uuid.uuid4())

    #create a Paper for each paper and append to this list
    papers = kwargs.get('papers', [])

    #handle dict inputs by converting to a 1-item list
    if type(wos_data) is dict:
        wos_data = [wos_data]
        #print 'wos data \n' , wos_data


    # Calling the validate function here, before even building papers list
    # [62809724]
    status = _validate(wos_data)
    if not status:
        #raise Error
        pass

    # Define the direct relationships between WoS fieldtags and Paper keys.
    translator = _wos2paper_map()

    # Perform the key convertions
    for paper in wos_data:
        paper = Paper()

        #direct translations
        for key in translator.iterkeys():
            paper[translator[key]] = paper[key]

        # Group authors ('CA') are treated as personal authors.
        if 'CA' in paper.keys():
            try: paper['AU'] += paper['CA']
            except TypeError: paper['AU'] = paper['CA']
            try: paper['AF'] += paper['CA']
            except KeyError: paper['AF'] = paper['CA']

        # more complicated translations
        # FIXME: not robust to all names, organziation authors, etc.
        if paper['AU'] is not None:
            paper['aulast'], paper['auinit'] = _handle_authors(paper)

        #construct ayjid
        ayjid = _create_ayjid(paper['aulast'], paper['auinit'],
                              paper['date'], paper['jtitle'])
        paper['ayjid'] = ayjid

        # Parse author-institution affiliations. #60216226, #57746858.
        if paper['C1'] is not None:
            paper['institutions'] = _handle_author_institutions(paper)

        # Convert CR references into paper format
        if paper['CR'] is not None:
            meta_cr_list = []
            for ref in paper['CR']:
                meta_cr_list.append(_parse_cr(ref))
                #print 'meta_cr_list' , meta_cr_list
            paper['citations'] = meta_cr_list

        paper['accession'] = accession

        papers.append(paper)
    # End paper for loop.

    return papers

def _handle_authors(paper):

    aulast_list = []
    auinit_list = []
    for name in paper['AU']:
        name_tokens = name.split(',')
        aulast = name_tokens[0].upper().strip()
        try:
            # 1 for 'aulast, aufirst'
            auinit = name_tokens[1][1:].upper().strip()
        except IndexError:
            # then no first initial character
            # preserve parallel name lists with empty string
            auinit = ''
        aulast_list.append(aulast), auinit_list.append(auinit)

    return aulast_list, auinit_list

def _handle_author_institutions(paper):
    pattern = re.compile(r'\[(.*?)\]')
    author_institutions = {}

    for c1_str in paper['C1']:   # One C1 line for each institution.

        match = pattern.search(c1_str)
        if match:   # Explicit author-institution mappings are provided.
            # For example:
            #
            # [Lin, Bing-Sian; Lee, Chon-Lin] Natl Sun Yat Sen Univ, Dept
            #   Marine Environm & Engn, Kaohsiung 80424, Taiwan.
            # [Brimblecombe, Peter] Univ E Anglia, Sch Environm Sci, Norwich NR4
            #   7TJ, Norfolk, England.
            # [Lee, Chon-Lin] Natl Sun Yat Sen Univ, Asia Pacific Ocean Res Ctr,
            #   Kuroshio Res Grp, Kaohsiung 80424, Taiwan.
            # [Lee, Chon-Lin] Natl Sun Yat Sen Univ, Ctr Emerging Contaminants
            #   Res, Kaohsiung 80424, Taiwan.
            # [Liu, James T.] Natl Sun Yat Sen Univ, Inst Marine Geol & Chem,
            #   Kaohsiung 80424, Taiwan.

            authors = c1_str[match.start()+1:match.end()-1].split('; ')
            institution = c1_str[match.end():].upper()      \
                                              .strip()      \
                                              .strip('.')   \
                                              .split(', ')

            for author in authors:
                # The A-I mapping (in data) uses the AF representation
                #  of author names. But we use the AU representation
                #  as our mapping key to ensure consistency with older
                #  datasets.
                author_index = paper['AF'].index(author)
                author_au = paper['AU'][author_index].upper()    \
                                                        .replace(',','')
                inst_name = ', '.join([institution[0], institution[-1].strip()])

                # Use lists, so we can tally 'votes' for most likely
                #  institution.
                try:
                    author_institutions[author_au].append(inst_name)
                except KeyError:
                    author_institutions[author_au] = [inst_name]

        else:   # Author-institution mappings are not provided. We
                #  therefore map all authors to all institutions.
            # For example:
            #
            # UN, Environm Programme, Nairobi, Kenya.
            # Univ Haifa, Dept Geog, IL-31095 Haifa, Israel.

            for author_au in paper['AU']:
                author_au = author_au.upper()       \
                                     .replace(',','')

                institution = c1_str.upper()        \
                                    .strip()        \
                                    .strip('.')     \
                                    .split(',')
                inst_name = ', '.join([institution[0], institution[-1].strip()])

                # Use lists, so we can tally 'votes' for most likely
                #  institution.
                try:
                    author_institutions[author_au].append(inst_name)
                except KeyError:
                    author_institutions[author_au] = [inst_name]

    # Should have the same order as the author names.
    inst_list = []
    for k in paper['AU']:
        k = k.upper().replace(',','')
        if k in author_institutions:
            inst_list.append(author_institutions[k])
        else:
            inst_list.append([])

    return inst_list

def read(datapath, **kwargs):
    """
    Yields a list of :class:`.Paper` instances from a Web of Science data file.

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
       >>> papers = rd.wos.read("/Path/to/data.txt")

    """
    logger.debug('kwargs: {0}'.format(kwargs))

    try:
        wl = parse(datapath)
        papers = convert(wl, **kwargs)
    except IOError:
        raise IOError("Invalid path.")

    return papers

# [#60462784]
def from_dir(path):
    """
    Convenience function for generating a list of :class:`.Paper` from a
    directory of Web of Science field-tagged data files.

    Parameters
    ----------
    path : string
        Path to directory of field-tagged data files.

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

       >>> import tethne.readers as rd
       >>> papers = rd.wos.from_dir("/Path/to/datadir")

    """

    papers = []

    try:
        files = os.listdir(path)
    except IOError:
        raise IOError("Invalid path.")

    for f in files:
        if not f.startswith('.'): # Ignore hidden files.
            try:
                papers += parse(path + "/" + f)
            except (IOError,UnboundLocalError): # Ignore files that don't
                pass                            #  contain WoS data.
    papers = convert(papers)
    return papers

def read_corpus(path):
    """

    """

    papers = read(path)
    return Corpus(papers, index_by='wosid')

def corpus_from_dir(path):
    """

    Parameters
    ----------
    path : string
        Path to directory of field-tagged data files.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` objects.
    """

    papers = from_dir(path)
    return Corpus(papers, index_by='wosid')

# [62809724]
def _validate(wos_data):
    """
    Defines the fucntion to check the input data validation.

    Returns
    -------
    bool - True or false
    if the data is in expected format (True)
    if the respective field is not in expected format (False)

    Raises
    ------
    ValueError - according to the severity of the issue,
    whether the wrong format will affect the further processing.
    """

    # Create a translator dict whose keys are the fields which needs to be
    # validated from the input.
    # Any new field which needs validation in the future
    translator = _new_paper()

    # Now all these input fields needs to be validated as per requirements.

    for paper in wos_data:
        #direct translations
        for key in translator.iterkeys():
            # Validate for 'CR' field
            if paper['CR'] is not None:
                for cr in paper['CR']:
                    # check if the CR field is populated correctly
                    pass
            if paper['C1'] is not None:
                for cr in paper['C1']:
                    # check if the C1 field is populated correctly
                    pass

    status = 1
    return status

def _new_query_dict():
    """
    Declares only those keys of the :class:`.Paper`'s metadata that are
    queryable through CrossRef.
    """
    q_dict = {
                'aulast':None,
                'auinit':None,
                'atitle':None,
                'address':None,
                'jtitle':None,
                'volume':None,
                'issue':None,
                'spage':None,
                'epage':None,
                'date':None     }

    return q_dict


def _new_paper():
    """
    Defines the set of field tags that will try to be converted, and intializes
    them to 'None'.

    Returns
    -------
    paper : dict
        A papers dictionary with 'None' as default values for all keys.

    """
    paper = {
                    'DI':None,
                    'AU':None,
                    'C1':None,
                    'TI':None,
                    'SO':None,
                    'VL':None,
                    'IS':None,
                    'BP':None,
                    'EP':None,
                    'PY':None,
                    'UT':None,
                    'CR':None,
                    'AB':None   }

    return paper

def _wos2paper_map():
    """
    Defines the direct relationships between the paper and :class:`.Paper`.

    Returns
    -------
    translator : dict
        A 'translator' dictionary.

    """
    translator = {
                    'DI':'doi',
                    'TI':'atitle',
                    'SO':'jtitle',
                    'VL':'volume',
                    'IS':'issue',
                    'BP':'spage',
                    'EP':'epage',
                    'PY':'date',
                    'UT':'wosid',
                    'AB':'abstract'    }

    return translator

#Custom Error Defined
class DataError(Exception):
    pass
