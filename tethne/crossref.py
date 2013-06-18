def query(aulast=None, auinit=None, atitle=None, jtitle=None, volume=None, 
          issue=None, spage=None, epage=None, date=None):
    """
    Query CrossRef with article metadata with the hope to find a DOI number 
    for that metadata in their system. 
    Inputs:
        aulast  - first author's last name
        auinit  - first author's first initial
        atitle  - article title
        jtitle  - journal title or abbreviated title
        volume  - journal volume number
        issue   - journal issue number
        spage   - starting page of article in journal
        epage   - ending page of article in journal
        date    - article date of publication
    Returns a DOI number as a string

    Notes:
        A sample query is given here:
        http://www.crossref.org/openurl?pid=git.tethne@gmail.com&url_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.atitle=Isolation%20of%20a%20common%20receptor%20for%20coxsackie%20B&rft.jtitle=Science&rft.aulast=Bergelson&rft.auinit=J&rft.date=1997&rft.volume=275&rft.issue=5304&rft.spage=1320&rft.epage=1323&redirect=false

    More information is available at the CrossRef documentation site:
        http://help.crossref.org/#home
    See "Machine Interfaces / APIs" in particular.

    :copyright: (c) 2013 Aaron Baker
    """
    args = locals()

    #user account information and query type information at crossref
    pid = 'git.tethne@gmail.com'
    url = ('http://www.crossref.org/openurl?' +
            'pid=' + pid +
            '&url_ver=Z39.88-2004&' + 
            '&rft_val_fmt=info:ofi/fmt:kev:mtx:journal')

    #(incomplete but expected) URL encodings
    encodings = {
        ';':'%3B',
        '/':'%2F',
        '?':'%3F',
        ':':'%3A',
        '@':'%40',
        '=':'%3D',
        '&':'%26',
        ' ':'%20'}
 
    #build remaining url based on inputs
    for key, value in args.iteritems():
        if value is not None:
            value = str(value)

            #encode special characters
            for character, encoding in encodings.iteritems():
                value = value.replace(character,encoding)

            #and add to the URL
            url += '&rft.' + key + '=' + value

    #special redirect key
    url += '&redirect=false'

    #visit url 
    xml_string = ''
    import urllib
    f = urllib.urlopen(url)
    xml_string = f.read()
    f.close()

    #and from the xml extract a doi
    import xml.etree.ElementTree as ET 
    root = ET.fromstring(xml_string)
    query = root.find('.//{http://www.crossref.org/qrschema/2.0}query')
    doi = query.find('{http://www.crossref.org/qrschema/2.0}doi')

    return doi.text
