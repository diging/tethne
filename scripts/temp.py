"""
this script is a work in progress to test the new work flow of
wos_readers and the query system
"""

import tethne.readers as rd
import tethne.crossref as cr
filepath = "../docs/savedrecs.txt"
raw_records = rd.parse_wos(filepath)
meta_records = rd.wos_meta(raw_records)
print meta_records[0]['citations']
#determine number of DOI's missing from cited references
missing_doi_count = 0
for record in meta_records:
    for citation in record['citations']:
        try:
            test = citation['doi']
        except KeyError:
            missing_doi_count += 1
print missing_doi_count

#try to query for new DOI's
for record in meta_records:
    for citation in record['citations']:
        try:
            test = citation['doi']
        except KeyError:
            doi = cr.query(**citation)
            print doi
            citation['doi'] = doi

