"""
Classes and methods related to the :class:`.TAPModelManager`\.
"""

import os
import re
import shutil
import tempfile
import subprocess
import numpy as np

from networkx import Graph
import networkx as nx

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

from ...classes import GraphCollection
from ..social import TAPModel
from ..managers import SocialModelManager

class TAPModelManager(SocialModelManager):
    """
    Generates a time-sensitive set of :class:`.TAPModel`\s from a 
    :class:`.Corpus`\, a :mod:`.corpus` model, and a coauthorship 
    :class:`.GraphCollection`\.
    
    The standard :class:`.TAPModel` is not sensitive to time, in that influence
    among authors is estimated without regard to the sequence in which those
    authors adopt features in their papers. The :class:`.TAPModelManager` 
    generates :class:`.TAPModel`\s sequentially, using the posterior influence
    values from one time-period as priors for the next time-period. The
    :class:`.TAPModel` for the latest time-period, therefore, should reflect
    both the structure of the network in that time-period as well as the
    evolution of that network and the sequence in which authors adopt features
    in their work.
    
    Parameters
    ----------
    D : :class:`.Corpus`
    G : :class:`.GraphCollection`
    model : :class:`.LDAModel`
    
    Examples
    --------
    
    Starting with some JSTOR DfR data, a typical workflow might look something
    like this:
    
    .. code-block:: python
    
       >>> from tethne.readers import dfr                  # 1. Create a Corpus.
       >>> from nltk.corpus import stopwords
       >>> C = dfr.read_corpus('/path/to/dataset/', 'uni', stopwords.word())
       >>> C.slice('date', 'time_period', window_size=5)
       
       >>> from tethne import GraphCollection          # 2. Coauthorship graphs.
       >>> G = GraphCollection().build(C, 'date', 'authors', 'coauthors')
       >>> G.graphs
       
       >>> from tethne.model import MALLETModelManager        # 3. Corpus model.
       >>> outpath = '/path/to/my/working/directory'
       >>> mallet = '/Applications/mallet-2.0.7'
       >>> M = MALLETModelManager(C, 'wc_filtered', outpath, mallet_path=mallet)
       >>> model = M.build(Z=50, max_iter=300)
       
       >>> from tethne.model import TAPModelManager        # 4. Build TAPModels.
       >>> T = TAPModelManager(C, G, model)
       >>> T.build()

    To visualize the :class:`.TAPModel`\s, use 
    :func:`TAPModelManager.graph_collection` to generate a 
    :class:`.GraphCollection` of influence graphs for a particular topic. For 
    example:
    
    .. code-block:: python
    
       >>> IG = T.graph_collection(0)
    
    You can then use a method from :mod:`.writers` to export a network datafile
    for visualization in `Cytoscape <http://www.cytoscape.org>`_ or
    `Gephi <http://gephi.org>`_.
    
    .. figure:: _static/images/tap_topic0.png
       :width: 600
       :align: center
       
    """
    
    def __init__(self, D=None, G=None, model=None, **kwargs):
        """

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
            Key in :class:`.Paper` used to index :class:`.Corpus`\.
            
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
                # In that case, just give zero values for those authors.
                logger.debug('TAPModelManager.author_theta(): KeyError on {0}'
                                                        .format(p[indexed_by]))

                dist = np.array(np.zeros(self.topicmodel.Z))
                # Give 0 values for authors.
                for author in p.authors():
                    if authors is not None:
                        if author not in authors:
                            continue
                
                    a = authors[author]
                    if a in a_topics:
                        a_topics[a].append(dist)
                    else:
                        a_topics[a] = [ dist ]

        shape = ( len(a_topics), self.topicmodel.Z )
        logger.debug('TAPModelManager.author_theta(): initialize with shape {0}'
                                                                 .format(shape))

        a_theta = {}
        for a, dists in a_topics.iteritems():
            a_dist = np.zeros(( self.topicmodel.Z ))
            for dist in dists:
                a_dist += dist
            if np.sum(a_dist) != 0.0:
                a_theta[a] = a_dist/len(dists)
            else:
                a_theta[a] = np.array([1e-6]*self.topicmodel.Z)

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
                raise RuntimeError('No such axis in Corpus.')
                
            s = 0
            last = None
            for slice in sorted(self.D.get_slices(axis).keys()):
                logger.debug('TAPModelManager._run_model(): ' + \
                             'modeling slice {0}'.format(slice))

                if s > 0 and sequential:
                    alt_r = self.SM[last].r
                    alt_a = self.SM[last].a
                    alt_G = self.SM[last].G

                papers = self.D.get_slice(axis, slice, papers=True)
                include = { n[1]['label']:n[0]
                            for n in self.G[slice].nodes(data=True) }

                if len(include) < 1:    # Skip slices with no coauthorship.
                    logger.debug('TAPModelManager._run_model(): ' + \
                                 'skipping slice {0}.'.format(slice))
                    continue

                theta = self.author_theta(papers, authors=include)
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
            
            # Get node labels from original GraphCollection.
            labels = nx.get_node_attributes(self.G[slice], 'label')
            labels_ = { n:l for n,l in labels.iteritems()
                        if n in C[slice].nodes() }
            
            nx.set_node_attributes(C[slice], 'label', labels_)
    
        return C
                    
    
    def _load_model(self):
        pass
