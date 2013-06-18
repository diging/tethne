"""
Each file reader takes an input file from an academic knowledge database
such as the Web of Science or PubMed and parses the input file into a
list of "meta_dict" dictionaries for each paper with as many as possible of 
the following keys; missing values are set to None
    aulast  - authors' last name as a list
    auinit  - authors' first initial as a list
    atitle  - article title
    jtitle  - journal title or abbreviated title
    volume  - journal volume number
    issue   - journal issue number
    spage   - starting page of article in journal
    epage   - ending page of article in journal
    date    - article date of publication
These keys are associated with the meta data entries in the databases of 
organizations such as the International DOI Foundation and its Registration
Agencies such as CrossRef and DataCite

In addition, meta_dict dictionaries will contain keys with information 
relevant to the networks of interest for Tethne including
    citations   - a list of minimum meta_dict dictionaries for cited references
    ayjid       - First author's last name, initial the publication year and
                  the journal published in
    doi         - Digital Object Identifier 
    pmid        - PubMed ID
    wosid       - Web of Science UT fieldtag
Missing data here also results in the above keys being set to None
"""
import data_struct as ds

def parse_wos(filepath):
    """
    Read Web of Science plain text data
    Input:
        filepath - a filepath to the Web of Science plain text file
    Output:
        wos_list
            a list of dictionaries each associated with a paper from 
            the Web of Science with keys from docs/fieldtags.txt
            as encountered in the file; most values associated with
            keys are strings with special exceptions defined by
            the list_keys and int_keys variables
    Notes:
        Unknown keys: RI, OI, Z9
        :copyright: (c) 2013 Aaron Baker
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
    Support the Web of Science reader by converting the strings found
    at the CR field tag of a record into a minimum meta_dict dictionary 
    Input   - CR field tag data from a plain text Web of Science file
    Output  - meta_dict dictionary
    Notes
        Needs a sophisticated name parser, would like to use an open source
        resource for this
        If WoS is missing a field in the middle of the list there are NOT
        commas indicating that; the following example does NOT occur
            Doe J, ,, Some Journal
        instead
            Doe J, Some Journal
        this threatens the integrity of WoS data; should we address it?
        Another threat: if WoS is unsure of the DOI number there will be
        multiple DOI numbers in a list of form [doi1, doi2, ...], address this?
        :copyright: (c) 2013 Aaron Baker
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

def create_ayjid(aulast='', auinit='', date='', jtitle='', **kwargs):
    """
    Convert aulast, auinit, and jtitle into the fuzzy identifier ayjid
    Returns 'Unknown paper' if all id components are missing (None)
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


def wos2meta(wos_data):
    """
    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a meta_dict dictionary or list of
    dictionaries, the standard for Tethne
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

        #more complicated translations
        #FIXME: not robust to all names, organziation authors, etc.
        if wos_dict['AU'] is not None:
            aulast_list = []
            auinit_list = []
            for name in wos_dict['AU']:
                name_tokens = name.split(',')
                aulast = name_tokens[0]
                auinit = name_tokens[1][1] #1 b/c of 'aulast, aufirst'
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


def parse_bib(filename):
    """
    Warning: tethne.bib has been known to make errors in parsing bib files
    FIXME: structure the bibtex translator in the data_struct folder
    along with the others
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


def build(filename):
    """
    Reads Web of Science data file (see docs/savedrecs.txt for sample), and 
    builds a list of wos_objects.
    Input: 
        filename - A WoS data file filepath string
    Output:
        wos_list - A list of dictionaries with the following keys:
        AU          - authors of the paper 
        year        - publication year
        identifier  - CR-like string
        wosid       - Web of Science Accession Number
        journal     - journal name
        title       - article title
        citations   - a list of citations in 'CR' format
    """
    wos_list = []

    with open(filename, 'r') as f:
        cache = {}
        for line in f:
            # AJB consider using f.splitlines() instead of this for loop
            line = line.replace("\n","").replace("\r","")

            # extract line's 2-letter prefix for information about the 
            # record and handle "bad" prefixes
            if len(line) > 1:
                # has a prefix
                prefix = line[0:2]      
            else:
                # doesn't have a prefix; make special one to ignore
                prefix = 'XX'           
            if prefix == 'EF':          
                # At the end of the data file 
                break
            if prefix == 'ER':          
                # At the end of a record (paper), create CR-like identifier
                identifier = cache['AU'][0].replace(",","") + ", " + cache['PY'][0] + ", " + cache['J9'][0] 
                identifier = identifier.upper()
                 
                # TODO: Need to figure out why I did this....
                num_authors = 0
                authors = {}
                for au in cache['AU']:
                    num_authors += 1
                    found = 'false'
                    au_last = au.split(',')[0]
                    for af in cache['AF']:
                        af_last = af.split(',')[0]
                        if au_last.upper() == af_last.upper():
                            authors[au] = af
                            found = 'true'
                    if found != 'true':             # Maybe there is no AF entry
                        authors[au] = au
                cache['num_authors'] = num_authors
        
                title = ''
                for row in cache['TI']:             # Some titles bleed over into multiple rows
                    title += row
        
                #rather than making an object make a dict
                #DO NOT continue changing these key names as authors was
                #changed from 'authors' to 'AU'; as more sources are
                #incorporated they will have various input formats to deal
                #with. we should move towards a mneumonic system
                #rather than base everything on the (poor) WoS key system
                wos_dict = {'aulast':authors,
                            'date':int(cache['PY'][0]),
                            'identifier':identifier,
                            'wosid':cache['UT'][0],
                            'jtitle':cache['SO'][0],
                            'atitle':title,
                            'citations':cache['CR']}
                wos_list.append(wos_dict)
        
                cache = {}              # Dump for next record
                cache['CR'] = None      # Prevents a KeyError if the record has no references.

            else:
                # We're still in the middle of a record...
                if (prefix != 'XX') and (prefix != ''):
                    if prefix == '  ':
                        # there is no prefix, the line is part of the field
                        # to which the previous line belonged.
                        prefix = last_prefix
                    else:
                        # there is a prefix, and the line starts the next 
                        # field in the record
                        cache[prefix] = []

                    if prefix != 'XX':
                        # the line was probably blank
                        line_cache = line[3:].replace(".", "").upper()
                        
                        if prefix == 'CR':
                            # store the citation record (CR) in a list 
                            line_split = line_cache.split(",")
                            if len(line_split) > 3:    
                                # extract the first three fields:
                                # author, year, and journal/title
                                line_cache = (line_split[0] + "," + 
                                              line_split[1] + "," + 
                                              line_split[2])

                        cache[prefix].append(line_cache)
                    # end "not XX" if
            # end "middle of record" else
            last_prefix = prefix
        #end line loop
    #end file read
    return wos_list
