"""
.. module:: readers
    :synopsis: Methods for parsing bibliographic data.
    
Each file reader takes an input file from an academic knowledge database
such as the Web of Science or PubMed and parses the input file into a
list of "meta_dict" dictionaries for each paper with as many as possible of 
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

In addition, meta_dict dictionaries will contain keys with information 
relevant to the networks of interest for Tethne including:

    * citations   - a list of minimum meta_dict dictionaries for cited references
    * ayjid       - First author's last name, initial the publication year and
                  the journal published in
    * doi         - Digital Object Identifier
    * pmid        - PubMed ID
    * wosid       - Web of Science UT fieldtag
    
Missing data here also results in the above keys being set to None.
"""
import data_struct as ds
import xml.etree.ElementTree as ET

# general functions
def create_ayjid(aulast=None, auinit=None, date=None, jtitle=None, **kwargs):
    """
    .. function:: create_ayjid(aulast='', auinit='', date='', jtitle='', **kwargs)
    
    Convert aulast, auinit, and jtitle into the fuzzy identifier ayjid
    Returns 'Unknown paper' if all id components are missing (None).
    
    Kwargs:
        aulast (str): Author surname.
        auinit (str): Author initial(s).
        date (str): Four-digit year.
        jtitle (str): Title of the journal.
        
    Returns:
        str. Fuzzy identifier ayjid, or 'Unknown paper' if all id components are missing (None).
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


# Web of Science functions
def parse_wos(filepath):
    """Read Web of Science plain text data.
    
    Args:
        filepath (str): Filepath to the Web of Science plain text file.
        
    Returns:
        list.  A list of dictionaries each associated with a paper from the Web of Science with keys from docs/fieldtags.txt as encountered in the file; most values associated with keys are strings with special exceptions defined by the list_keys and int_keys variables.
            
    Notes:
       Unknown keys: RI, OI, Z9
    """
    wos_list = []

    #define special key handling
    paper_start_key = 'PT'
    paper_end_key = 'ER'

    #try to read filepath
    line_list = []
    with open(filepath,'r') as f:
        line_list = f.read().splitlines()
    if len(line_list) is 0:
        raise IOError("Unable to read filepath or filepath is empty")

    #convert the data in the file to a usable list of dictionaries
    #note: first two lines of file are not related to any paper therein
    last_field_tag = paper_start_key #initialize to something
    for line in line_list[2:]:
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
            if field_tag in ['AU', 'AF', 'CR']:
                #these unique fields use the new line delimiter to distinguish
                #their list elements below
                wos_dict[field_tag] += '\n' + str(line[3:])
            else:
                wos_dict[field_tag] += ' ' + str(line[3:])
        except (KeyError, TypeError):
            #key didn't exist already, can't append but must create
            wos_dict[field_tag] = str(line[3:])

        last_field_tag = field_tag
    #end line loop

    #define keys that should be lists instead of default string
    list_keys = ['AU','AF','DE','ID','CR']
    delims = {'AU':'\n',
              'AF':'\n',
              'DE':';',
              'ID':';',
              'CR':'\n'}

    #and convert the data at those keys into lists
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
    at the CR field tag of a record into a minimum meta_dict dictionary 

    Args:
        ref (str): CR field tag data from a plain text Web of Science file.

    Returns:
        dict.  meta_dict dictionary.
    
    Notes:
        Needs a sophisticated name parser, would like to use an open source
        resource for this.
        
        If WoS is missing a field in the middle of the list there are NOT
        commas indicating that; the following example does NOT occur
        
            Doe J, ,, Some Journal

        instead

            Doe J, Some Journal

        this threatens the integrity of WoS data; should we address it?
        Another threat: if WoS is unsure of the DOI number there will be
        multiple DOI numbers in a list of form [doi1, doi2, ...], address this?
    """
    meta_dict = ds.new_meta_dict()
    #tokens of form: aulast auinit, date, jtitle, volume, spage, doi
    tokens = ref.split(',')
    try:
        #FIXME: needs better name parser
        name = tokens[0]
        name_tokens = name.split(' ')
        meta_dict['aulast'] = name_tokens[0]
        meta_dict['auinit'] = name_tokens[1]

        #strip initial characters based on the field (spaces, 'V', 'DOI')
        meta_dict['date'] = int(tokens[1][1:])
        meta_dict['jtitle'] = tokens[2][1:]
        meta_dict['volume'] = tokens[3][2:]
        meta_dict['spage'] = tokens[4][2:]
        meta_dict['doi'] = tokens[5][5:]
    except IndexError:
        #ref did not have the full set of tokens
        pass
    except ValueError:
        #this occurs when the program expects a date but gets a string with
        #no numbers, we leave the field incomplete because chances are
        #the CR string is too sparse to use anyway
        pass

    ayjid = create_ayjid(meta_dict['aulast'], meta_dict['auinit'], 
                         meta_dict['date'], meta_dict['jtitle'])
    meta_dict['ayjid'] = ayjid
 
    return meta_dict

