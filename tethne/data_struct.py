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
    meta_dict = {'aulast':None,
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
                 'wosid':None}
    
    return meta_dict


def new_query_dict():
    """
    Declares only those keys of meta_dict that are query-able through CrossRef.
    """
    q_dict = {'aulast':None,
              'auinit':None,
              'atitle':None,
              'address':None, 
              'jtitle':None,
              'volume':None,
              'issue':None,
              'spage':None,
              'epage':None,
              'date':None} 

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
    wos_dict = {'DI':None,
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
                'CR':None}

    return wos_dict

def wos2meta_map():
    """
    Defines the direct relationships between the wos_dict and the meta_dict.
    
    Returns
    -------
    translator : dict
        A 'translator' dictionary.
        
    """
    translator = {'DI':'doi',
                  'TI':'atitle',
                  'SO':'jtitle',
                  'C1':'address',
                  'VL':'volume',
                  'IS':'issue',
                  'BP':'spage',
                  'EP':'epage',
                  'PY':'date',
                  'UT':'wosid'}

    return translator


