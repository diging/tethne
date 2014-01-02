"""
Each file reader takes an input file from an academic knowledge database
such as the Web of Science or PubMed and parses the input file into a
list of :class:`.Paper` instances for each paper with as many as possible of
the following keys; missing values are set to None:

    * aulast  - authors' last name as a list
    * auinit  - authors' first initial as a list
    * atitle  - article title
    * jtitle  - journal title or abbreviated title
    * volume  - journal volume number
    * issue   - journal issue number
    * spage   - starting page of article in journal
    * epage   - ending page of article in journal
    * date    - article date of publication

These keys are associated with the meta data entries in the databases of
organizations such as the International DOI Foundation and its Registration
Agencies such as CrossRef and DataCite.

In addition, :class:`.Paper` instances will contain keys with information
relevant to the networks of interest for Tethne including:

    * citations -- list of minimum :class:`.Paper` instances for cited
        references.
    * ayjid -- First author's name (last, fi), publication year, and journal.
    * doi -- Digital Object Identifier
    * pmid -- PubMed ID
    * wosid -- Web of Science UT fieldtag

Missing data here also results in the above keys being set to None.
"""
import tethne.data as ds
import xml.etree.ElementTree as ET
import tethne.utilities as util
import os
import re

# general functions

def create_ayjid(aulast=None, auinit=None, date=None, jtitle=None, **kwargs):
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
    elif isinstance(aulast,list):
        aulast = aulast[0]

    if auinit is None:
        auinit = ''
    elif isinstance(auinit,list):
        auinit = auinit[0]

    if date is None:
        date = ''

    if jtitle is None:
        jtitle = ''

    ayj = aulast + ' ' + auinit + ' ' + str(date) + ' ' + jtitle

    if ayj == '   ':
        ayj = 'Unknown paper'

    return ayj

def create_ainstid(aulast=None, auinit=None, addr1=None, addr2=None, country=None, **kwargs):
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
    elif isinstance(aulast,list):
        aulast = aulast[0]

    if auinit is None:
        auinit = ''
    elif isinstance(auinit,list):
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
def parse_wos(filepath):
    """Read Web of Science plain text data.

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
    KeyError
        One key value which needs to be converted to an 'int' is not present.

    AttributeError
        similar type of error as given above.

    IOError
        File at filepath not found, not readable, or empty.

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

    #convert the data in the file to a usable list of dictionaries
    #note: first two lines of file are not related to any paper therein
    last_field_tag = paper_start_key #initialize to something
    for line in line_list[2:]:
        line = util.strip_non_ascii(line)
        field_tag = line[:2]
        if field_tag == paper_start_key:
            #then prepare for next paper
            wos_dict = ds.new_wos_dict()

        if field_tag == paper_end_key:
            #then add paper to our list
            wos_list.append(wos_dict)

        #handle keys like AU,AF,CR that continue over many lines
        if field_tag == '  ':
            field_tag = last_field_tag

        #add value for the key to the wos_dict: the rest of the line
        try:
            if field_tag in ['AU', 'AF', 'CR','C1']:
                # These unique fields use the new line delimiter to distinguish
                # their list elements below.
                # The field C1 can be either in multiple lines or in a single
                # line -- It is the address/institutions of the author.
                wos_dict[field_tag] += '\n' + str(line[3:])
            else:
                wos_dict[field_tag] += ' ' + str(line[3:])
        except (KeyError, TypeError,UnboundLocalError):
            #key didn't exist already, can't append but must create
            wos_dict[field_tag] = str(line[3:])

        last_field_tag = field_tag
    #end line loop

    #define keys that should be lists instead of default string
    list_keys = ['AU','AF','DE','ID','CR','C1']
    delims = {'AU':'\n',
              'AF':'\n',
              'DE':';',
              'ID':';',
              'C1':'\n',
              'CR':'\n'}

    #and convert the data at those keys into lists
    for wos_dict in wos_list:
        #print 'wos_dict is \n',wos_dict
        for key in list_keys:
            delim = delims[key]
            #print 'delim is\n' , delim
            try:
                key_contents = wos_dict[key]
                #print 'key_contents is \n ' , key_contents
                if delim != '\n':
                    wos_dict[key] = key_contents.split(delim)
                else:
                    wos_dict[key] = key_contents.splitlines()
            except KeyError:
                #one of the keys to be converted to a list didn't exist
                pass
            except AttributeError:
                #again a key didn't exist but it belonged to the wos
                #data_struct set of keys; can't split a None
                pass

    #similarly convert some data from string to int
    int_keys = ['PY']
    for wos_dict in wos_list:
        for key in int_keys:
            try:
                wos_dict[key] = int(wos_dict[key])
            except KeyError:
                #one of the keys to be converted to an int didn't exist
                pass
            except TypeError:
                #again a key didn't exist but it belonged to the wos
                #data_struct set of keys; can't convert None to an int
                pass

    return wos_list


def parse_cr(ref):

    """
    Supports the Web of Science reader by converting the strings found
    at the CR field tag of a record into a minimum :class:`.Paper` instance.

    Parameters
    ----------
    ref : str
        CR field tag data from a plain text Web of Science file.

    Returns
    -------
    meta_dict : :class:`.Paper`
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
    meta_dict = ds.Paper()
    #tokens of form: aulast auinit, date, jtitle, volume, spage, doi
    tokens = ref.split(',')
    try:
        #FIXME: needs better name parser
        name = tokens[0]
        name_tokens = name.split(' ')
        
        
        
        meta_dict['aulast'] = [name_tokens[0]]
        meta_dict['auinit'] = [name_tokens[1]]

        #strip initial characters based on the field (spaces, 'V', 'DOI')
        meta_dict['date'] = int(tokens[1][1:])
        meta_dict['jtitle'] = tokens[2][1:]
        meta_dict['volume'] = tokens[3][2:]
        meta_dict['spage'] = tokens[4][2:]
        meta_dict['doi'] = tokens[5][5:]
    except IndexError as E:     # ref did not have the full set of tokens
        pass
    except ValueError as E:     # This occurs when the program expects a date
        pass                    #  but gets a string with no numbers. We leave
                                #  the field incomplete because chances are the
                                #  CR string is too sparse to use anyway.

    ayjid = create_ayjid(meta_dict['aulast'], meta_dict['auinit'],
                         meta_dict['date'], meta_dict['jtitle'])
    meta_dict['ayjid'] = ayjid

    return meta_dict

