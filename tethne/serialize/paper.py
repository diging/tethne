"""
This class has functionalities to serialize a TETHNE corpus object  to persist in the database;

.. code-block:: python
>>> from tethne.serialize import paper

"""

import os
import json

from tethne.dao import tethnedao
from time import gmtime, strftime


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
                author_instance_key = paper.wosid + author_key
                self.authorInstanceIdMap[author_instance_key] = au_instanceid
                instance_data = {
                        "model": "django-tethne.author_instance",
                        "pk": au_instanceid,
                        "fields":{
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

    serializehandler = Serialize(corpus, source)

    corpusDetails = serializehandler.serializeCorpus()
    papersDetails = serializehandler.serializePaper()
    authorDetails = serializehandler.serializeAuthors()
    authorInstanceDetails = serializehandler.serializeAuthorInstances()

    with open(corpusfilePath, 'w') as f:
        json.dump(corpusDetails, f)

    with open(paperFilePath, 'w') as f:
        json.dump(papersDetails, f)

    with open(authorFilePath, 'w') as f:
        json.dump(authorDetails, f)

    with open(authorInstanceFilePath, 'w') as f:
        json.dump(authorInstanceDetails, f)







