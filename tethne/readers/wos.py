"""
Reader for Web of Science field-tagged bibliographic data.

.. autosummary::

   convert
   from_dir
   parse
   read

"""

import tethne.data as ds
import xml.etree.ElementTree as ET
import tethne.utilities as util
import os
import re

# MACRO for printing the 'print' statement values.
# 0 prints nothing in the console.
# 1 prints all print statements in the console.
DEBUG = 0

# general functions

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

def _create_ainstid(aulast=None, auinit=None, addr1=None, \
                   addr2=None, country=None, **kwargs):
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

    ainstid = aulast + ' ' + auinit + ' ' + addr1 + ' ' + addr2 + ' ' + country

    if ainstid == ' ':
        ainstid = 'Unknown Institution'

    return ainstid


# Web of Science functions
def parse(filepath):
    """
    Parse Web of Science field-tagged data.

    **Usage**

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> wos_list = rd.wos.parse("/Path/to/data.txt")

    Parameters
    ----------
    filepath : string
        Filepath to the Web of Science plain text file.

    Returns
    -------
    wos_list : list
        A list of dictionaries each associated with a paper from the Web of
        Science with keys from docs/fieldtags.txt as encountered in the file;
        most values associated with keys are strings with special exceptions
        defined by the list_keys and int_keys variables.

    Raises
    ------
    KeyError : Key value which needs to be converted to an 'int' is not present.
    AttributeError :
    IOError : File at filepath not found, not readable, or empty.

    Notes
    -----
    Unknown keys: RI, OI, Z9

    """
    wos_list = []

    paper_start_key = 'PT'
    paper_end_key = 'ER'

    # Try to read filepath
    line_list = []
    try:
        with open(filepath,'r') as f:
            line_list = f.read().splitlines()
    except IOError: # File does not exist, or couldn't be read.
        raise IOError("File does not exist, or cannot be read.")

    if len(line_list) is 0:
        raise IOError("Unable to read filepath or filepath is empty.")

    # Convert the data in the file to a usable list of dictionaries.
    # Note: first two lines of file are not related to any paper therein.
    last_field_tag = paper_start_key #initialize to something.
    for line in line_list[2:]:
        line = util.strip_non_ascii(line)
        field_tag = line[:2]
        if field_tag == paper_start_key:
            # Then prepare for next paper.
            wos_dict = _new_wos_dict()

        if field_tag == paper_end_key:
            # Then add paper to our list.
            wos_list.append(wos_dict)

        # Handle keys like AU,AF,CR that continue over many lines.
        if field_tag == '  ':
            field_tag = last_field_tag

        # Add value for the key to the wos_dict: the rest of the line.
        try:
            if field_tag in ['AU', 'AF', 'CR', 'C1']:
                # These unique fields use the new line delimiter to distinguish
                # their list elements below.
                # The field C1 can be either in multiple lines or in a single
                # line -- It is the address/institutions of the author.
                wos_dict[field_tag] += '\n' + str(line[3:])
            else:
                wos_dict[field_tag] += ' ' + str(line[3:])
        except (KeyError, TypeError, UnboundLocalError):
            wos_dict[field_tag] = str(line[3:])

        last_field_tag = field_tag
    # End line loop.

    # Define keys that should be lists instead of default string.
    list_keys = ['AU', 'AF', 'DE', 'ID', 'CR', 'C1']
    delims = {'AU':'\n',
              'AF':'\n',
              'DE':';',
              'ID':';',
              'C1':'\n',
              'CR':'\n'}

    # And convert the data at those keys into lists.
    for wos_dict in wos_list:
        for key in list_keys:
            delim = delims[key]
            try:
                key_contents = wos_dict[key]
                if delim != '\n':
                    wos_dict[key] = key_contents.split(delim)
                else:
                    wos_dict[key] = key_contents.splitlines()
            except KeyError:
                # One of the keys to be converted to a list didn't exist.
                pass
            except AttributeError:
                # Again a key didn't exist but it belonged to the wos
                # data_struct set of keys; can't split a None.
                pass

    # Similarly convert some data from string to int.
    int_keys = ['PY']
    for wos_dict in wos_list:
        for key in int_keys:
            try:
                wos_dict[key] = int(wos_dict[key])
            except KeyError:
                # One of the keys to be converted to an int didn't exist.
                pass
            except TypeError:
                # Again a key didn't exist but it belonged to the wos
                # data_struct set of keys; can't convert None to an int.
                pass

    return wos_list

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
    paper = ds.Paper()
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
            if DEBUG :
                print  'stripped name: ', name

        name_tokens = name.split(' ')
        if len(name_tokens) < 2:
            # name_tokens.append('None')
            name_tokens.append(' ')

        paper['aulast'] = [name_tokens[0]]
        paper['auinit'] = [''.join(name_tokens[1:]).replace('.','')]

        if DEBUG:
            print "Final Meta Dicts", paper['aulast'], paper['auinit']

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