def parse_institutions(ref):
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

    auinsid = create_ayjid(addr_dict['aulast'], addr_dict['auinit'],
                         addr_dict['date'], addr_dict['jtitle'])
    addr_dict['auinsid'] = auinsid
    print 'auinsid', auinsid
    return addr_dict

def wos2meta(wos_data):
    """
    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a :class:`.Paper` instance or list of
    :class:`.Paper` instances, the standard for Tethne.

    Parameters
    ----------
    wos_data : list
        A list of wos_dict dictionaries with keys from the WoS field tags.

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
    #define the direct relationships between WoS fieldtags and Paper keys
    translator = ds.wos2meta_map()

    #perform the key convertions
    for wos_dict in wos_data:
        meta_dict = ds.Paper()

        #direct translations
        for key in translator.iterkeys():
            meta_dict[translator[key]] = wos_dict[key]

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
            meta_dict['aulast'] = aulast_list
            meta_dict['auinit'] = auinit_list

        #construct ayjid
        ayjid = create_ayjid(meta_dict['aulast'], meta_dict['auinit'],
                             meta_dict['date'], meta_dict['jtitle'])
        meta_dict['ayjid'] = ayjid

        # Parse author-institution affiliations. #60216226, #57746858.
        pattern = re.compile('\[(.*?)\]')
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
                        author_au = wos_dict['AU'][author_index].upper()    # e.g. "WU, ZD"
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

            meta_dict['institutions'] = author_institutions

        # Convert CR references into meta_dict format
        if wos_dict['CR'] is not None:
            meta_cr_list = []
            for ref in wos_dict['CR']:
                meta_cr_list.append(parse_cr(ref))
                #print 'meta_cr_list' , meta_cr_list
            meta_dict['citations'] = meta_cr_list

        wos_meta.append(meta_dict)
    # End wos_dict for loop.

    return wos_meta

# [#60462784]
def parse_from_dir(path):
    """
    Convenience function for generating a wos_list from a directory of Web of
    Science field-tagged data files.

    Parameters
    ----------
    path : string
        Path to directory of field-tagged data files.

    Returns
    -------
    wos_list : list
        A list of wos_dict dictionaries.

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

    for file in files:
        try:
            print "Loaded " + file
            wos_list += parse_wos(path + "/" + file)
        except (IOError, DataError): # Ignore files that don't contain WoS data.
            print "Could not load " + file
            pass

    return wos_list