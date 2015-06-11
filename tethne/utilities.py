"""
Helper functions.
"""
import string
import copy
from HTMLParser import HTMLParser

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()

def argsort(seq):
    return sorted(range(len(seq)), key=seq.__getitem__)

def argmin(iterable):
    i_min = -1
    v_min = max(iterable)
    for i, v in enumerate(iterable):
        if v < v_min:
            i_min = i
            v_min = v
    return i_min

def argmax(iterable):
    i_max = -1
    v_max = min(iterable)
    for i, v in enumerate(iterable):
        if v > v_max:
            i_max = i
            v_max = v
    return i_max

def nonzero(iterable):
    return [i for i,v in enumerate(iterable) if abs(v) > 0.0]

def mean(iterable):
    if len(iterable) > 0:
        return float(sum(iterable))/len(iterable)
    else:
        return float('nan')

def _iterable(o):
	if hasattr(o, '__iter__'):
		return o
	else:
		return [o]

def _strip_punctuation(s):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in s if ch not in exclude)

def _space_sep(s):
	if len(s) > 3:
		return s
	return ' '.join(list(s))


def swap(u,v):
    """
    exchange the values of u and v
    """

    return copy.deepcopy(v),copy.deepcopy(u)

def contains(l, f):
    """
    Searches list l for a pattern specified in a lambda function f.
    """
    for x in l:
        if f(x):
            return True
    return False


def overlap(listA, listB):
    """
    Return list of objects shared by listA, listB.
    """
    if (listA is None) or (listB is None):
        return []
    else:
        return list(set(listA) & set(listB))


def subdict(super_dict, keys):
    """
    Returns a subset of the super_dict with the specified keys.
    """
    sub_dict = {}
    valid_keys = super_dict.keys()
    for key in keys:
        if key in valid_keys:
            sub_dict[key] = super_dict[key]

    return sub_dict


def attribs_to_string(attrib_dict, keys):
    """
    A more specific version of the subdict utility aimed at handling
    node and edge attribute dictionaries for NetworkX file formats such as
    gexf (which does not allow attributes to have a list type) by making
    them writable in those formats
    """
    for key, value in attrib_dict.iteritems():
        if (isinstance(value, list) or isinstance(value, dict) or
            isinstance(value, tuple)):
            attrib_dict[key] = str(value)

    return attrib_dict


def concat_list(listA, listB, delim=' '):
    """
    Concatenate list elements pair-wise with the delim character
    Returns the concatenated list
    Raises index error if lists are not parallel
    """

    # Lists must be of equal length.
    if len(listA) != len(listB):
        raise IndexError('Input lists are not parallel.')

    # Concatenate lists.
    listC = []
    for i in xrange(len(listA)):
        app = listA[i] + delim + listB[i]
        listC.append(app)

    return listC

def strip_non_ascii(s):
    """
    Returns the string without non-ASCII characters.

    Parameters
    ----------
    string : string
        A string that may contain non-ASCII characters.

    Returns
    -------
    clean_string : string
        A string that does not contain non-ASCII characters.

    """
    stripped = (c for c in s if 0 < ord(c) < 127)
    clean_string = ''.join(stripped)
    return clean_string

def strip_punctuation(s):
    exclude = set(string.punctuation)
    return ''.join(ch for ch in s if ch not in exclude)


def dict_from_node(node, recursive=False):
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
                value = dict_from_node(snode, True)
            else:
                value = len(snode)
        elif snode.text is not None:
            value = snode.text
        else:
            value = ''

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
    
class Dictionary:
    """
    A two-way index for integer/string pairs.
    """
    def __init__(self):
        self.by_str = {}
        self.by_int = {}
        
    def __setitem__(self, key, value):
        if type(key) == str:
            self.by_str[key] = value
            self.by_int[value] = key
        if type(key) == int:
            self.by_int[key] = value
            self.by_str[value] = key
    
    def __getitem__(self, key):
        if type(key) == str:
            return self.by_str[key]
        if type(key) == int:
            return self.by_int[key]