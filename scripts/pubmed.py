"""
Work in progress script to collect data from pubmed
"""
import tethne.data_struct as ds

filename = '/home/apoh/Repository/tethne/docs/pmc_result.xml'
import xml.etree.ElementTree as ET
tree = ET.parse(filename)
root = tree.getroot()

for article in root.iter('article'):
    meta_dict = ds.new_meta_dict()

    # collect information from the 'front' section of the article
    # doi and pmid in article/front/article-meta/article-id
    id_list = article.findall('./front/article-meta/article-id')
    for identifier in id_list:
        id_type = identifier.get('pub-id-type')
        if id_type == 'doi':
            meta_dict['doi'] = identifier.text 
        elif id_type == 'pmid':
            meta_dict['pmid'] = identifier.text

    # atitle in article/front/article-meta/title-group/article-title
    title = article.find('./front/article-meta/title-group/article-title').text
    meta_dict['atitle'] = title

    # aulast in article/front/article-meta/contrib-group/contrib/
    #               name/surname
    aulast = []
    # auinit in article/front/article-meta/contrib-group/contrib/
    #               name/given-names
    auinit = []
    contribs = article.findall('./front/article-meta/contrib-group/contrib')
    for contrib in contribs:
        contrib_type = contrib.get('contrib-type')
        if contrib_type == 'author':
            surname = contrib.find('./name/surname').text
            # multiple given names? this takes first one
            given_name = contrib.find('./name/given-names').text
            aulast.append(surname)
            auinit.append(given_name[0])

    # date
    pub_dates = article.findall('./front/article-meta/pub-date')
    for pub_date in pub_dates:
       pub_type = pub_date.get('pub-type') 
       if pub_type == 'collection':
            year = pub_date.text
            meta_dict['date'] = year


    # jtitle
    # volume
    # issue
    # spage
    # epage
