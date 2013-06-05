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


