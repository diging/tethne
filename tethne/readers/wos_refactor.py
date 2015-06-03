import string
import re 

from tethne.base.ftparser import FTParser
from tethne.classes.paper import Paper
from tethne.utilities import _strip_punctuation, _space_sep	

class WoSParser(FTParser):
    start_tag = 'PT'
    end_tag = 'ER'
    concat_fields = ['abstract', 'keywords', 'funding']
    entry_class = Paper

    tags = {
        'PY': 'date',
        'SO': 'journal',
        'AB': 'abstract',
        'TI': 'title',
        'AF': 'authors_full',
        'AU': 'authors_init',
        'ID': 'authorKeywords',
        'DE': 'keywordsPlus',
        'DI': 'doi',
        'BP': 'pageStart',
        'EP': 'pageEnd',
        'VL': 'volume',
        'IS': 'issue',
        'CR': 'citedReferences',
        'DT': 'documentType',
        'CA': 'groupAuthors',
        'ED': 'editors',
        'SE': 'bookSeriesTitle',
        'BS': 'bookSeriesSubtitle',
        'LA': 'language',
        'DT': 'documentType',
        'CT': 'conferenceTitle',
        'CY': 'conferenceDate',
        'HO': 'conferenceHost',
        'CL': 'conferenceLocation',
        'SP': 'conferenceSponsors',
        'C1': 'authorAddress',
        'RP': 'reprintAddress',
        'EM': 'emailAddress',
        'FU': 'funding',
        'NR': 'citationCount',
        'TC': 'timesCited',
        'PU': 'publisher',
        'PI': 'publisherCity',
        'PA': 'publisherAddress',
        'SC': 'subject',
        'SN': 'ISSN',
        'BN': 'ISSN',
        'UT': 'wosid',
        'JI': 'isoSource',
    }

	
    def parse_author(self, value):
        tokens = tuple([t.upper().strip() for t in value.split(',')])
        if len(tokens) > 0:
            aulast, auinit = tokens
        else:
            aulast, auinit = tokens[0], ''
        return _strip_punctuation(aulast), _strip_punctuation(auinit)


    def handle_AF(self, value):
        return self.parse_author(value)

        
    def handle_AU(self, value):
        aulast, auinit = self.parse_author(value)
        auinit = _space_sep(auinit)
        return aulast, auinit


    def handle_TI(self, value): return value.title()


    def handle_VL(self, value): return str(value)
        

    def handle_IS(self, value): return str(value)


    def handle_CR(self, value):
        citation = self.entry_class()

        # First-author name and publication date.
        ny_match = re.match('([A-Za-z\,\.\-\s\'\/\[\]]+)([0-9]{4})?\,\s+([0-9A-Z\s]+)', value)
        if ny_match is not None:
            name_raw, date, journal = ny_match.groups()
        name_tokens = [t.replace('.', '') for t in name_raw.split(' ')]
        if len(name_tokens) > 0:
            aulast = name_tokens[0].upper()
            auinit = ' '.join([_space_sep(_strip_punctuation(n)) for n in name_tokens[1:]]).upper()
        else:
            aulast = name_tokens[0].upper()
            auinit = ''	
        setattr(citation, 'authors_init', [(aulast, auinit)])
        if date:
            date = int(date)
        setattr(citation, 'date', date)
        setattr(citation, 'journal', journal)

        # Volume.
        v_match = re.search('\,\s+V([0-9A-Za-z]+)', value)
        if v_match is not None:  volume = v_match.group(1)		
        else:					 volume = None
        setattr(citation, 'volume', volume)

        # Start page.
        p_match = re.search('\,\s+[Pp]([0-9A-Za-z]+)', value)
        if p_match is not None:  page = p_match.group(1)		
        else:					 page = None	
        setattr(citation, 'pageStart', page)			

        # DOI.
        doi_match = re.search('DOI\s(.*)', value)
        if doi_match is not None:	doi = doi_match.group(1)
        else:						doi = None
        setattr(citation, 'doi', doi)
        return citation

        
    def postprocess_authorKeywords(self, entry):
        """
        Author Keywords are usually semicolon-delimited.
        """

        if type(entry.authorKeywords) is str:
            entry.authorKeywords = [k.strip().upper() for k 
                                    in entry.authorKeywords.split(';')]


    def postprocess_keywordsPlus(self, entry):
        """
        Keyword Plus keywords are usually semicolon-delimited.
        """	

        if type(entry.keywordsPlus) is str:
            entry.keywordsPlus = [k.strip().upper() for k
                                  in entry.keywordsPlus.split(';')]			


    def postprocess_funding(self, entry):
        """
        Separate funding agency from grant numbers.
        """
        
        sources = [fu.strip() for fu in entry.funding.split(';')]
        sources_processed = []
        for source in sources:
            m = re.search('(.*)?\s+\[(.+)\]', source)
            if m:
                agency, grant = m.groups()
            else:
                agency, grant = source, None
            sources_processed.append((agency, grant))
        entry.funding = sources_processed
