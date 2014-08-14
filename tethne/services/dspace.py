import hashlib
import urllib2
import xml.etree.ElementTree as ET
from pprint import pprint
import string
import unicodedata

class DSpace:
    """
    :class:`.DSpace` provides methods for interacting with the
    `DSpaceTools API <https://github.com/mbl-cli/DspaceTools/wiki/API>`_, which
    is a custom REST API for the
    `ASU Digital HPS Repository <http://hpsrepository.asu.edu>`_.

    ..
    """
        
    def __init__(self, public_key, private_key, rest_path):
        """
        Class for interacting with the ASU Digital HPS Community Repository
        custom API. https://github.com/mbl-cli/DspaceTools/wiki/API

        Parameters
        ----------
        public_key : string
        private_key : string
        rest_path : string
            URL for RESTful API endpoint
        """
        self.public_key = public_key
        self.private_key = private_key
        self.rest_path = rest_path
    
    def list_collections(self):
        """
        Retrieves all of the collections to which the user has access.
        """
        
        root = self._get_element_from_resource('/collections.xml')
    
        C = []
        for node in root:
            coll = self._dict_from_node(node, True)
            C.append({
                        'id': coll['entityId'],
                        'name': coll['name']
                    })
        return C

    def list_items(self, collection):
        """
        Retrieves details about all items in a collection.

        Parameters
        ----------
        collection : string or int
            Collection id.

        Returns
        -------
        list : a list of nested dictionaries.
        """

        items = self.collection(collection)['items']['itementity']
    
        I = [{
                'id': item['id'],
                'title': item['name'],
                'uri': self._item_uri(item),
                'primary_bitstream': self._item_primary_bitstream(item),
                'creators' : self._item_creators(item),
                'creators_string': self._item_creators_string(item),
                'dateCreated': self._item_dateCreated(item),
                'dateDigitized': self._item_dateDigitized(item),
                'abstract': self._item_abstract(item)
             } for item in items ]
        return I
        
    def get_bitstream(self, bitstream, save_path=None):
        """
        Downloads a bitstream and handles it. If save_path is provided, returns
        a file pointer. Otherwise returns the content of the bitstream.

        Parameters
        ----------
        bitstream : string or int
            A bitstream id.
        save_path : string or None
            Full path where bitstream should be saved, including the filename.

        Returns
        -------
        Contents of bitstream, or file pointer.

        Notes
        -----
        WARNING: This has only been tested on bitstreams containing text data!

        TODO: More robust handling for different data types.
        """

        rpath = self._get_path('/bitstream/' + str(bitstream))
        r = urllib2.urlopen(rpath)
        data = r.read()
        if save_path is None:
            return data
        else:
            with open(save_path, 'w') as f:
                f.write(data)
                return f        

    def _item_primary_bitstream(self, item):
        try:
            return item['bundles']['bundleentity']['primaryBitstreamId']
        except TypeError:   # Something is wrong with this item, apparently.
            return None
    
    def _item_creators_string(self, item):
        return self._item_metadata(item, 'creator', list=True)
    
    def _item_creators(self, item):
        return self._item_metadata(item, 'creator', 'uri', list=True)
    
    def _item_uri(self, item):
        return self._item_metadata(item, 'identifier', 'uri')

    def _item_dateCreated(self, item):
        return self._item_metadata(item, 'date')
        
    def _item_dateDigitized(self, item):
        return self._item_metadata(item, 'date', 'digitized')
        
    def _item_abstract(self, item):
        return self._item_metadata(item, 'description', 'abstract')
        
    def _item_metadata(self, item, element, qualifier='None', schema='dc', list=False):
        values = []
        for ent in item['metadata']['metadataentity']:
            if ent['element'] == element and ent['qualifier'] == qualifier:
                if list:
                    values.append(ent['value'])
                else:
                    return ent['value']
                    
        if list and len(values) > 0:
            return values
        return None

    def _get_digest(self, path):
        """
        Produces an authentication digest based on resource path and your
        private key.

        Parameters
        ----------
        path : string
            Relative URL of desired resource. E.g. '/items.xml'

        Returns
        -------
        string : authentication digest for desired resource.
        """

        m = hashlib.sha1('/rest' + path + self.private_key)
        return m.hexdigest()[0:8]

    def _get_path(self, path, idOnly=False):
        """
        Produces a full path for the desired resource.

        Parameters
        ----------
        path : string
            Relative URL of desired resource. E.g. '/items.xml'
        idOnly : boolean
            If True, the returned path will yield only id/reference information
            for the desired resource. Default is False.

        Returns
        -------
        string : full URL of desired resource, including authentication
            information.
        """

        digest = self._get_digest(path)
        return self.rest_path + path + "?api_key=" + self.public_key + \
                "&api_digest=" + digest + "&idOnly=" + str(idOnly).lower()

    def _get_element_from_resource(self, path, idOnly=False):
        """
        Retrieves the desired resource from the DSpace API.

        Parameters
        ----------
        path : string
            Relative URL of desired resource. E.g. '/items.xml'
        idOnly : boolean
            If True, will yield only id/reference information for the desired
            resource. Default is False.

        Returns
        -------
        ElementTree node : containing API response.
        """

        request_path = self._get_path(path, idOnly)
        response = urllib2.urlopen(request_path).read()
        return ET.fromstring(response)

    def _clean_text(self, s):
        """
        Gets rid of garbage. Strips non-ascii characters, newlines, and leading/
        trailing whitespace.

        Parameters
        ----------
        s : string
            A messy string.

        Returns
        -------
        string : a somewhat cleaner string.
        """

        norm = unicodedata.normalize('NFKD', unicode(s))
        return  norm.encode('ascii', 'ignore').rstrip().replace('\n','')

    def _dict_from_node(self, node, recursive=False):
        """
        Converts ElementTree node to a dictionary.

        Parameters
        ----------
        node : ElementTree node
        recursive : boolean
            If recursive=False, the value of any field with children will be the
            number of children.

        Returns
        -------
        dict : nested dictionary.
            Tags as keys and values as values. Sub-elements that occur multiple
            times in an element are contained in a list.
        """

        dict = {}
        for snode in node:
            if len(snode) > 0:
                if recursive:
                    # Will drill down until len(snode) <= 0.
                    value = self._dict_from_node(snode, True)
                else:
                    value = len(snode)
            else:
                value = self._clean_text(snode.text)

            if snode.tag in dict.keys():    # If there are multiple subelements
                                            #  with the same tag, then the value
                                            #  of the element should be a list
                                            #  rather than a dict.
                if type(dict[snode.tag]) is list:   # If a list has already been
                                                    #  started, just append to
                                                    #  it.
                    dict[snode.tag].append(value)
                else:
                    dict[snode.tag] = [ dict[snode.tag], value ]
            else:
                dict[snode.tag] = value     # Default behavior.
        return dict

    def communities(self):
        """
        Retrieves all of the communities to which the user has access.

        Returns
        -------
        list : a list of nested dictionaries.
        """

        root = self._get_element_from_resource('/communities.xml')

        C = []
        for node in root:
            comm = self._dict_from_node(node, True)
            C.append({
                        'id': comm['entityId'],
                        'name': comm['name']
                    })
        return C



    def community(self, community):
        """
        Retrieves details about a specific community, by id.

        Parameters
        ----------
        community : string or int
            Community id.

        Returns
        -------
        dict : a nested dictionary.
        """

        path = '/communities/'+str(community)+'.xml'
        root = self._get_element_from_resource(path)
        return self._dict_from_node(root, True)

    def list_collection_ids(self, community):
        """
        Returns a list of collection IDs for a given community.

        Parameters
        ----------
        community : string or int
            Community id.

        Returns
        -------
        list : a list of collection ids.
        """
        collections = self.collections(community)
        return [ c['id'] for c in  collections]

    def collection(self, collection):
        """
        Retrieves details for a specific collection, by id.

        Parameters
        ----------
        collection : string or int
            Collection id.

        Returns
        -------
        dict : a nested dictionary.

        """

        path = '/collections/'+str(collection)+'.xml'
        root = self._get_element_from_resource(path)
        return self._dict_from_node(root, True)

    def list_item_ids(self, collection):
        """
        Returns a list of item IDs for a given collection.

        Parameters
        ----------
        collection : string or int
            Collection id.

        Returns
        -------
        list : a list of item ids.
        """

        return [ i['id'] for i in self.list_items(collection) ]

    def item(self, item):
        """
        Retrieve an item by id.

        Parameters
        ----------
        item : string or int
            An item id.

        Returns
        -------
        dict : a nested dictionary.
        """

        path = '/items/' + str(item) + '.xml'
        root = self._get_element_from_resource(path)
        return self._dict_from_node(root, True)

    def item_metadata(self, item):
        """
        Returs metadata for an item as a simple dictionary, with dc fields
        as keys.

        Parameters
        ----------
        item : string or int
            An item id.

        Returns
        -------
        dict : metadata, with dc fields as keys.
        """

        i = self.item(item)
        return { me['element'] + '.' + me['qualifier']:me['value'] for me \
                  in i['metadata']['metadataentity'] }

    def all_collections(self):
        """
        Retrieves details about all of the collections to which a user has
        access.

        Returns
        -------
        list : a list of nested dictionaries.
        """

        root = self._get_element_from_resource('/collections.xml')
        return [ self._dict_from_node(node) for node in root ]

    def list_bitstream_ids(self, item):
        """
        Returns a list of bitstream ids for an item.

        Parameters
        ----------
        item : string or int
            An item id.

        Returns
        -------
        list : a list of bitstream ids.
        """

        i = self.item(item)
        if type(i['bitstreams']['bitstreamentity']) is dict:    # One bitstream.
            return [ i['bitstreams']['bitstreamentity']['id'] ]
        else:
            return [ be['id'] for be in i['bitstreams']['bitstreamentity'] ]

    def bitstream(self, bitstream):
        """
        Returns information about a bitstream.

        Parameters
        ----------
        item : string or int
            An item id.

        Returns
        -------
        dict : a nested dictionary.
        """

        path = '/bitstream/' + str(bitstream) + '.xml'
        root = self._get_element_from_resource()
        bitstreamentities = root.findall('.//bitstreamentity')
        for b in bitstreamentities:
            if self._dict_from_node(b)['id'] == str(bitstream):
                return self._dict_from_node(b, True)

