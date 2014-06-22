import os
import re
import shutil
import tempfile
import subprocess
import numpy as np

from networkx import Graph

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

from ...classes import GraphCollection
from ..social import TAPModel
from ..managers import SocialModelManager

class TAPModelManager(SocialModelManager):
    """
    For managing the :class:`.TAPModel` .
    """
    
    def __init__(self, D, G, model, **kwargs):
        """
        
        Parameters
        ----------
        D : :class:`.DataCollection`
        G : :class:`.GraphCollection`
        model : :class:`.LDAModel`
        """

        super(TAPModelManager, self).__init__(**kwargs)
        self.D = D
        self.G = G
        self.topicmodel = model

        self.SM = {}
        self.SG = GraphCollection()
        
    def author_theta(self, papers, authors=None, indexed_by='doi'):
        """
        Generates distributions over topics for authors, based on distributions
        over topics for their papers.
        
        Parameters
        ----------
        papers : list
            Contains :class:`.Paper` instances.
        authors : dict
            Maps author names (LAST F) onto coauthor :class:`.Graph` indices.
        indexed_by : str
            Key in :class:`.Paper` used to index :class:`.DataCollection`\.
            
        Returns
        -------
        a_theta : dict
            Maps author indices (from coauthor :class:`.Graph`) onto arrays
            describing distribution over topics (normalized to 1).
        """
        
        a_topics = {}
        
        logger.debug('TAPModelManager.author_theta(): start for {0} papers'
                                                           .format(len(papers)))

        for p in papers:
            try:
                item = self.topicmodel.lookup[p[indexed_by]]
                t = self.topicmodel.item(item)
                
                dist = np.zeros(( len(t) ))
                for i,v in t:
                    dist[i] = v

                for author in p.authors():
                    # Only include authors in the coauthors graph.
                    if authors is not None:
                        if author not in authors:
                            continue
                
                    a = authors[author]
                    if a in a_topics:
                        a_topics[a].append(dist)
                    else:
                        a_topics[a] = [ dist ]

            except KeyError:    # May not be corpus model repr for all papers.
                logger.debug('TAPModelManager.author_theta(): KeyError on {0}'
                                                        .format(p[_indexed_by]))
                pass

        shape = ( len(a_topics), self.topicmodel.Z )
        logger.debug('TAPModelManager.author_theta(): initialize with shape {0}'
                                                                 .format(shape))

        a_theta = {}
        for a, dists in a_topics.iteritems():
            a_dist = np.zeros(( self.topicmodel.Z ))
            for dist in dists:
                a_dist += dist
            a_dist = a_dist/len(dists)
            a_theta[a] = a_dist/np.sum(a_dist)   # Should sum to <= 1.0.

        return a_theta
    
    def _run_model(self, max_iter=1000, sequential=True, **kwargs):
        logger.debug('TAPModelManager._run_model(): ' + \
                     'start with max_iter {0} and sequential {1}'
                                                  .format(max_iter, sequential))
        
        axis = kwargs.get('axis', None) # e.g. 'date'

        if axis is None:
            logger.debug('TAPModelManager._run_model(): axis is None')

            # single model.
            pass
        else:
            # model for each slice.
            if axis not in self.D.get_axes():
                raise RuntimeError('No such axis in DataCollection.')
                
            s = 0
            last = None
            for slice in sorted(self.D.get_slices(axis).keys()):
                logger.debug('TAPModelManager._run_model(): ' + \
                             'modeling slice {0}'.format(slice))

                if s > 0 and sequential:
                    alt_r, alt_a, alt_G = self.SM[last].r, self.SM[last].a, self.SM[last].G

                papers = self.D.get_slice(axis, slice, include_papers=True)
                include = {n[1]['label']:n[0] for n in self.G[slice].nodes(data=True) }

                if len(include) < 1:    # Skip slices with no coauthorship.
                    logger.debug('TAPModelManager._run_model(): ' + \
                                 'skipping slice {0}.'.format(slice))
                    continue

                theta = self.author_theta(papers, authors=include) #self.M[slice])
                model = TAPModel(self.G[slice], theta)
                
                if s > 0 and sequential:
                    model.prime(alt_r, alt_a, alt_G)
                
                logger.debug('TAPModelManager._run_model(): ' + \
                             'model.build() for slice {0}'.format(slice))
                model.build(max_iter=max_iter)
                logger.debug('TAPModelManager._run_model(): ' + \
                             'model.build() for slice {0} done'.format(slice))

                self.SM[slice] = model
                last = slice
                s += 1

    def graph_collection(self, k):
        """
        Generate a :class:`.GraphCollection` from the set of :class:`.TapModel`
        instances, for topic ``k``.
        
        Parameters
        ----------
        k : int
            Topic index.
        
        Returns
        -------
        C : :class:`.GraphCollection`
        """
        
        C = GraphCollection()
        for slice in self.SM.keys():
            C[slice] = self.SM[slice].graph(k)
    
        return C
                    
    
    def _load_model(self):
        pass
