import urllib
import tethne.utilities as util
import tethne.data_struct as ds

def pubmed_pmid(pmid):
    """
    Return XML from a query of PubMed's EFetch database for the pmid.

    Notes
    -----
    Update this to query db = pmc instead: pmc contains citation data while
    pubmed does not.
    """
    url_string = ('http://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?' +
                  'db=pubmed&' +
                  'id=' + str(pmid) + '&' + 
                  'retmode=xml')

    f = urllib.urlopen(url_string)
    xml_string = f.read()
    f.close()

    return xml_string


def crossref_meta(**kwargs):
    """
    Query CrossRef with article metadata with the hope to find a DOI number 
    for that metadata in their system. 
    
    Inputs
    ------
    * aulast -- first author's last name
    * auinit -- first author's first initial
    * atitle -- article title
    * jtitle -- journal title or abbreviated title
    * volume -- journal volume number
    * issue -- journal issue number
    * spage -- starting page of article in journal
    * epage -- ending page of article in journal
    * date -- article date of publication

    Returns a DOI as a string

    Notes
    -----
    A sample query is given here:
    
    http://www.crossref.org/openurl?pid=git.tethne@gmail.com&url_ver=Z39.88-2004&rft_val_fmt=info:ofi/fmt:kev:mtx:journal&rft.atitle=Isolation%20of%20a%20common%20receptor%20for%20coxsackie%20B&rft.jtitle=Science&rft.aulast=Bergelson&rft.auinit=J&rft.date=1997&rft.volume=275&rft.issue=5304&rft.spage=1320&rft.epage=1323&redirect=false

    More information is available at the CrossRef documentation site: http://help.crossref.org/#home
    
    See "Machine Interfaces / APIs" in particular.
    
    """
    valid_keys = ds.new_query_dict().keys()
    q_dict = util.subdict(kwargs, valid_keys)
    #handle keys in meta_dict that are lists...
    if q_dict['aulast'] is not None:
        q_dict['aulast'] = q_dict['aulast'][0]
    if q_dict['auinit'] is not None:
        q_dict['auinit'] = q_dict['auinit'][0]

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
    for key, value in q_dict.iteritems():
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
    try:
        doi = query.find('{http://www.crossref.org/qrschema/2.0}doi').text
    except AttributeError:
        #then doi not found
        doi = None

    return doi
