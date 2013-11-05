class Paper():
    """
    Base class for Papers. Enforces a limited vocabulary of keys, and specific
    data types.
    
    Should be used in place of data_struct.new_meta_dict(), below.
    """
    
    def __init__(self):
        """
        Defines keys, and acceptable data types for values.
        """
        self.meta_dict = {
                            'aulast':None,
                            'auinit':None,
                            'institution':None,
                            'atitle':None,
                            'jtitle':None,
                            'volume':None,
                            'issue':None,
                            'spage':None,
                            'epage':None,
                            'date':None,
                            'citations':None,
                            'country':None,
                            'ayjid':None,
                            'doi':None,
                            'pmid':None,
                            'wosid':None    }
    
        self.list_fields = [ 'aulast', 
                             'auinit', 
                             'institution', 
                             'citations' ]
        
        self.string_fields = [ 'atitle', 
                               'jtitle', 
                               'volume', 
                               'issue', 
                               'spage', 
                               'epage', 
                               'ayjid', 
                               'doi', 
                               'pmid', 
                               'wosid' ]
        
        self.int_fields = [ 'date' ]
    
    def __setitem__(self, key, value):
        """
        Enforces limited vocabulary of keys, and acceptable data types for
        values.
        """
        
        if key not in self.meta_dict.keys():
            raise KeyError(str(key) + " is not a valid key in Paper meta_dict.")
        elif key in self.list_fields and type(value) is not list:
                raise ValueError("Value for key "+str(key)+" must be a list.")
        elif key in self.string_fields and type(value) is not str:
                raise ValueError("Value for key "+str(key)+" must be a string.")
        elif key in self.int_fields and type(value) is not int:
                raise ValueError("Value for key "+str(key)+" must be an integer.")              
        else:
            self.meta_dict[key] = value
        
    def __getitem__(self, key):
        """Passes through to core dictionary."""
        return self.meta_dict[key]
    
    def __delitem__(self, key):
        """Passes through to core dictionary."""
        del self.meta_dict[key]
    
    def __len__(self):
        """Passes through to core dictionary."""
        return len(self.meta_dict)
    
    def keys(self):
        """Passes through to core dictionary."""
        return self.meta_dict.keys()
    
    def values(self):
        """Passes through to core dictionary."""
        return self.meta_dict.values()
    
    def iteritems(self):
        """Passes through to core dictionary."""
        return self.meta_dict.iteritems()
    

def new_meta_dict():
    """
    Creates a Meta Dictionary of citation data values. 
    This function has the most common values from citation data sources like WebOfScience,PubMed etc.,
    
    Returns
    --------
    meta_list : list
        A meta_list dictionary with 'None' as default values.
    
    Notes
    -----
    * aulast -- authors' last name as a list.
    * auinit -- authors' first initial as a list.
    * institution -- institutions with which the authors are affiliated.
    * atitle -- article title
    * jtitle -- journal title or abbreviated title
    * volume -- journal volume number
    * issue -- journal issue number
    * spage -- starting page of article in journal
    * epage -- ending page of article in journal
    * date -- article date of publication
    * country -- country with which the authors are affiliated.
    * citations -- a list of minimum meta_dict dictionaries for cited references
    * ayjid -- First author's last name, initial the publication year and the 
        journal published in
    * doi -- Digital Object Identifier 
    * pmid -- PubMed ID
    * wosid -- Web of Science UT fieldtag
    
    """
    meta_dict = {
                    'aulast':None,
                    'auinit':None,
                    'institution':None, #
                    'atitle':None,
                    'jtitle':None,
                    'volume':None,
                    'issue':None,
                    'spage':None,
                    'epage':None,
                    'date':None,
                    'citations':None,
                    'country':None, #
                    'ayjid':None,
                    'doi':None,
                    'pmid':None,
                    'wosid':None    }
    
    return meta_dict


def new_query_dict():
    """
    Declares only those keys of meta_dict that are query-able through CrossRef.
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


def new_wos_dict():
    """
    Defines the set of field tags that will try to be converted into a meta_dict
    and intializes them to 'None'.
   
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
                    'CR':None   }

    return wos_dict

def wos2meta_map():
    """
    Defines the direct relationships between the wos_dict and the meta_dict.
    
    Returns
    -------
    translator : dict
        A 'translator' dictionary.
        
    """
    translator = {
                    'DI':'doi',
                    'TI':'atitle',
                    'SO':'jtitle',
                    'C1':'address',
                    'VL':'volume',
                    'IS':'issue',
                    'BP':'spage',
                    'EP':'epage',
                    'PY':'date',
                    'UT':'wosid'    }

    return translator


