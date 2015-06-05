"""
A :class:`.Corpus` organizes :class:`.Paper`\s for analysis.
"""

from collections import Counter

from tethne.classes.feature import FeatureSet, Feature
from tethne.utilities import _iterable


def _tfidf(f, c, C, DC, N):
    tf = float(c)
    idf = np.log(float(N)/float(DC))
    return tf*idf

def _filter(s, C, DC):
    if C > 3 and DC > 1 and len(s) > 3:
        return True
    return False
    
    
class Corpus(object):
    @property
    def papers(self):
        return self.indexed_papers.values()

    def __init__(self, papers=None, index_by=None,
                 index_fields=['authors', 'citations'],
                 index_features=['authors', 'citations'], **kwargs):
        """
        Parameters
        ----------
        paper : list
        index_by : str
        index_fields : str or iterable of strs
        """

        if not index_by:
            if hasattr(papers[0], 'doi'):        index_by = 'doi'
            elif hasattr(papers[0], 'wosid'):    index_by = 'wosid'
            elif hasattr(papers[0], 'uri'):        index_by = 'uri'            

        self.indexed_papers = {getattr(paper, index_by): paper
                               for paper in papers}

        self.index_by = index_by
        self.indices = {}
        self.features = {}
        self.slices = []

        if index_features:
            for feature_name in index_features:
                self.index_feature(feature_name)

        if index_fields:
            for attr in _iterable(index_fields):
                self.index(attr)

    def index_feature(self, feature_name):
        """
        Create a new :class:`.Feature` from the attribute ``feature_name``
        in each :class:`.Paper`\.
        """
        features = {p: Feature(getattr(p, feature_name)) for p
                    in self.papers if hasattr(p, feature_name)}
        self.features[feature_name] = FeatureSet(features)

    def index(self, attr):
        """
        Index ``papers`` by ``attr``
        """

        self.indices[attr] = {}
        for i, paper in self.indexed_papers.iteritems():
            if hasattr(paper, attr):
                value = getattr(paper, attr)
                for v in _iterable(value):
                    if type(value) is Feature:
                        v_ = v[:-1]
                    else:
                        v_ = v

                    if hasattr(v_, '__iter__'):
                        if len(v_) == 1:
                            t = type(v_[0])
                            v_ = t(v_[0])

                    if v_ not in self.indices[attr]:
                        self.indices[attr][v_] = []
                    self.indices[attr][v_].append(i)

    
    def __getitem__(self, args):
        attr, value = args
        return [self.indexed_papers[p] for p in self.indices[attr][value]]


    def slice(self, method='period', window_size=1, step_size=1, papers=False):
        if 'date' not in self.indices:
            self.index('date')
        
        
        start = min(self.indices['date'].keys())
        end = max(self.indices['date'].keys())
        while start <= end - (window_size - 1):
            yield [pset for i in xrange(start, start + window_size, 1) 
                   for pset in self['date', i]]
            start += step_size
        
            
    def distribution(self, **slice_kwargs):
        return [len(papers) for papers in self.slice(**slice_kwargs)]
        
    
    def feature_distribution(self, feature, element, mode='counts', **slice_kwargs):
        def get_value(d, elem):
            if elem in d:
                return d[elem]
            return 0
            
        values = []
        for papers in self.slice(**slice_kwargs):
            values.append(sum([get_value(dict(getattr(paper, feature)), element)
                               for paper in papers]))
        return values

