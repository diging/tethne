"""
This class has functionalities to serialize a TETHNE corpus object  to persist in the database;

.. code-block:: python
>>> from tethne.serialize import paper

"""

import os
import json
import re

from tethne.dao import tethnedao
from time import gmtime, strftime
from tethne.utilities import _strip_punctuation


class SerializeUtility:

    @staticmethod
    def get_auth_inst(address):
        if ']' not in address:
            return address, None
        institute_literal = address.rsplit(']', 1)[1].lstrip()
        author_literal = address.rsplit(']', 1)[0].replace('[', '')
        authors = author_literal.split(';')
        return institute_literal, authors


class Serialize:
    """
    This class is used to serialize the Corpus object and has methods to create fixtures(JSON files)
    for different models in the TETHNE database.
    """

    paper_source_map = {3: 'wosid', 2: 'url', 1: 'doi'}

    def __init__(self, corpus, source):
        """

        Parameters
        ----------
        corpus - The Corpus object that is to be serialized.
        source - This denotes the Source of the corpus object.
        The possible values can be

        1 for JSTOR,
        2 for ZOTERO,
        3 for WOS and
        4 for Scopus

        The source value helps us in deciding, what attribute to fetch the paper_id from?
        i.e.
        DOI in case of JSTOR,
        URL in case of ZOTERO
        and WOSID in case of WOS.

        Following are the parameters which are initialized.

        >>>  self.corpus_id = tethnedao.getMaxCorpusID()+1 #this sets the new primary key which is (max PK +1)

        Following are the hashMaps which are initialized and will be used for foreign key references.


        >>>  self.paperIdMap ={}
        >>>  self.paperIdMap[paper.wosid] = pid # This helps in keeping track of the Primary keys

        Similarly, we have the following for Authors and AuthorsInstances.

        >>>  self.authorIdMap = {}

        >>>  self.authorInstanceIdMap = {}

        Returns
        -------

        """
        self.corpus = corpus
        self.source = source
        self.corpus_id = tethnedao.getMaxCorpusID()+1
        self.paperIdMap = {}
        self.authorIdMap = {}
        self.authorInstanceIdMap = {}
        self.citationIdMap = {}
        self.citationInstanceMap = {}
        self.instituteIdMap = {}
        self.instituteIdInstanceMap = {}

    def serializeCorpus(self):
        """
        This method creates a fixture for the "django-tethne_corpus" model.
        Returns
        -------
        corpus_details in JSON format which can written to a file.

        """
        corpus_details = [{
                "model": "django-tethne.corpus",
                "pk": self.corpus_id,
                "fields": {
                    "source": self.source,
                    "date_created":strftime("%Y-%m-%d %H:%M:%S", gmtime()),
                    "length" : len(self.corpus),
                }
            }]
        return corpus_details

    def serializePaper(self):
        """
        This method creates a fixture for the "django-tethne_paper" model.

        Returns
        -------
        paper_details in JSON format, which can written to a file.

        """
        pid = tethnedao.getMaxPaperID();
        papers_details = []

        for paper in self.corpus:
            pid = pid + 1
            paper_key = getattr(paper, Serialize.paper_source_map[self.source])
            self.paperIdMap[paper_key] = pid
            paper_data = {
                "model": "django-tethne.paper",
                "pk": self.paperIdMap[paper_key],
                "fields": {
                    "paper_id": paper_key,
                    "corpus":self.corpus_id,
                    "pub_date": getattr(paper, 'date', ''),
                    "volume": getattr(paper, 'volume', ''),
                    "title": getattr(paper, 'title', ''),
                    "abstract": getattr(paper, 'abstract', ''),
                }
            }
            papers_details.append(paper_data)
        return papers_details

    def serializeAuthors(self):
        """
         This method creates a fixture for the "django-tethne_author" model.

        Returns
        -------

        Author details in JSON format, which can be written to a file.

        """
        author_details = []
        auid = tethnedao.getMaxAuthorID()
        for val in self.corpus.features['authors'].index.values():
            auid = auid + 1
            self.authorIdMap[val[1]+val[0]] = auid
            instanceData = {
                    "model": "django-tethne.author",
                    "pk": auid,
                    "fields":{
                        "first_name": val[1],
                        "last_name": val[0],
                    }
                }
            author_details.append(instanceData)
        return author_details

    def serializeAuthorInstances(self):
        """
         This method creates a fixture for the "django-tethne_author" model.

        Returns
        -------
        Author Instance details which can be written to a file

        """
        author_instance_details = []
        au_instanceid = tethnedao.getMaxAuthorInstanceID()

        for paper in self.corpus:
            paper_key = getattr(paper, Serialize.paper_source_map[self.source])
            for author in paper.authors:
                au_instanceid = au_instanceid + 1
                author_key = author[0][1] + author[0][0]
                author_instance_key = paper_key + author_key
                self.authorInstanceIdMap[author_instance_key] = au_instanceid
                instance_data = {
                        "model": "django-tethne.author_instance",
                        "pk": au_instanceid,
                        "fields": {
                            "paper": self.paperIdMap[paper_key],
                            "author": self.authorIdMap[author_key],
                            "first_name": author[0][1],
                            "last_name":author[0][0],
                        }
                    }
                author_instance_details.append(instance_data)

                # Commented the following, as we do not have author identity detail now.
                """
                    identity_data = {
                        "model": "django-tethne.author_identity",
                        "fields" :{
                            "author": self.authorIdMap[author[0][1]+author[0][0]],
                            "author_instance": self.authorInstanceIdMap[paper.wosid+author[0][1]+author[0][0]],
                            "confidence": 0.0,
                        }
                    }
                    author_identity.append(identity_data)
                """
        return author_instance_details

    def serializeCitation(self):
        """
        This method creates a fixture for the "django-tethne_citation" model.

        Returns
        -------
        citation details which can be written to a file

        """
        citation_details = []
        citation_id = tethnedao.getMaxCitationID()
        for citation in self.corpus.features['citations'].index.values():

            date_match = re.search(r'(\d+)', citation)
            if date_match is not None:
                date = date_match.group(1)
            if date_match is None:
                date_match = re.search(r"NONE", citation)
                date = date_match.group()
            first_author = citation.replace('_', ' ').split(date)[0].rstrip()
            journal = citation.replace('_', ' ').split(date)[1].lstrip()
            citation_key = citation
            if citation_key not in self.citationIdMap:
                citation_id += 1
                self.citationIdMap[citation_key] = citation_id
                citation_data = {
                        "model": "django-tethne.citation",
                        "pk": citation_id,
                        "fields": {
                            "literal": citation,
                            "journal": journal,
                            "first_author": first_author,
                            "date": date
                        }
                    }
                citation_details.append(citation_data)
        return citation_details

    def serializeCitationInstance(self):
        """

        This method creates a fixture for the "django-tethne_citation_instance" model.

        Returns
        -------
        citation Instance details which can be written to a file

        """
        citation_instance_data = []
        citation_instance_id = tethnedao.getMaxCitationInstanceID()
        for paper in self.corpus:
            paper_key = getattr(paper, Serialize.paper_source_map[self.source])
            for citation_list in paper.citations:
                citation = citation_list[0]
                citation_key = citation
                citation_instance_id += 1
                date_match = re.search(r'(\d+)', citation)
                if date_match is not None:
                    date = date_match.group(1)
                if date_match is None:
                    date_match = re.search(r"NONE", citation)
                    date = date_match.group()
                first_author = citation.replace('_', ' ').split(date)[0].rstrip()
                journal = citation.replace('_', ' ').split(date)[1].lstrip()
                citation_instance_details = {
                    "model": "django-tethne.citation_instance",
                    "pk": citation_instance_id,
                    "fields": {
                        "literal": citation,
                        "citation": self.citationIdMap[citation_key],
                        "paper": self.paperIdMap[paper_key],
                        "journal": journal,
                        "first_author": first_author,
                        "date": date
                    }
                }
                citation_instance_data.append(citation_instance_details)
        return citation_instance_data

    def serializeInstitution(self):
        """
        This method creates a fixture for the "django-tethne_citation_institution" model.

        Returns
        -------
        institution details which can be written to a file

        """
        institution_data = []
        institution_instance_data = []
        affiliation_data = []
        affiliation_id = tethnedao.getMaxAffiliationID()
        institution_id = tethnedao.getMaxInstitutionID()
        institution_instance_id = tethnedao.getMaxInstitutionInstanceID()

        for paper in self.corpus:
            if hasattr(paper, 'authorAddress'):
                paper_key = getattr(paper, Serialize.paper_source_map[self.source])
                if type(paper.authorAddress) is unicode:
                    institution_id += 1
                    institution_instance_id += 1
                    institute_literal, authors = SerializeUtility.get_auth_inst(paper.authorAddress)
                    institute_row, institute_instance_row = self.get_details_from_inst_literal(institute_literal,
                                                                                               institution_id,
                                                                                               institution_instance_id,
                                                                                               paper_key)
                    if institute_row:
                        institution_data.append(institute_row)
                    institution_instance_data.append(institute_instance_row)
                    if authors:
                        for author in authors:
                            affiliation_id += 1
                            affiliation_row = self.get_affiliation_details(author, affiliation_id, institute_literal)
                            affiliation_data.append(affiliation_row)

                elif type(paper.authorAddress) is list:
                    for address in paper.authorAddress:
                        institution_id += 1
                        institution_instance_id += 1
                        institute_literal, authors = SerializeUtility.get_auth_inst(address)
                        institute_row, institute_instance_row = self.get_details_from_inst_literal(institute_literal,
                                                                                                   institution_id,
                                                                                                   institution_instance_id,
                                                                                                   paper_key)
                        if institute_row:
                            institution_data.append(institute_row)
                        institution_instance_data.append(institute_instance_row)
                        if authors is None:
                            authors = prevAuthors
                        for author in authors:
                            affiliation_id += 1
                            affiliation_row = self.get_affiliation_details(author, affiliation_id, institute_literal)
                            affiliation_data.append(affiliation_row)
                        prevAuthors = authors
        return institution_data, institution_instance_data, affiliation_data

    def get_details_from_inst_literal(self, institute_literal, institution_id, institution_instance_id, paper_key):
        """
        This method parses the institute literal to get the following
        1. Department naame
        2. Country
        3. University name
        4. ZIP, STATE AND CITY (Only if the country is USA. For other countries the standard may vary. So parsing these
        values becomes very difficult. However, the complete address can be found in the column "AddressLine1"

        Parameters
        ----------
        institute_literal -> The literal value of the institute
        institution_id  -> the Primary key value which is to be added in the fixture
        institution_instance_id -> Primary key value which is to be added in the fixture
        paper_key -> The Paper key which is used for the Institution Instance

        Returns
        -------

        """
        institute_details = institute_literal.split(',')
        institute_name = institute_details[0]
        country = institute_details[len(institute_details)-1].lstrip().replace('.', '')
        institute_row = None
        zipcode = ""
        state = ""
        city = ""
        if 'USA' in country:
            temp = country
            if(len(temp.split())) == 3:
                country = temp.split()[2]
                zipcode = temp.split()[1]
                state = temp.split()[0]
            elif(len(temp.split())) == 2:
                country = temp.split()[1]
                state = temp.split()[0]
            city = institute_details[len(institute_details)-2].lstrip()

        addressline1 = ""
        for i in range(1, len(institute_details)-1, 1):
            if i != len(institute_details)-2:
                addressline1 = addressline1 + institute_details[i]+','
            else:
                addressline1 = addressline1 + institute_details[i]
        if institute_literal not in self.instituteIdMap:
                self.instituteIdMap[institute_literal] = institution_id
                institute_row = {
                    "model": "django-tethne.institution",
                    "pk": institution_id,
                    "fields": {
                        "institute_name": institute_name,
                        "addressLine1": addressline1,
                        "country": country,
                        "zip": zipcode,
                        "state": state,
                        "city": city
                    }
                }
        department = ""
        if re.search('Dept([^,]*),', institute_literal) is not None:
            department = re.search('Dept([^,]*),', institute_literal).group().replace(',', '')
        institute_instance_row = {
            "model": "django-tethne.institution_instance",
            "pk": institution_instance_id,
            "fields": {
                "institution": self.instituteIdMap[institute_literal],
                "literal": institute_literal,
                "institute_name": institute_name,
                "addressLine1": addressline1,
                "country": country,
                "paper": self.paperIdMap[paper_key],
                "department": department,
                "zip": zipcode,
                "state": state,
                "city": city

            }
        }
        return institute_row, institute_instance_row

    def get_affiliation_details(self, value, affiliation_id, institute_literal):
        """
        This method is used to map the Affiliation between an author and Institution.

        Parameters
        ----------
        value - The author name
        affiliation_id - Primary key of the affiliation table
        institute_literal

        Returns
        -------
        Affiliation details(JSON fixture) which can be written to a file

        """
        tokens = tuple([t.upper().strip() for t in value.split(',')])
        if len(tokens) == 1:
            tokens = value.split()
        if len(tokens) > 0:
            if len(tokens) > 1:
                aulast, auinit = tokens[0:2]
            else:
                aulast = tokens[0]
                auinit = ''
        else:
            aulast, auinit = tokens[0], ''
        aulast = _strip_punctuation(aulast).upper()
        auinit = _strip_punctuation(auinit).upper()

        author_key = auinit+aulast
        affiliation_row = {
            "model": "django-tethne.affiliation",
            "pk": affiliation_id,
            "fields": {
                "author": self.authorIdMap[author_key],
                "institution": self.instituteIdMap[institute_literal]
            }
        }
        return affiliation_row


