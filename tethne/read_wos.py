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
 

