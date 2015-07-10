from collections import Counter, defaultdict

from tethne.utilities import _iterable, argsort

class Feature(list):
    """
    A :class:`.Feature` instance is a sparse vector of features over a given
    concept (usually a :class:`.Paper`\).
    
    For example, a :class:`.Feature` might represent word counts for a single
    :class:`.Paper`\.
    
    A :class:`.Feature` may be initialized from a list of ``(feature, value)``
    tuples...
    
    .. code-block:: python
    
       >>> myFeature = Feature([('the', 2), ('pine', 1), ('trapezoid', 5)])
       
    ...or by passing a list of raw feature tokens:
    
    .. codeblock:: python
    
       >>> myFeature = Feature(['the', 'the', 'pine', 'trapezoid', 'trapezoid',
       ...                      'trapezoid', 'trapezoid', 'trapezoid'])
       >>> myFeature
       [('the', 2), ('pine', 1), ('trapezoid', 5)]

    To get the set of unique features in this :class:`.Feature`\, use 
    :prop:`.Feature.unique`\:
    
    .. code-block:: python
    
       >>> myFeature.unique
       set(['the', 'pine', 'trapezoid'])
       
    Normalized feature values (so that all values sum to 1.) can be accessed
    using :prop:`.Feature.norm`\.
    
    .. code-block:: python
    
       >>> myFeature.norm
       [('the', 0.25), ('pine', 0.125), ('trapezoid', 0.625)]

    """

    def __init__(self, data):
        if len(data) > 0:
            self.extend(data)
            
    def __add__(self, data):
        if type(data[0]) is tuple and type(data[0][-1]) in [float, int]:
            # There may be overlap with existing features, 
            combined_data = defaultdict(type(data[0][-1]))
            for k, v in data + self:
                combined_data[k] += v
            return combined_data.items()
        else:
            return self.__add__(Counter(_iterable(data)).items())  # Recurses.
    
    def __sub__(self, data):
        if type(data[0]) is tuple and type(data[0][-1]) in [float, int]:
            combined_data = defaultdict(type(data[0][-1]))
            combined_data.update(dict(self))
            for k, v in data:
                combined_data[k] -= v
            return combined_data.items()
        else:
            return self.__sub__(Counter(_iterable(data)).items())  # Recurses.    
    
    def __iadd__(self, data):
        return self.extend(data)

    def __isub__(self, data):
        combined_data = self.__sub__(data)
        del self[:]
        super(Feature, self).extend(combined_data)
        return self        

    def extend(self, data):
        combined_data = self.__add__(data)  # Combines new and existing data.
        del self[:]                         # Clear old data.
        super(Feature, self).extend(combined_data)
        return self
            
    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.Feature`\.
        """
        if len(self) > 0:
            return set(zip(*self)[0])
        return set()

    @property
    def norm(self):
        T = sum(zip(*self)[1])
        return Feature([(i,float(v)/T) for i,v in self])

    def top(self, topn=10):
        """
        Get a list of the top ``topn`` features in this :class:`.Feature`\.
        
        Example
        -------
        
        .. code-block:: python
        
        >>> myFeature = Feature([('the', 2), ('pine', 1), ('trapezoid', 5)])
        >>> myFeature.top(1)
        [('trapezoid', 5)]
        
        Parameters
        ----------
        topn : int
        
        Returns
        -------
        list
        """
        return [self[i] for i in argsort(zip(*self)[1])[::-1][:topn]]
        
    def value(self, element):
        return dict(self)[element]


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

#    def __setitem__(self, key, value):
#        setattr(self, key, value)
#
    def __getitem__(self, key):
        return self.features[key]

    def __len__(self):
        return len(self.features)

    def items(self):
        return self.features.items()

    @property
    def unique(self):
        """
        The `set` of unique elements in this :class:`.FeatureSet`\.
        """
        return set(self.lookup.keys())

    @property
    def N_features(self):
        return len(self.unique)

    @property
    def N_documents(self):
        return len(self.features)

    def count(self, elem):
        if elem in self.lookup:
            return self.counts[self.lookup[elem]]
        else:
            return 0.

    def documentCount(self, elem):
        if elem in self.lookup:
            return self.documentCounts[self.lookup[elem]]
        else:
            return 0.

    def papers_containing(self, elem):
        return self.with_feature[self.lookup[elem]]

    def add(self, paper_id, feature):
        if type(feature) is not Feature:
            raise ValueError('`feature` must be an instance of class Feature')

        self.features[paper_id] = feature

        self.extend_index(feature.unique)
        for elem, count in feature:
            self.counts[self.lookup[elem]] += count
            self.documentCounts[self.lookup[elem]] += 1.
            self.with_feature[self.lookup[elem]].append(paper_id)

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
        
        Parameters
        ----------
        topn : int
            Number of features to return.
        by : str
            (default: 'counts') How features should be sorted. Must be 'counts' or 
            'documentcounts'.
        
        Returns
        -------
        list

        """

        if by not in ['counts', 'documentCounts']:
            raise NameError('kwarg `by` must be "counts" or "documentCounts"')

        cvalues = getattr(self, by)
        top = [cvalues.keys()[i] for i in argsort(cvalues.values())][::-1]
        return [(self.index[x], cvalues[x]) for x in top][:topn]

    def as_matrix(self):
        """
        
        """

        matrix = [[0. for e in xrange(self.N_features)]
                  for i in xrange(self.N_documents)]
        for i, p in enumerate(self.features.keys()):
            f = self.features[p]
            for e, c in f:
                j = self.lookup[e]
                matrix[i][j] = c

        return matrix

    def as_vector(self, p, norm=False):
        m = len(self.index.keys())

        if norm:
            values = dict(self.features[p].norm)
        else:
            values = dict(self.features[p])

        vect = []
        for i in xrange(m):
            e = self.index[i]
            if e in values:
                c = float(values[e])
            else:
                c = 0.
            vect.append(c)

        return vect


def feature(f):
    """
    Decorator for properties that should be represented as :class:`.Feature`\s.
    """
    def deco(self):
        return Feature(f(self))
    return deco