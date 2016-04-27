"""
This class will serialize the Tethne Paper to persist in the database;

.. code-block:: python
>>> from tethne.serialize import paper

"""


import re
import os
import sys
from tethne.readers import Corpus, Paper
from tethne.dao import tethnedao
import json
import datetime
from time import gmtime, strftime
from uuid import uuid4

import sys
PYTHON_3 = sys.version_info[0] == 3
if PYTHON_3:
    unicode = str

class Serialize:

    paper_source_map = {3: 'wosid', 2: 'url'}

    def __init__(self, corpus, source):
        self.corpus = corpus
        self.source = source
        print tethnedao.getMaxCorpusID()
        self.corpus_id = tethnedao.getMaxCorpusID()+1
        self.paperIdMap = {}
        self.authorIdMap = {}
        self.authorInstanceIdMap = {}

    def serializeCorpus(self):
        if self.corpus is not None:
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
        pid = tethnedao.getMaxPaperID();
        for paper in self.corpus:
            pid = pid+1
            if not hasattr(paper, 'abstract'):
               paper.abstract = ""
            if not hasattr(paper, 'volume'):
                paper.volume = ""
            if not hasattr(paper, 'title'):
                paper.title = ""
            if not hasattr(paper, 'date'):
                paper.date = ""
            if self.source == 3:
                self.paperIdMap[paper.wosid] = pid
            elif self.source == 2:
                self.paperIdMap[paper.url] = pid

        if self.corpus is not None:
                papersDetails = [{
                    "model": "django-tethne.paper",
                    "pk": self.paperIdMap[paper.wosid],
                    "fields": {
                    "paper_id": paper.wosid,
                    "corpus": self.corpus_id,
                    "pub_date": paper.date,
                    "volume":paper.volume,
                    "title" : paper.title,
                    "abstract":paper.abstract,
                }
            } for paper in self.corpus]
        return papersDetails

    def serializeAuthors(self):
        author_details = []

        if self.corpus is not None:
            auid = tethnedao.getMaxAuthorID()
            for val in self.corpus.features['authors'].index.values():
                auid = auid+1
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
        author_instance_details = []
        author_identity = []
        auInstanceId = tethnedao.getMaxAuthorInstanceID()

        if self.corpus is not None:
            for paper in self.corpus:
                for author in paper.authors:
                    auInstanceId = auInstanceId+1
                    self.authorInstanceIdMap[paper.wosid+author[0][1]+author[0][0]]=auInstanceId
                    instance_data = {
                    "model": "django-tethne.author_instance",
                    "pk": auInstanceId,
                    "fields":{
                        "paper": self.paperIdMap[paper.wosid],
                        "author": self.authorIdMap[author[0][1]+author[0][0]],
                        "first_name": author[0][1],
                        "last_name":author[0][0],
                            }
                    }
                    author_instance_details.append(instance_data)
                    identity_data = {
                    "model": "django-tethne.author_identity",
                    "fields" :{
                        "author": self.authorIdMap[author[0][1]+author[0][0]],
                        "author_instance": self.authorInstanceIdMap[paper.wosid+author[0][1]+author[0][0]],
                        "confidence": 0.0,
                        }
                    }
                    author_identity.append(identity_data)
        return author_instance_details, author_identity






def serialize(dirPath, corpus, source, corpus_number):
    if not os.path.isdir(dirPath):
        raise ValueError('No such file or directory')

    if os.path.isdir(dirPath):
        corpusfilePath = os.path.join(dirPath, "corpus.json")
        paperFilePath = os.path.join(dirPath, "paper.json")
        authorFilePath = os.path.join(dirPath, "authors.json")
        authorInstanceFilePath = os.path.join(dirPath, "authorInstance.json")
        authorIdentityFilePath = os.path.join(dirPath, "authorIdentity.json")

    serializehandler = Serialize(corpus, source)

    corpusDetails = serializehandler.serializeCorpus()
    papersDetails = serializehandler.serializePaper()
    authorDetails = serializehandler.serializeAuthors()
    authorInstanceDetails, authorIdentityDetails = serializehandler.serializeAuthorInstances()

    with open(corpusfilePath, 'w') as f:
        json.dump(corpusDetails, f)

    with open(paperFilePath, 'w') as f:
        json.dump(papersDetails, f)

    with open(authorFilePath, 'w') as f:
        json.dump(authorDetails, f)

    with open(authorInstanceFilePath, 'w') as f:
        json.dump(authorInstanceDetails, f)

    with open(authorIdentityFilePath, 'w') as f:
        json.dump(authorIdentityDetails, f)







