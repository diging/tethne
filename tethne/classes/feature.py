from collections import Counter

from tethne.utilities import _iterable, argsort

class Feature(list):
    def __init__(self, data):
        if len(data) > 0:
            if type(data[0]) is tuple and type(data[0][-1]) in [float, int]:
                self.extend(data)
            else:
                self.extend(Counter(_iterable(data)).items())


    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.Feature`\.
        """
        if len(self) > 0:
            return set(zip(*self)[0])
        return set()


class FeatureSet(object):
    def __init__(self, features={}):
        self.index = {}
        self.lookup = {}
        self.counts = {}
        self.documentCounts = {}
        self.features = {}
        self.with_feature = {}

        for paper, feature in features.items():
            self.add(paper, feature)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def __getitem__(self, key):
        return getattr(self, key)

    def items(self):
        return self.features.items()

    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.FeatureSet`\.
        """
        return set(self.lookup.keys())

    def count(self, elem):
        return self.counts[self.lookup[elem]]

    def documentCount(self, elem):
        return self.documentCounts[self.lookup[elem]]

    def papers_containing(self, elem):
        return self.with_feature[self.lookup[elem]]

    def add(self, paper, feature):
        if type(feature) is not Feature:
            raise ValueError('`feature` must be an instance of class Feature')

        self.features[paper] = feature

        self.extend_index(feature.unique)
        for elem, count in feature:
            self.counts[self.lookup[elem]] += count
            self.documentCounts[self.lookup[elem]] += 1.
            self.with_feature[self.lookup[elem]].append(paper)

    def extend_index(self, elements):
        """
        
        """
        new_elements = list(set(elements) - self.unique)
        for i in xrange(len(new_elements)):
            x = len(self.index)
            self.index[x] = new_elements[i]
            self.lookup[new_elements[i]] = x
            self.counts[x] = 0.
            self.documentCounts[x] = 0.
            self.with_feature[x] = []

    def top(self, topn, by='counts'):
        """
        Get the top ``topn`` features in the :class:`.FeatureSet`\.
        """

        if by not in ['counts', 'documentCounts']:
            raise NameError('kwarg `by` must be "counts" or "documentCounts"')

        cvalues = getattr(self, by)
        top = [cvalues.keys()[i] for i in argsort(cvalues.values())][::-1]
        return [(self.index[x], cvalues[x]) for x in top][:topn]


def feature(f):
    """
    Decorator for properties that should be represented as :class:`.Feature`\s.
    """
    def deco(self):
        return Feature(f(self))
    return deco