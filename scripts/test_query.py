"""
This short script illustrates how to improve a set of document's identifiers
by querying CrossRef for DOI numbers based on document meta data 
"""
import tethne.readers as rd
filepath = "../docs/savedrecs.txt"
wos_list = rd.parse_wos(filepath)
meta_list = rd.wos2meta(wos_list)

import tethne.crossref as cr
#query for doi numbers on the main documents of the meta_list
for doc in meta_list:
    if doc['doi'] is None:
        doi = cr.query(**doc)
        doc['doi'] = doi

#query for doi numbers on the citations of those documents
for doc in meta_list:
    for citation in doc['citations']:
        if citation['doi'] is None:
            doi = cr.query(**citation)
            if doi is not None:
                citation['doi'] = doi
            print citation
