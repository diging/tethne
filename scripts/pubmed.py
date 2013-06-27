"""
Work in progress script to collect data from pubmed

See the following hyperlinks regarding possible structures of XML:
    http://www.ncbi.nlm.nih.gov/pmc/pmcdoc/tagging-guidelines/citations/v2/citationtags.html#2Articlewithmorethan10authors%28listthefirst10andaddetal%29
    http://dtd.nlm.nih.gov/publishing/
"""
import tethne.data_struct as ds
import tethne.readers as rd

filename = '/home/apoh/Repository/tethne/docs/pmc_result.xml'
import xml.etree.ElementTree as ET
tree = ET.parse(filename)
root = tree.getroot()

meta_list = []
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
        else:
            # if never found, remain at None from initialization
            pass

    # title
    title = article.find('./front/article-meta/title-group/article-title')
    if title is not None:
        # then article title was found
        meta_dict['atitle'] = title.text
    else:
        meta_dict['atitle'] = None

    # aulast and auinint
    aulast = []
    auinit = []
    contribs = article.findall('./front/article-meta/contrib-group/contrib')
    # if contrib is not found then loop is skipped
    for contrib in contribs:
        contrib_type = contrib.get('contrib-type')
        if contrib_type == 'author':
            surname = contrib.find('./name/surname')
            if surname is not None:
                # then it was found
                aulast.append(surname.text)
            else:
                aulast.append(None)

            # multiple given names? this takes first one
            given_name = contrib.find('./name/given-names')
            if given_name is not None:
                # then it was found
                auinit.append(given_name.text[0])
            else:
                auinit.append(None)
    meta_dict['aulast'] = aulast
    meta_dict['auinit'] = auinit

    # date
    pub_dates = article.findall('./front/article-meta/pub-date')
    # if pub-date is not found then loop is skipped
    for pub_date in pub_dates:
       pub_type = pub_date.get('pub-type') 
       print pub_type
       if pub_type == 'collection':
            year = pub_date.find('./year')
            if year is not None:
                # then it was found
                meta_dict['date'] = year.text
            else:
                meta_dict['date'] = None

    # jtitle
    jtitle = article.find('./front/journal-meta/journal-title-group/' +
                             'journal-title')
    if jtitle is not None:
        # then it was found
        meta_dict['jtitle'] = jtitle.text
    else:
        meta_dict['jtitle'] = None

    # volume
    volume = article.find('./front/article-meta/volume')
    if volume is not None:
        # then it was found
        meta_dict['volume'] = volume.text
    else:
        meta_dict['volume'] = None

    # issue
    issue = article.find('./front/article-meta/issue')
    if issue is not None:
        # then it was found
        meta_dict['issue'] = issue.text
    else:
        meta_dict['issue'] = None

    # spage
    fpage = article.find('./front/article-meta/fpage')
    if fpage is not None:
        # then it was found
        meta_dict['spage'] = fpage.text
    else:
        meta_dict['spage'] = None

    # epage
    lpage = article.find('./front/article-meta/lpage')
    if lpage is not None:
        # then it was found
        meta_dict['epage'] = lpage.text
    else:
        meta_dict['epage'] = None

    meta_list.append(meta_dict)

    # ayjid
    meta_dict['ayjid'] = rd.create_ayjid(**meta_dict)

    # citations
    citations = []
    references = article.findall('./back/ref-list/ref')
    for ref in references:
        ref_dict = ds.new_meta_dict()

        # aulast and auinit
        ref_aulast = []
        ref_auinit = []
        
        # determine if person group is authors
        person_group = ref.find('./element-citation/person-group')
        if person_group is not None:
            group_type = person_group.get('person-group-type')
        else:
            group_type = None

        # then add the authors to the ref_dict
        if group_type == 'author':
            names = person_group.findall('./name')
            for name in names:
                # add surname
                surname = name.find('./surname')
                if surname is not None:
                    # then it was found
                    ref_aulast.append(surname.text)
                else:
                    ref_aulast.append(None)

                # add given names
                given_names = name.find('./given-names')
                if given_names is not None:
                    # then it was found
                    ref_auinit.append(given_names.text[0])
                else:
                    ref_auinit.append(None)

        if not ref_aulast:
            # then empty
            ref_aulast = None
        if not ref_auinit:
            # then empty
            ref_auinit = None

        ref_dict['aulast'] = ref_aulast
        ref_dict['auinit'] = ref_auinit

        # atitle
        article_title = ref.find('./element-citation/article-title')
        if article_title is not None:
            # then it was found
            ref_dict['atitle'] = article_title.text
        else:
            ref_dict['atitle'] = None

        # jtitle
        source = ref.find('./element-citation/source')
        if source is not None:
            # then it was found
            ref_dict['jtitle'] = source.text
        else:
            ref_dict['jtitle'] = None

        # date
        year = ref.find('./element-citation/year')
        if year is not None:
            # then it was found
            ref_dict['date'] = year.text
        else:
            ref_dict['date'] = None

        # volume
        volume = ref.find('./element-citation/volume')
        if volume is not None:
            # then it was found
            ref_dict['volume'] = volume.text
        else:
            ref_dict['volume'] = None

        # spage
        fpage = ref.find('./element-citation/fpage')
        if fpage is not None:
            # then it was found
            ref_dict['spage'] = fpage.text
        else:
            ref_dict['spage'] = None

        # epage
        lpage = ref.find('./element-citation/lpage')
        if lpage is not None:
            # then it was found
            ref_dict['epage'] = lpage.text
        else:
            ref_dict['epage'] = None

        # doi and pmid
        ref_ids = ref.findall('./element-citation/pub-id')
        for ref_id in ref_ids:
           id_type = ref_id.get('pub-id-type')
           if id_type == 'doi':
               ref_dict['doi'] = ref_id.text 
           elif id_type == 'pmid':
               ref_dict['pmid'] = ref_id.text

        citations.append(ref_dict)
    # end ref loop

    meta_dict['citations'] = citations

#for meta_dict in meta_list:
#    for citation_dict in meta_dict['citations']:
#        print citation_dict
