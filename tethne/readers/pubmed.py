"""
Methods for working with PubMed data are still under development. Please use
with care.

.. autosummary::

   read

"""

import tethne.data as ds
import xml.etree.ElementTree as ET


# PubMed functions
def _pubmed_file_id(filename):
    """Future (not implemented).

    Given a filename (presumed to contain PubMed compatible IDs)
    return an xml string for each article associated with that ID.

    Parameters
    ----------
    filename : string
        Path to a file containing PubMed-compatible IDs.

    Returns
    -------
    list : list
        A list of XML strings.

    """

    return None

def read(filepath):
    """
    Given a file with PubMed XML, return a list of :class:`.Paper` instances.

    See the following hyperlinks regarding possible structures of XML:
    * http://www.ncbi.nlm.nih.gov/pmc/pmcdoc/tagging-guidelines/citations/v2/citationtags.html#2Articlewithmorethan10authors%28listthefirst10andaddetal%29
    * http://dtd.nlm.nih.gov/publishing/
    
    **Usage**
    
    .. code-block:: python
    
       >>> import tethne.readers as rd
       >>> papers = rd.pubmed.read("/Path/to/PubMedData.xml")

    Parameters
    ----------
    filepath : string
        Path to PubMed XML file.

    Returns
    -------
    meta_list : list
        A list of :class:`.Paper` instances.
    """

    try:
        with open(filepath,'r') as f:
            tree = ET.fromstring(text, parser)(filepath)
            root = tree.getroot()

    except IOError: # File does not exist, or couldn't be read.
        raise IOError("File does not exist, or cannot be read.")

    # define location of simple article meta data relative to xml tree rooted
    # at 'article'
    meta_loc = {'atitle':'./front/article-meta/title-group/article-title',
                'jtitle':('./front/journal-meta/journal-title-group/' +
                          'journal-title'),
                'volume':'./front/article-meta/volume',
                'issue':'./front/article-meta/issue',
                'spage':'./front/article-meta/fpage',
                'epage':'./front/article-meta/lpage'}

    # location relative to element-citation element
    cit_meta_loc = {'atitle':'./article-title',
                    'jtitle':'./source',
                    'date':'./year',
                    'volume':'./volume',
                    'spage':'./fpage',
                    'epage':'./epage'}

    meta_list = []
    for article in root.iter('article'):
        meta_dict = ds.Paper()

        # collect information from the 'front' section of the article
        # collect the simple data
        for key in meta_loc.iterkeys():
            key_data = article.find(meta_loc[key])
            if key_data is not None:
                meta_dict[key] = key_data.text
            else:
                meta_dict[key] = None

        # collect doi and pmid
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

        # collect aulast and auinint
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

        # collect date
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

        meta_list.append(meta_dict)

        # construct ayjid
        meta_dict['ayjid'] = create_ayjid(**meta_dict)

        # citations
        citations_list = []

        # element-citation handling different from mixed-citation handling
        citations = article.findall('./back/ref-list/ref/element-citation')
        for cite in citations:
            cite_dict = ds.Paper()

            # simple meta data
            for key in cit_meta_loc.iterkeys():
                key_data = cite.find(cit_meta_loc[key])
                if key_data is not None:
                    meta_dict[key] = key_data.text
                else:
                    meta_dict[key] = None

            # doi and pmid
            pub_id = cite.find('./pub-id')
            if pub_id is not None:
                pub_id_type = pub_id.get('pub-id-type')
                if pub_id_type == 'doi':
                    cite_dict['doi'] = pub_id.text
                elif pub_id_type == 'pmid':
                    cite_dict['pmid'] = pub_id.text

            # aulast and auinit
            cite_aulast = []
            cite_auinit = []

            # determine if person group is authors
            person_group = cite.find('./person-group')
            if person_group is not None:
                group_type = person_group.get('person-group-type')
            else:
                group_type = None

            # then add the authors to the cite_dict
            if group_type == 'author':
                names = person_group.findall('./name')
                for name in names:
                    # add surname
                    surname = name.find('./surname')
                    if surname is not None:
                        # then it was found
                        cite_aulast.append(surname.text)
                    else:
                        cite_aulast.append(None)

                    # add given names
                    given_names = name.find('./given-names')
                    if given_names is not None:
                        # then it was found
                        cite_auinit.append(given_names.text[0])
                    else:
                        cite_auinit.append(None)

            if not cite_aulast:
                # then empty
                cite_aulast = None
            if not cite_auinit:
                # then empty
                cite_auinit = None

            cite_dict['aulast'] = cite_aulast
            cite_dict['auinit'] = cite_auinit

            citations_list.append(cite_dict)
        # end cite loop

        meta_dict['citations'] = citations_list

        meta_list.append(meta_dict)
    # end article loop

    return meta_list

def _expand_pubmed(meta_list):
    """Future (not implemented).

    Given a list of first-level meta dicts and their second-level meta dicts,
    first['citations'], expand the network by adding the second-level meta
    dicts to the first level. That is, for the second-level meta dicts with
    sufficient information (either a DOI, PubMed ID, enough metadata to
    query for a DOI, etc.), query PubMed for their more expansive set
    of meta data, most notably their citation data, parse the associated xml,
    and append their :class:`.Paper` to the meta_list.

    Parameters
    ----------
    meta_list : list
        A list of :class:`.Paper` instances.

    Returns
    -------
    list : list
        A list of :class:`.Paper` instances.

    Notes
    -----
    Do something about the redundent information about them stored still in the
    first level?

    """
    pass
