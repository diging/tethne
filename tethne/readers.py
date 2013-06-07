def read_wos(filepath):
    """
    A file reader for Web of Science plain text data
    Input:
        filepath - a filepath to the Web of Science plain text file
    Output:
        wos_data - a list of dictionaries each associated with a paper
            from the Web of Science
    Notes:
        keys may be found in the docs folder
        C1=Address may need some kind of address parser
        RP=Reprint address as well
        main identifier will be the DOI number not WOS number,
            DOI found on CR and as key DI for primary record
        Unknown keys:
            RI, OI, Z9
        If DOI is on reference sheet, may be confident that the reference
            also exists in the Web of Science; the inverse is not true:
            for example, the El-Fadel paper in savedrecs.txt cites
            a paper by Al-Rabeh titled A Stochastic Simulation...
            the latter has a DOI, but not on the reference list, it exists
            in the Web of Science, but it is not acknowledged as cited by
            the El-Fadel paper
    """
    wos_data = []

    #define special key handling
    file_start_key = 'FN'
    file_end_key = 'EF'
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
            key_contents = paper_dict[key]
            if delim != '\n':
                #we dont want the newline characters
                key_contents = key_contents.strip('\n')
            paper_dict[key] = key_contents.split(delim)

    return wos_data

class wos_object:
    """
    Each entry in the WoS data file becomes a wos_object
    Arguments:
        authors - A dictionary that maps CR-like to AF-like.
        pub_year -
        identifier -- A CR-like string, e.g. "Last FM, 2012, J EXP BIOL, V210".
        wosid -
        journal - 
        doc_type -
        meta -- A dictionary, containing anything.
        title -
        citations -- A list of identifiers
    """

    def __init__(self, authors, pub_year, identifier, wosid, journal, doc_type,                     meta, title, citations):
        self.authors = authors
        self.year = pub_year
        self.identifier = identifier
        self.wosid = wosid
        self.journal = journal
        self.doc_type = doc_type
        self.meta = meta
        self.title = title
        self.citations = citations
 
def build(filename):
    """
    Reads Web of Science data file (see docs/savedrecs.txt for sample), and 
    builds a list of wos_objects.
    Input: 
        filename - A WoS data file filepath string
    Output:
        wos_list - A list of wos_objects containing data in the file
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
        
                wos_list.append(wos_object(authors, int(cache['PY'][0]), identifier, cache['UT'][0], cache['SO'][0], cache['DT'][0], cache, title, cache['CR']))
        
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
 

