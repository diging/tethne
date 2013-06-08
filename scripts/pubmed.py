"""
Work in progress script to collect data from pubmed
"""

filename = '/home/apoh/Repository/tethne/docs/pmc_result.xml'
import xml.etree.ElementTree as ET
tree = ET.parse(filename)
root = tree.getroot()

for article in root.iter('article'):
    title = article.find('.//article-title').text
    authors = []
    for contrib in article.iter('contrib'):
        if contrib.attrib['contrib-type'] == 'author':
            surname = contrib.find('.//surname').text
            given_name = contrib.find('.//given-names').text
            authors.append(surname + ", " + given_name)
    year = 0
    for pub_date in article.iter('pub-date'):
        if pub_date.attrib['pub-type'] == 'collection':
            year = pub_date.find('year').text

    references = []
    for ref in article.iter('ref'):
        identity = ref.attrib['id']
        references.append(identity)
            
    print title
    print authors
    print year
    print references