def wos2meta(wos_data):
    """
    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a meta_dict dictionary or list of
    dictionaries, the standard for Tethne.

    Args:
        wos_data (dict): A list of dictionaries with keys from the WoS field tags.

    Returns:
        dict. a meta_dict dictionary.

    Notes:
        need to handle author name anomolies (case, blank spaces, etc.)
        that may make the same author appear to be two different authors
        in Networkx; this is important for any graph with authors as nodes.
    """
    #create a meta_dict for each wos_dict and append to this list
    wos_meta = []

    #handle dict inputs by converting to a 1-item list
    if type(wos_data) is dict:
        wos_data = [wos_data]

    #define the direct relationships between WoS fieldtags and meta_dict keys
    translator = ds.wos2meta_map()
    
    #perform the key convertions
    for wos_dict in wos_data:
        meta_dict = ds.new_meta_dict()

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

        #convert CR references into meta_dict format
        if wos_dict['CR'] is not None:
            meta_cr_list = []
            for ref in wos_dict['CR']:
                meta_cr_list.append(parse_cr(ref))
            meta_dict['citations'] = meta_cr_list

        wos_meta.append(meta_dict)
    #end wos_dict for loop

    return wos_meta


# PubMed functions
def pubmed_file_id(filename):
    """
    Given a filename (presumed to contain PubMed compatible IDs)
    return an xml string for each article associated with that ID.
    
    Args:
        filename (str): Path to a file containing PubMed-compatible IDs.
    
    Returns:
        list.  A list of XML strings.
    """

    return None

def pubmed_file_xml(filename):
    """
    Given a filename (presumed to contain PubMed XML schemas)
    return an xml string for each article in the file.
    
    Args:
        filename (str): Path to a file containing PubMed XML schemas.
    
    Returns:
        list.  A list of meta_dict dicts.
    """

    return None

def parse_pubmed_xml(filepath):
    """
    Given a file with PubMed XML, return a list of meta_dicts

    See the following hyperlinks regarding possible structures of XML:
        http://www.ncbi.nlm.nih.gov/pmc/pmcdoc/tagging-guidelines/citations/v2/citationtags.html#2Articlewithmorethan10authors%28listthefirst10andaddetal%29
        http://dtd.nlm.nih.gov/publishing/
        
    Args:
        filepath (str): Path to PubMed XML file.
    
    Returns:
        list.  A list of meta_dict dictionaries.
    """
    tree = ET.parse(filepath)
    root = tree.getroot()
    
    # define location of simple article meta data relative to xml tree rooted 
    # at 'article'
    meta_loc = {'atitle':'./front/article-meta/title-group/article-title',
                'jtitle':('./front/journal-meta/journal-title-group/' +
                          'journal-title'),
                'volume':'./front/article-meta/volume',
                'issue':'./front/article-meta/issue',
                'spage':'./front/article-meta/fpage',
                'epage':'./front/article-meta/lpage'}
    
    # location relative to element-citation element
    cit_meta_loc = {'atitle':'./article-title',
                    'jtitle':'./source',
                    'date':'./year',
                    'volume':'./volume',
                    'spage':'./fpage',
                    'epage':'./epage'}
    
    meta_list = []
    for article in root.iter('article'):
        meta_dict = ds.new_meta_dict()
    
        # collect information from the 'front' section of the article
        # collect the simple data
        for key in meta_loc.iterkeys():
            key_data = article.find(meta_loc[key]) 
            if key_data is not None:
                meta_dict[key] = key_data.text
            else:
                meta_dict[key] = None
    
        # collect doi and pmid 
        id_list = article.findall('./front/article-meta/article-id')
        for identifier in id_list:
            id_type = identifier.get('pub-id-type')
            if id_type == 'doi':
                meta_dict['doi'] = identifier.text 
            elif id_type == 'pmid':
                meta_dict['pmid'] = identifier.text
            else:
                # if never found, remain at None from initialization
                pass
    
        # collect aulast and auinint
        aulast = []
        auinit = []
        contribs = article.findall('./front/article-meta/contrib-group/contrib')
        # if contrib is not found then loop is skipped
        for contrib in contribs:
            contrib_type = contrib.get('contrib-type')
            if contrib_type == 'author':
                surname = contrib.find('./name/surname')
                if surname is not None:
                    # then it was found
                    aulast.append(surname.text)
                else:
                    aulast.append(None)
    
                # multiple given names? this takes first one
                given_name = contrib.find('./name/given-names')
                if given_name is not None:
                    # then it was found
                    auinit.append(given_name.text[0])
                else:
                    auinit.append(None)
        meta_dict['aulast'] = aulast
        meta_dict['auinit'] = auinit
    
        # collect date
        pub_dates = article.findall('./front/article-meta/pub-date')
        # if pub-date is not found then loop is skipped
        for pub_date in pub_dates:
           pub_type = pub_date.get('pub-type') 
           print pub_type
           if pub_type == 'collection':
                year = pub_date.find('./year')
                if year is not None:
                    # then it was found
                    meta_dict['date'] = year.text
                else:
                    meta_dict['date'] = None
    
        meta_list.append(meta_dict)
    
        # construct ayjid
        meta_dict['ayjid'] = rd.create_ayjid(**meta_dict)
    
        # citations
        citations_list = []
    
        # element-citation handling different from mixed-citation handling
        citations = article.findall('./back/ref-list/ref/element-citation')
        for cite in citations:
            cite_dict = ds.new_meta_dict()
            
            # simple meta data
            for key in cit_meta_loc.iterkeys():
                key_data = cite.find(cit_meta_loc[key]) 
                if key_data is not None:
                    meta_dict[key] = key_data.text
                else:
                    meta_dict[key] = None
    
            # doi and pmid
            pub_id = cite.find('./pub-id')
            if pub_id is not None:
                pub_id_type = pub_id.get('pub-id-type')
                if pub_id_type == 'doi':
                    cite_dict['doi'] = pub_id.text
                elif pub_id_type == 'pmid':
                    cite_dict['pmid'] = pub_id.text
    
            # aulast and auinit
            cite_aulast = []
            cite_auinit = []
            
            # determine if person group is authors
            person_group = cite.find('./person-group')
            if person_group is not None:
                group_type = person_group.get('person-group-type')
            else:
                group_type = None
    
            # then add the authors to the cite_dict
            if group_type == 'author':
                names = person_group.findall('./name')
                for name in names:
                    # add surname
                    surname = name.find('./surname')
                    if surname is not None:
                        # then it was found
                        cite_aulast.append(surname.text)
                    else:
                        cite_aulast.append(None)
    
                    # add given names
                    given_names = name.find('./given-names')
                    if given_names is not None:
                        # then it was found
                        cite_auinit.append(given_names.text[0])
                    else:
                        cite_auinit.append(None)
    
            if not cite_aulast:
                # then empty
                cite_aulast = None
            if not cite_auinit:
                # then empty
                cite_auinit = None
    
            cite_dict['aulast'] = cite_aulast
            cite_dict['auinit'] = cite_auinit
    
            citations_list.append(cite_dict)
        # end cite loop
    
        meta_dict['citations'] = citations_list
    
        meta_list.append(meta_dict)
    # end article loop
    
    return meta_list
    return None

