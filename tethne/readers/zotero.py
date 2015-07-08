import os
import iso8601
import logging
import rdflib
logging.basicConfig(level=40)

from unidecode import unidecode
from datetime import datetime

from tethne import Paper, Corpus
from tethne.readers.base import RDFParser


class ZoteroParser(RDFParser):
    entry_class = Paper
    entry_elements = ['bib:Illustration', 'bib:Recording', 'bib:Legislation', 
                      'bib:Document', 'bib:BookSection', 'bib:Book', 'bib:Data', 
                      'bib:Letter', 'bib:Report', 'bib:Article', 'bib:Manuscript',
                      'bib:Image', 'bib:ConferenceProceedings', 'bib:Thesis']    
    tags = {
        'isPartOf': 'journal'
    }
                      
    meta_elements = [
        ('date', rdflib.URIRef("http://purl.org/dc/elements/1.1/date")),
        ('identifier', rdflib.URIRef("http://purl.org/dc/elements/1.1/identifier")),        
        ('abstract', rdflib.URIRef("http://purl.org/dc/terms/abstract")),
        ('authors_full', rdflib.URIRef("http://purl.org/net/biblio#authors")),
        ('link', rdflib.URIRef("http://purl.org/rss/1.0/modules/link/link")),
        ('title', rdflib.URIRef("http://purl.org/dc/elements/1.1/title")),
        ('isPartOf', rdflib.URIRef("http://purl.org/dc/terms/isPartOf")),
        ('pages', rdflib.URIRef("http://purl.org/net/biblio#pages")),
        ('documentType', 
         rdflib.URIRef("http://www.zotero.org/namespaces/export#itemType"))]     
    
    def __init__(self, path, **kwargs):
        name = os.path.split(path)[1]
        path = os.path.join(path, '{0}.rdf'.format(name))
        super(ZoteroParser, self).__init__(path, **kwargs)
    
    def open(self):
    
        # Fix validation issues. Zotero incorrectly uses rdf:resource as a
        # child element for Attribute; rdf:resource should instead be used
        # as an attribute of link:link.    
        with open(self.path, 'r') as f:
            corrected = f.read().replace('rdf:resource rdf:resource',
                                         'link:link rdf:resource')
        with open(self.path, 'w') as f:
            f.write(corrected)

        super(ZoteroParser, self).open()
    
    def handle_title(self, value):
        return str(value)
        
    def handle_abstract(self, value):
        return unidecode(value)
    
    def handle_identifier(self, value):
        uri_elem = rdflib.URIRef("http://purl.org/dc/terms/URI")
        type_elem = rdflib.term.URIRef(u'http://www.w3.org/1999/02/22-rdf-syntax-ns#type')
        value_elem = rdflib.URIRef('http://www.w3.org/1999/02/22-rdf-syntax-ns#value')
        identifier = str(self.graph.value(subject=value, predicate=value_elem))
        ident_type = self.graph.value(subject=value, predicate=type_elem)
        if ident_type == uri_elem:
            self.set_value('uri', identifier)

    
    def handle_link(self, value):
        link_elem = rdflib.URIRef("http://purl.org/rss/1.0/modules/link/link")
        for s, p, o in self.graph.triples((value, None, None)):
            if p == link_elem:
                return str(o).replace('file://', '')                 

    def handle_date(self, value):
        try:
            return iso8601.parse_date(str(value)).year    
        except iso8601.ParseError:
            return datetime.strptime(str(value), "%m/%d/%Y").date().year
        
    def handle_documentType(self, value):
        return str(value)
        
    def handle_authors_full(self, value):
        authors = [self.handle_author(o) for s, p, o
                   in self.graph.triples((value, None, None))]        
        return [a for a in authors if a is not None]
        
    def handle_author(self, value):
        forename_elem = rdflib.URIRef('http://xmlns.com/foaf/0.1/givenname')
        forename_iter = self.graph.triples((value, forename_elem, None))        
        surname_elem = rdflib.URIRef('http://xmlns.com/foaf/0.1/surname')
        surname_iter = self.graph.triples((value, surname_elem, None))
        
        try:
            forename = str([e[2] for e in forename_iter][0]).upper().replace('.', '')
        except IndexError:
            forename = ''

        try:
            surname = str([e[2] for e in surname_iter][0]).upper().replace('.', '')
        except IndexError:
            surname = ''

        if surname == '' and forename == '':
            return
        return surname, forename            
    
    def handle_isPartOf(self, value):
        vol = rdflib.term.URIRef(u'http://prismstandard.org/namespaces/1.2/basic/volume')
        ident = rdflib.URIRef("http://purl.org/dc/elements/1.1/identifier")
        journal = None
        for s, p, o in self.graph.triples((value, None, None)):
           
            if p == vol:        # Volume number
                self.set_value('volume', str(o))                    
            elif p == rdflib.term.URIRef(u'http://purl.org/dc/elements/1.1/title'):
                journal = str(o)    # Journal title.
        return journal
        
    def handle_pages(self, value):
        return tuple(unidecode(value).split('-'))
        
    def postprocess_pages(self, entry):
        start, end = entry.pages
        setattr(entry, 'pageStart', start)
        setattr(entry, 'pageEnd', end)
        del entry.pages

def read(path, corpus=True, index_by='identifier', **kwargs):
    # TODO: is there a case where `from_dir` would make sense?
    papers = ZoteroParser(path).parse()

    if corpus:
        return Corpus(papers, index_by=index_by, **kwargs)
    return papers
        