def _parse_institutions(ref):
    """
    Supports the Web of Science reader by converting the strings found at the C1
    fieldtag of a record into a minimum :class:`.Paper` instance.

    Parameters
    ----------
    ref : str
        'C1' field tag data from a plain text Web of Science file which contains
        Author First and Last names, Institution affiliated, and the
        location/city where they are affiliated to.

    Returns
    -------
    addr_dict : :class:`.Paper`
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
    Needs to check many test cases to check various input types.

    """
    addr_dict = ds.Paper()
    #tokens of form:
    tokens = ref.split(',')
    print 'tokens inside parse_institutions : \n', tokens
    try:

        name = tokens[0]
        name_tokens = name.split(' ')
        addr_dict['aulast'] = name_tokens[0]
        addr_dict['auinit'] = name_tokens[1]

        #strip initial characters based on the field (spaces, 'V', 'DOI')
        addr_dict['addr2'] = tokens[1][1:]
        addr_dict['addr3'] = tokens[2][1:]
        addr_dict['country'] = tokens[3][2:]

    except IndexError:
        #ref did not have the full set of tokens
        pass
    except ValueError:
        #this occurs when the program expects a date but gets a string with
        #no numbers, we leave the field incomplete because chances are
        #the CR string is too sparse to use anyway
        pass

    auinsid = _create_ayjid(addr_dict['aulast'], addr_dict['auinit'],
                         addr_dict['date'], addr_dict['jtitle'])
    addr_dict['auinsid'] = auinsid
    print 'auinsid', auinsid
    return addr_dict

def convert(wos_data):
    """
    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a :class:`.Paper` instance or list of
    :class:`.Paper` instances, the standard for Tethne.

    **Usage**

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> wos_list = rd.wos.parse("/Path/to/data.txt")
       >>> papers = rd.wos.convert(wos_list)

    Parameters
    ----------
    wos_data : list
        A list of dictionaries with keys from the WoS field tags.

    Returns
    -------
    wos_meta : list
        A list of :class:`.Paper` instances.

    Notes
    -----
    Need to handle author name anomolies (case, blank spaces, etc.) that may
    make the same author appear to be two different authors in Networkx; this is
    important for any graph with authors as nodes.

    """
    #create a Paper for each wos_dict and append to this list
    wos_meta = []

    #handle dict inputs by converting to a 1-item list
    if type(wos_data) is dict:
        wos_data = [wos_data]
        #print 'wos data \n' , wos_data


    # Calling the validate function here, before even building wos_meta list
    # [62809724]
    status = _validate(wos_data)
    if not status:
        #raise Error
        pass
    # Define the direct relationships between WoS fieldtags and Paper keys.
    translator = _wos2paper_map()
    # Perform the key convertions
    for wos_dict in wos_data:
        paper = ds.Paper()

        #direct translations
        for key in translator.iterkeys():
            paper[translator[key]] = wos_dict[key]
        # more complicated translations
        # FIXME: not robust to all names, organziation authors, etc.
        if wos_dict['AU'] is not None:
            aulast_list = []
            auinit_list = []
            for name in wos_dict['AU']:
                name_tokens = name.split(',')
                aulast = name_tokens[0].upper().strip()
                try:
                    # 1 for 'aulast, aufirst'
                    auinit = name_tokens[1][1].upper().strip()
                except IndexError:
                    # then no first initial character
                    # preserve parallel name lists with empty string
                    auinit = ''
                aulast_list.append(aulast)
                auinit_list.append(auinit)
            paper['aulast'] = aulast_list
            paper['auinit'] = auinit_list

        #construct ayjid
        ayjid = _create_ayjid(paper['aulast'], paper['auinit'],
                             paper['date'], paper['jtitle'])
        paper['ayjid'] = ayjid

        # Parse author-institution affiliations. #60216226, #57746858.
        # pattern = re.compile('\[(.*?)\]') # pylint
        pattern = re.compile(r'\[(.*?)\]')
        author_institutions = {}

        if wos_dict['C1'] is not None:
            for c1_str in wos_dict['C1']:   # One C1 line for each institution.

                match = pattern.search(c1_str)
                if match:   # Explicit author-institution mappings are provided.
                    authors = c1_str[match.start()+1:match.end()-1].split('; ')
                    institution = c1_str[match.end():].strip().split(', ')
                    for author in authors:
                        # The A-I mapping (in data) uses the AF representation
                        #  of author names. But we use the AU representation
                        #  as our mapping key to ensure consistency with older
                        #  datasets.
                        author_index = wos_dict['AF'].index(author)
                        #e.g."WU, ZD"
                        author_au = wos_dict['AU'][author_index].upper()
                        inst_name = institution[0]

                        try:
                            author_institutions[author_au].append(inst_name)
                        except KeyError:
                            author_institutions[author_au] = [inst_name]

                else:   # Author-institution mappings are not provided. We
                        #  therefore map all authors to all institutions.
                    for author_au in wos_dict['AU']:
                        institution = c1_str.strip().split(', ')
                        inst_name = institution[0]

                        try:
                            author_institutions[author_au].append(inst_name)
                        except KeyError:
                            author_institutions[author_au] = [inst_name]

            paper['institutions'] = author_institutions

        # Convert CR references into paper format
        if wos_dict['CR'] is not None:
            meta_cr_list = []
            for ref in wos_dict['CR']:
                meta_cr_list.append(_parse_cr(ref))
                #print 'meta_cr_list' , meta_cr_list
            paper['citations'] = meta_cr_list

        wos_meta.append(paper)
    # End wos_dict for loop.

    return wos_meta

