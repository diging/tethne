from ..services import dspace
from ..classes import Paper, Corpus

import logging
logging.basicConfig(filename=None, format='%(asctime)-6s: %(name)s - %(levelname)s - %(module)s - %(funcName)s - %(lineno)d - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

def read(publickey, privatekey, endpoint, collection):
    """
    Get metadata from ``collection``, and generate a :class:`.Corpus`\.
    """
    
    service = dspace.DSpace(publickey, privatekey, endpoint)
    
    logging.debug('Retrieving metadata from collection {0}'.format(collection))
    items = service.list_items(collection)
    logging.debug('Retrieved metadata for {0} items'.format(len(items)))
    
    papers = []
    for i in items:
        p = Paper()
        p['uri'] = i['uri']
        p['date'] = i['dateCreated']
        papers.append(p)
        
        print i['creators']

    

#def read_corpus(publickey, privatekey, collectionid):
#    service = dspace.DSpace(publickey, privatekey)
    