def expand_pubmed(meta_list):
    """
    Given a list of first-level meta dicts and their second-level meta dicts,
    first['citations'], expand the network by adding the second-level meta
    dicts to the first level. That is, for the second-level meta dicts with
    sufficient information (either a DOI, PubMed ID, enough metadata to
    query for a DOI, etc.), query PubMed for their more expansive set 
    of meta data, most notably their citation data, parse the associated xml, 
    and append their meta_dicts to the meta_list.

    Args:
        meta_list (list): A list of meta_dict dictionaries.
    
    Returns:
        list.  A list of meta_dict dictionaries.

    Notes:
        (and do something about the redundent information about them stored
        still in the first level?)
    """

def parse_bib(filename):
    """
    Args:
        filename (str): Path to BibTex file.
    
    Returns:
        list. A list of meta_dict dictionaries.
    
    Warning: tethne.bib has been known to make errors in parsing bib files
    FIXME: structure the bibtex translator in the data_struct folder
    along with the others.
    """
    import tethne.bib as bb

    #load file into bib.py readable format
    data = ""
    with open(filename,'r') as f:
        for line in f:
            line = line.rstrip()
            data += line + "\n"

    #parse the bibtex file into a dict (article) of dicts (article meta)
    data = bb.clear_comments(data)
    bib = bb.Bibparser(data)
    bib.parse()

    #convert data into a list of tethne meta_dict
    translator = {'doi':'doi',
                  'author':'aulast',
                  'title':'atitle',
                  'journal':'jtitle',
                  'volume':'volume',
                  'year':'date'}
    bib_list = []
    for record in bib.records.itervalues():
        meta_dict = ds.new_meta_dict()
        meta_dict['file'] = filename
        for key, value in record.iteritems():
            translator_keys = translator.keys()
            if key in translator_keys:
                meta_key = translator[key]
                meta_dict[meta_key] = value
        bib_list.append(meta_dict)

    #perform the non-simple convertions
    for meta_dict in bib_list:
        if meta_dict['aulast'] is not None:
            aulast = []
            auinit = []
            for name_dict in meta_dict['aulast']:
                aulast.append(name_dict['family'])
                if 'given' in name_dict.keys():
                    auinit.append(name_dict['given'][0].upper())
                else:
                    auinit.append('')
            meta_dict['aulast'] = aulast
            meta_dict['auinit'] = auinit
        else:
            print 'Parser failed at', meta_dict

    return bib_list


