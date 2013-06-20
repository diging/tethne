"""
Contains utilities for building networks in networks.py
"""
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
    Return number of shared objects between listA, listB as a list
    """
    if (listA is None) or (listB is None):
        return []
    else:
        return list(set(listA) & set(listB))


def subdict(super_dict, keys):
    """
    Returns a subset of the super_dict with the specified keys
    """
    sub_dict = {}
    valid_keys = super_dict.keys()
    for key in keys:
        if key in valid_keys:
            sub_dict[key] = super_dict[key]

    return sub_dict


def concat_list(listA, listB, delim=' '):
    """
    Concatenate list elements pair-wise with the delim character
    Returns the concatenated list
    Raises index error if lists are not parallel
    """
    #validate input
    if len(listA) != len(listB):
        raise IndexError('Input lists are not parallel.')

    #concatenate lists
    listC = []
    for i in xrange(len(listA)):
        listC.append(listA[i] + delim + listB[i])

    return listC


