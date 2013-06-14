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
    ayid        - First author's last name and the publication year
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
        wos_data
            a list of dictionaries each associated with a paper from 
            the Web of Science with keys from docs/fieldtags.txt
            as encountered in the file; most values associated with
            keys are strings with special exceptions defined by
            the list_keys and int_keys variables
    Notes:
        Unknown keys: RI, OI, Z9
        :copyright: (c) 2013 Aaron Baker
    """
    wos_data = []

    #define special key handling
    paper_start_key = 'PT'

    #try to read filepath
    line_list = []
    with open(filepath,'r') as f:
        line_list = f.read().splitlines()
    if len(line_list) is 0:
        raise IOError("Unable to read filepath or filepath is empty")

    #convert the data in the file to a usable list of dictionaries
    #note: first two lines of file are not related to any paper therein
    paper_dict = {}
    last_field_tag = paper_start_key #initialize to something
    for line in line_list[2:]:
        field_tag = line[:2]
        if field_tag == paper_start_key:
            if paper_dict:
                #is not empty; add paper data to our list
                wos_data.append(paper_dict)
            #regardless, prepare for next paper
            paper_dict = {}

        #handle keys like AU,AF,CR that continue over many lines
        if field_tag == '  ':
            field_tag = last_field_tag

        #add value for the key to the paper_dict: the rest of the line
        try:
            paper_dict[field_tag] += str(line[3:]) + '\n'
        except KeyError:
            #key didn't exist already, can't append but must create
            paper_dict[field_tag] = str(line[3:]) + '\n'

        last_field_tag = field_tag

    #define keys that should be lists instead of default string
    list_keys = ['AU','AF','DE','ID','CR']
    delims = {'AU':'\n',
              'AF':'\n',
              'DE':';',
              'ID':';',
              'CR':'\n'
             }

    #and convert the data at those keys into lists
    for paper_dict in wos_data:
        for key in list_keys:
            delim = delims[key]
            try:
                key_contents = paper_dict[key]
                if delim != '\n':
                    #we dont want the newline characters
                    key_contents = key_contents.strip('\n')
                paper_dict[key] = key_contents.split(delim)
            except KeyError:
                #one of the keys to be converted to a list didn't exist
                pass

    #similarly convert some data from string to int
    int_keys = ['PY']
    for paper_dict in wos_data:
        for key in int_keys:
            try:
                paper_dict[key] = int(paper_dict[key])
            except KeyError:
                #one of the keys to be converted to an int didn't exist
                pass

    return wos_data


def parse_cr(ref):
    """
    Support the Web of Science reader by converting the strings found
    at the CR field tag of a record into a minimum meta_dict dictionary 
    Input   - CR field tag data from a plain text Web of Science file
    Output  - meta_dict dictionary
    Notes
        Needs a sophisticated name parser, would like to use an open source
        resource for this
        :copyright: (c) 2013 Aaron Baker
    """
    meta_dict = {}
    #tokens of form: aulast auinit, date, jtitle, volume, spage, doi
    tokens = ref.split(',')
    try:
        #strip initial characters based on the field (spaces, 'V', 'DOI')
        meta_dict['aulast'] = tokens[0]
        meta_dict['date'] = int(tokens[1][1:])
        meta_dict['jtitle'] = tokens[2][1:]
        meta_dict['volume'] = tokens[3][2:]
        meta_dict['spage'] = tokens[4][2:]
        meta_dict['doi'] = tokens[5][5:]
    except IndexError:
        #ref did not have enough data
        pass

    return meta_dict


def wos_meta(wos_data):
    """
    Convert a dictionary or list of dictionaries with keys from the
    Web of Science field tags into a meta_dict dictionary or list of
    dictionaries, the standard for Tethne
    """
    #create a meta_dict for each paper_dict and append to this list
    wos_meta = []

    #handle dict inputs by converting to a 1-item list
    if type(wos_data) is dict:
        wos_data = [wos_data]

    #perform key convertions
    for paper_dict in wos_data:
        meta_dict = {}

        try:
            #aulast FIXME: not robust to all names, organziation authors, etc.
            name_list = []
            for name in paper_dict['AU']:
                name_tokens = name.split(',')
                aulast = name_tokens[0]
                name_list.append(aulast)
            meta_dict['aulast'] = name_list
            #auinit TODO
    
            #simple fields
            meta_dict['doi'] = paper_dict['DI']
            meta_dict['atitle'] = paper_dict['TI']
            meta_dict['jtitle'] = paper_dict['SO']
            meta_dict['volume'] = paper_dict['VL']
            meta_dict['issue'] = paper_dict['IS']
            meta_dict['spage'] = paper_dict['BP']
            meta_dict['epage'] = paper_dict['EP']
            meta_dict['date'] = paper_dict['PY']
    
            #additional fields
            #convert CR references into meta_dict format
            meta_cr_list = []
            for ref in paper_dict['CR']:
                meta_cr_list.append(parse_cr(ref))
            meta_dict['citations'] = meta_cr_list
        except KeyError:
            #missing Web of Science key
            pass

        wos_meta.append(meta_dict)
    #end paper_dict for loop

    return wos_meta


def parse_bib(filename):
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
