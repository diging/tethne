from ..services import dspace
from ..classes import Paper, Corpus

import tempfile
import cPickle as pickle
from unidecode import unidecode

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('INFO')

def read_corpus(metapath, bitstreampath=None):
    """
    Generate a :class:`.Corpus` from a ``collection`` in the DSpace repository
    at ``endpoint``.
    
    :class:`.Paper`\s are indexed by URI.
    """
    
    with open(metapath, 'r') as f:
        items = pickle.load(f)
        
    papers = read(metapath, items=items)
    corpus = Corpus(papers, index_by='uri')

    if bitstreampath is not None:
        corpus = add_bitstreams(corpus, bitstreampath)

    return corpus
    
def download_collection(    publickey, privatekey, endpoint, collection, 
                            outpath=None, getBitstreams=False   ):
    """
    Retrieves metadata (and bitstreams) for a ``collection`` in a DSpace
    repository at ``endpoint``.
    
    Parameters
    ----------
    publickey : str
    privatekey : str
    endpoint : str
        REST endpoint.
    collection : int
        Collection ID.
    outpath : str
        (optional). Directory in which to store metadata (and bitstreams).
    getBitstreams : bool
        (default: False) If True, downloads the primary bitstream for each item,
        and stores a dict mapping item URIs onto local paths to those
        bitstreams.
    
    Returns
    -------
    items : list
        A list of items (dict) in the collection.
    bitstreams : dict
        Maps item URIs onto local paths to bitstream files.
    outpath : str
        Path to directory containing metadata (and bitstreams).
    """
    logging.debug('Retrieving metadata from collection {0}'.format(collection))
    
    if outpath is None:
        # Generate a temporary directory to hold metadata
        outpath = tempfile.mkdtemp()    
        logging.debug('Generated temppath at {0}'.format(outpath))
    
    service = dspace.DSpace(publickey, privatekey, endpoint)
    items = service.list_items(collection)
    logging.debug('Retrieved metadata for {0} items'.format(len(items)))    
    
    with open(outpath+'/metadata.pickle', 'w') as f:
        pickle.dump(items, f)
        
    if getBitstreams:
        logging.debug('Retrieving bitstreams from collection {0}'
                                                            .format(collection))
        bitstreams = _get_bitstreams(items, service, outpath)
        # bitstreams is a dict keyed by URI.
    
        with open(outpath+'/bitstreams.pickle', 'w') as f:
            pickle.dump(bitstreams, f)
    else:
        bitstreams = None

    return items, bitstreams, outpath
    
def add_bitstreams(corpus, bitstreampath):
    """
    Load bitstream contents and add them to their respective :class:`.Paper`\s
    in ``corpus``.
    
    Parameters
    ----------
    corpus : :class:`.Corpus`
    bitstreampath : str
        Path to a pickled dict mapping :class:`.Paper` URIs onto paths to files
        containing text data.
        
    Returns
    -------
    corpus : :class:`.Corpus`
    """
    import codecs
    
    with open(bitstreampath, 'r') as f:
        bitstreams = pickle.load(f)
        
    for uri, bpath in bitstreams.iteritems():
        with codecs.open(bpath, 'r', encoding='utf-8') as f:
            contents = unidecode(f.read())

        corpus.papers[uri]['contents'] = contents    
    return corpus

def read(metapath=None, items=None):
    """
    Get metadata from ``collection``, and generate a list of :class:`.Paper`\s.
    """
    
    # Want to be able to provide items to cut down on API calls.
    if items is None:
        with open(metapath, 'r') as f:
            items = pickle.load(f)    
    
    papers = []
    for i in items:
        p = Paper()
        p['uri'] = i['uri']
        p['date'] = int(i['dateCreated'][0:4])
        p['atitle'] = i['title']
        p['abstract'] = i['abstract']
        p['aulast'], p['auinit'] = _handle_creators_string(i['creators_string'])
        p['auuri'] = i['creators']
        papers.append(p)

    logging.debug('Generated {0} papers from metadata'.format(len(papers)))
    return papers

def _get_bitstreams(items, service, outpath):
    bitstreams = {}
    
    # Download bitstreams.
    for i in items:
        if int(i['primary_bitstream']) != -1:
            logger.debug('Getting bitstream for {0}'.format(i['uri']) )
            
            safe_uri = i['uri'].replace('/','-').replace(':','_')
            fpath = '{0}/{1}.txt'.format(outpath, safe_uri)
            bitstream = service.get_bitstream(i['primary_bitstream'], fpath)
            bitstreams[i['uri']] = fpath
                
    return bitstreams

def _handle_creators_string(creators_string):
    """
    Extract author's lastname and initials.
    """
    aulast = []
    auinit = []
    for creator in creators_string:
        try:    # Should be formatted like LAST, FIRST[ MIDDLE][, extra stuff]
            surname, forename = creator.split(', ')[0:2]
        except ValueError: # No comma! Treat as FIRST MIDDLE LAST
            csplit = creator.split()
            surname = csplit[-1]
            forename = ' '.join(csplit[0:-1])
            
        aulast.append(surname.strip().upper())
        
        inits = ''.join([ n[0] for n in forename.split() ])
        auinit.append(inits.strip().upper())
    
    return aulast, auinit
        
    
    
#        print i['creators']

    

#def read_corpus(publickey, privatekey, collectionid):
#    service = dspace.DSpace(publickey, privatekey)
    