def serialize(dirPath, corpus, source):
    """

    Parameters
    ----------
    dirPath - A valid directory path where you want the JSON files to be written

    corpus - The corpus object which is to be serialized.

    source - The source of the corpus
    The possible values can be

        1 for JSTOR,
        2 for ZOTERO and
        3 for WOS
        4 for Scopus

    Follwoing is an example to use the serialize method.

    This method will raise an exception if

    1. dirPath is not a valid directory
    2. If Corpus object is none or has no papers to serialize
    3. The source is not a valid source.

    .. code-block:: python

    >>> from tethne.readers import wos
    >>> from tethne.serialize import paper
    >>> wosCorpus = wos.read('/path/to/my/Corpus.txt')
    >>> paper.serialize('/path/to/my/FixturesDir/', wosCorpus, 3)

    Returns
    -------

    Writes the fixtures at the directory location.

    """
    if not os.path.isdir(dirPath):
        raise IOError('No such file or directory')

    if corpus is None or len(corpus) < 1:
        raise NameError('The corpus object has no papers to serialize')

    if source not in (1, 2, 3, 4):
        raise ValueError("Not a valid source.")

    corpusfilePath = os.path.join(dirPath, "corpus.json")
    paperFilePath = os.path.join(dirPath, "paper.json")
    authorFilePath = os.path.join(dirPath, "authors.json")
    authorInstanceFilePath = os.path.join(dirPath, "authorInstance.json")
    citationsFilePath = os.path.join(dirPath, "citations.json")
    citationInstanceFilePath = os.path.join(dirPath, "citationInstance.json")
    institutionsFilePath = os.path.join(dirPath, "institutions.json")
    institutionInstanceFilePath = os.path.join(dirPath, "institutionInstance.json")
    affiliationsFilePath = os.path.join(dirPath, "affiliations.json")

    serializehandler = Serialize(corpus, source)

    corpusDetails = serializehandler.serializeCorpus()
    papersDetails = serializehandler.serializePaper()
    authorDetails = serializehandler.serializeAuthors()
    authorInstanceDetails = serializehandler.serializeAuthorInstances()
    citationDetails = serializehandler.serializeCitation()
    citationInstanceDetails = serializehandler.serializeCitationInstance()
    institutions, institutionsInstance, affilations = serializehandler.serializeInstitution()

    with open(corpusfilePath, mode='w+') as f:
        json.dump(corpusDetails, f)

    with open(paperFilePath, mode='w+') as f:
        json.dump(papersDetails, f)

    with open(authorFilePath, mode='w+') as f:
        json.dump(authorDetails, f)

    with open(authorInstanceFilePath, mode='w+') as f:
        json.dump(authorInstanceDetails, f)

    with open(citationsFilePath, mode='w+') as f:
        json.dump(citationDetails, f)

    with open(citationInstanceFilePath, mode='w+') as f:
        json.dump(citationInstanceDetails, f)

    with open(institutionsFilePath, mode='w+') as f:
        json.dump(institutions, f)

    with open(institutionInstanceFilePath, mode='w+') as f:
        json.dump(institutionsInstance, f)

    with open(affiliationsFilePath, mode='w+') as f:
        json.dump(affilations, f)