def read(datapath):
    """
    Yields a list of :class:`.Paper` instances from a Web of Science data file.

    **Usage**

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.wos.read("/Path/to/data.txt")

    Parameters
    ----------
    datapath : string
        Filepath to the Web of Science field-tagged data file.

    Returns
    -------
    papers : list
        A list of :class:`.Paper` instances.

    """

    wl = parse(datapath)
    papers = convert(wl)
    return papers

# [#60462784]
def from_dir(path):
    """
    Convenience function for generating a list of :class:`Paper` from a
    directory of Web of Science field-tagged data files.

    **Usage**

    .. code-block:: python

       >>> import tethne.readers as rd
       >>> papers = rd.wos.from_dir("/Path/to/datadir")

    Parameters
    ----------
    path : string
        Path to directory of field-tagged data files.

    Returns
    -------
    list : A list of :class:`Paper` objects.

    Raises
    ------
    IOError
        Invalid path.

    """

    wos_list = []

    try:
        files = os.listdir(path)
    except IOError:
        raise IOError("Invalid path.")

    for f in files:
        if not f.startswith('.'): # Hidden Files ignore
            try:
                print "Loaded " + f
                wos_list += parse(path + "/" + f)
            except IOError: # Ignore files that don't contain WoS data.
                print "Could not load " + f
                pass

    return convert(wos_list)

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
    if DEBUG:
        print wos_data


    # Create a translator dict whose keys are the fields which needs to be
    # validated from the input.
    # Any new field which needs validation in the future
    translator = _new_wos_dict()

    # Now all these input fields needs to be validated as per requirements.

    for wos_dict in wos_data:
        #direct translations
        for key in translator.iterkeys():
            if DEBUG :
                print wos_dict[key]
            # Validate for 'CR' field
            if wos_dict['CR'] is not None:
                for cr in wos_dict['CR']:
                    # check if the CR field is populated correctly
                    pass
            if wos_dict['C1'] is not None:
                for cr in wos_dict['C1']:
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


def _new_wos_dict():
    """
    Defines the set of field tags that will try to be converted, and intializes
    them to 'None'.

    Returns
    -------
    wos_dict : dict
        A wos_list dictionary with 'None' as default values for all keys.

    """
    wos_dict = {
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

    return wos_dict

def _wos2paper_map():
    """
    Defines the direct relationships between the wos_dict and :class:`.Paper`.

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
