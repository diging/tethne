"""
Classes and methods related to the :class:`.TAPModel`\.
"""

import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

import numpy as np
import networkx as nx
import warnings

from ..basemodel import BaseModel

class TAPModel(object):
    """
    Represents a Topical Affinity Propogation (TAP) social model.
    
    The TAP model assumes that authors can be influenced by other authors with
    whom they are acquainted to adopt particular features (eg topics) in their
    writing. The TAP model takes a weighted social graph, and the probabilities
    that each author will generate a document containing particular topics. For
    a complete description of the model, see 
    `Tang et al. 2009 <https://wiki.engr.illinois.edu/download/attachments/186384416/KDD09_Social_Influence_Analysis.pdf?version=1&modificationDate=1255578264000>`_,
    or the `presentation <http://videolectures.net/kdd09_tang_sia/>`_ on which
    the paper was based.
    
    Parameters
    ----------
    G : :class:`.nx.Graph()`
        Should have ``weight`` attribute in the range [0.,1.] indicating the
        strength of the relationship between authors (eg the number of
        coauthored papers).
    theta : dict
        Distribution over topics for authors. Should have ``N`` keys, with 
        values shaped ``T``; ``N == len(G.nodes())`` and ``T`` is the number of
        topics.
        
    Examples
    --------
    
    There are two ways to generate a :class:`.TAPModel`\:
    
    To generate a :class:`.TAPModel` from a single :func:`.coauthors` graph and
    a :mod:`.corpus` model, instantiate and build a :class:`.TAPModel` directly:
    
    .. code-block:: python
       
       >>> from tethne.networks import authors
       >>> g = authors.coauthors(C.all_papers())    # C is a Corpus.
       
       >>> from tethne.model import managers, TAPModel
       >>> atheta = managers.TAPModelManager().author_theta(C.all_papers())
       
       >>> model = TAPModel(g, atheta)
       >>> model.build()
    
    To generate a :class:`.TAPModel` from a :class:`.Corpus` that takes time
    into account, use a :class:`.TAPModelManager`\.
       
    Use :func:`TAPModel.graph` to retrieve an influence graph for a particular
    topic.
    
    """
    def __init__(self, G, theta, damper=0.5):

        assert len(theta) == len(G.nodes())
        
        self.G = G     # TODO: should take G as an input.
        self.theta = theta

        # These dictionaries are indexed by node id and not necessarily 0-based.
        self.a = {}
        self.b = {}
        self.r = {}
        self.g = {}

        self.damper = damper   # This was not very clear in the paper.

        self.N = len(self.G.nodes())
        self.M = len(self.G.edges())

        logger.debug('Loaded graph with {0} nodes and {1} edges.'
                                                        .format(self.N, self.M))
        
        self.T = self.theta.values()[0].shape[0]
        self.N_d = len(self.theta)

        self.yold = { i:{k:0 for k in xrange(self.T) }
                        for i in sorted(self.G.nodes()) }
        self.yold_values = { i:{k:0. for k in xrange(self.T) }
                                for i in sorted(self.G.nodes()) }

        logger.debug('Loaded distributions over {0} topics for {1} nodes.'
                                                      .format(self.T, self.N_d))
        
        self.dc_trace = []
    
    # Obligatory methods.
    def _item_description(self, i, **kwargs):
        """
        Yields author probability distribution over topics.
        """
        this_theta = self.theta[i]
        return [ (t, this_theta[t]) for t in xrange(this_theta.size) ]
    
    def _item_relationship(self, i, j, **kwargs):
        """
        Yields the influence strength from i to j for each topic.
        """
        try:
            return [ (k, G[i][j]['weight']) for k, G in self.MU.iteritems() ]
        except AttributeError:
            raise RuntimeError('Must build model first.')
        except KeyError:
            return []
    
    def _dimension_description(self, d, **kwargs):
        """
        Simply returns d; there is no additional information about dimensions.
        """
        return d
    
    def _dimension_relationship(self, d, e, **kwargs):
        """
        Simply returns (d,e); there is no additional information about 
        dimensions.
        """
        return d,e
    
    # TAP-specific methods.
    def _node_index(self, G, i):
        return G.nodes().index(i)

    def _calculate_g(self):
        """eq. 1"""
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
            self.g[i] = np.zeros((len(n)+1, self.T))

            sumin = np.zeros((self.T))
            sumout = np.zeros((self.T))
        
            for t, attr in self.G[i].iteritems():
                for k in xrange(self.T):
                    w = float(attr['weight'])     
                    sumout[k] = sumout[k] + w * self.theta[t][k]

            
            for t, attr in self.G[i].iteritems():
                for k in xrange(self.T):
                    w = float(attr['weight'])
                    sumin[k] = sumin[k] + w * self.theta[i][k]
                
                    # calculate y z, i=i ;; [n,] should be the last row.
                    self.g[i][len(n),k] = sumin[k] / (sumin[k] + sumout[k])

            j = 0
            for t,attr in self.G[i].iteritems():
                for k in xrange(self.T):
                    w = float(attr['weight'])
                    self.g[i][j,k] = w*self.theta[t][k]/(sumin[k]+sumout[k])
                j+=1

    def _calculate_b(self):
        """eq. 8"""
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
            self.b[i] = np.zeros((len(n)+1, self.T))
            self.r[i] = np.zeros((len(n)+1, self.T))
            self.a[i] = np.zeros((len(n)+1, self.T))
    

            for z in xrange(self.T):    # TODO: simplify this.
                sum_ = np.sum(self.g[i][:,z])
                for j in xrange(len(n)+1):
                    self.b[i][j,z] = np.log(self.g[i][j,z]/sum_)

    def _update_r(self):
        """eq. 5"""
    
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
        
            fmx = np.zeros((self.T))
            smx = np.zeros((self.T))
            temp = 0.
            maxk = {}
        
            if len(n) < 1:  # Node has no neighbors.
                for k in xrange(self.T):
                    self.r[i][0,k] = float(self.b[i][0,k])
            else:
                for k in xrange(self.T):
                    fmx[k] = float(self.b[i][0,k] + self.a[i][0,k])
                    smx[k] = float(self.b[i][1,k] + self.a[i][1,k])
                    maxk[k] = 0
                    # Setting a minimum difference >> 1e-5 to avoid weird
                    #  precision issues.
                    if smx[k] - fmx[k] > float(1e-5):
                        inter = float(fmx[k])
                        inter_ = float(smx[k])
                        fmx[k] = float(inter_)
                        smx[k] = float(inter)
                        maxk[k] = 1

                for j in xrange(2, len(n)+1):
                    for k in xrange(self.T):
                        temp = float(self.a[i][j,k] + self.b[i][j,k])
                        # (see above) precision issues.
                        if temp - smx[k] > float(1e-5):
                            inter = float(temp)
                            inter_ = float(smx[k])
                            temp = float(inter_)
                            smx[k] = float(inter)
                    
                        # (see above) precision issues.
                        if smx[k] - fmx[k] > float(1e-5):

                            inter = float(fmx[k])
                            inter_ = float(smx[k])
                            fmx[k] = float(inter_)
                            smx[k] = float(inter)
                            maxk[k] = int(j)
            
                for j in xrange(len(n) + 1):
                    for k in xrange(self.T):
                        if j == maxk[k]:
                            self.r[i][j,k] = ((self.b[i][j,k]-smx[k])*(1.-self.damper))+(self.r[i][j,k]*self.damper)
                        else:
                            self.r[i][j,k] = ((self.b[i][j,k]-fmx[k])*(1.-self.damper))+(self.r[i][j,k]*self.damper)
                

    def _update_a(self):
        fmx = {} 
        smx = {}
        maxk = {}

        for j in sorted(self.G.nodes()):
            fmx[j] = np.zeros((self.T))
            smx[j] = np.zeros((self.T))
        
            maxk[j] = np.array( [-1] * self.T )

            n = sorted(self.G.neighbors(j))
        
            # maxk[N] records the maximum value of min{r z, kj, 0}
            if len(n) < 1:
                for k in xrange(self.T):
                    fmx[j][k] = 0.
        
            else:
                neighbour = n[0]
                pos = sorted(self.G.neighbors(neighbour)).index(j)
            
                for k in xrange(self.T):
                    fmx[j][k] = min( self.r[neighbour][pos, k], 0. )
                    maxk[j][k] = neighbour
            
                if len(n) >= 2:
                    neighbour = n[1]
                    pos = sorted(self.G.neighbors(neighbour)).index(j)
                
                    for k in xrange(self.T):
                        smx[j][k] = min( self.r[neighbour][pos, k], 0. )
                        # (see above) precision issues.
                        if smx[j][k] - fmx[j][k] > float(1e-5):
                            inter = float(fmx[j][k])
                            inter_ = float(smx[j][k])
                            fmx[j][k] = float(inter_)
                            smx[j][k] = float(inter)
                            
                            maxk[j][k] = neighbour
            
                    for i in xrange(2, len(n)):
                        neighbour = n[i]
                        pos = sorted(self.G.neighbors(neighbour)).index(j)
                    
                        for k in xrange(self.T):
                            temp = min ( self.r[neighbour][pos,k] , 0. )
                            # (see above) precision issues.
                            if temp - smx[j][k] > float(1e-5):
                                inter = float(temp)
                                inter_ = float(smx[j][k])
                                temp = float(inter_)
                                smx[j][k] = float(inter)
                            
                            # (see above) precision issues.
                            if smx[j][k] - fmx[j][k] > float(1e-5):
                                inter = float(fmx[j][k])
                                inter_ = float(smx[j][k])
                                fmx[j][k] = float(inter_)
                                smx[j][k] = float(inter)
                                maxk[j][k] = int(neighbour)

        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
            for k in xrange(self.T): # a_ii
                self.a[i][len(n), k] = fmx[i][k]
        
            for j in n: # a_ij
                j_index = n.index(j)
                n_j = sorted(self.G.neighbors(j))
                for k in xrange(self.T):
                    if i == maxk[j][k]:
                        use = smx[i][k]
                    else:
                        use = fmx[i][k]
                        
                    qt = max ( self.r[j][len(n_j), k], 0 )
                    af = (-1*min ( self.r[j][len(n_j), k], 0 )) - use
                    self.a[i][j_index,k] = (min(qt, af) * (1.-self.damper)) + \
                                           (self.a[i][j_index,k] * self.damper)
                    
            
    def _check_convergence(self, nc):
        """
        Returns false if the ranking of influencing nodes hasn't changed in a 
        while.
        """

        dc = 0
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
            for k in xrange(self.T):
                last = 0.
                
                j_max = 0
                j_max_value = 0.
                # Get most influential neighbor, j_max.
                for j in xrange(len(n)):
                    f = float(self.r[i][j, k] + self.a[i][j, k])
                    if f > last:
                        j_max = int(j)
                        j_max_value = float(f)
                        last = float(f)
    
                if self.iteration > 50:
                    if self.yold[i][k] != j_max and (j_max_value - self.yold_values[i][k]) > float(1e-5):
                        dc += 1
                        self.yold[i][k] = int(j_max)
                        self.yold_values[i][k] = float(j_max_value)

        if dc == 0: # No change?
            nc += 1
        else:
            nc = 0
        
        self.dc_trace.append(dc)
        cont = True
        
        pct_change = np.mean(self.dc_trace[-4:])/self.M
        var_change = np.var(self.dc_trace[-4:])/self.M

        if pct_change < 0.01 and var_change < 0.01:
            cont = False
        
        return nc, cont, dc

    def _calculate_mu(self):
        self.MU = {}
        
        def eq_9(a, b, c): # Equation 9.
            return 1./ (1. + np.exp(-1. * (self.r[a][b,c] + self.a[a][b,c])))

        # Export
        for k in xrange(self.T):
            subg = nx.DiGraph()
            
            # Influence
            for i in sorted(self.G.nodes()):
                n = sorted(self.G.neighbors(i))
                for j in sorted(self.G.nodes()):
                    if j in n:
                        j_ = n.index(j)
                        i_ = sorted(self.G.neighbors(j)).index(i)
                
                        j_i = eq_9(i, j_, k)
                        i_j = eq_9(j, i_, k)

                        if j_i > i_j:   # Add only strongest edge.
                            subg.add_edge(j, i, weight=float(j_i))
                        else:
                            subg.add_edge(i, j, weight=float(i_j))
                            
            # Add theta as node attribute.
            for i in sorted(self.G.nodes()):
                 # Networkx doesn't like Numpy dtypes.
                try:
                    subg.node[i]['theta'] = float(self.theta[i][k])
                except KeyError:
                    subg.add_node(i, theta=float(self.theta[i][k]))
    
            self.MU[k] = subg
    
    def prime(self, alt_r, alt_a, alt_G):
        """
        Assign posterior ``r`` and ``a`` values from a previous model as priors
        for this model.
        
        Parameters
        ----------
        alt_r : dict
            { i: array-like [ j, k ] for i in G.nodes() }
            Must be from a model with the same topics.
        alt_a :dict
            { i: array-like [ j, k ] for i in G.nodes() }
            Must be from a model with the same topics.
        alt_G : :class:`.nx.Graph`
            Need not be the same shape as G, but node names must be consistent.
        """
        
        for i in alt_G.nodes():
            alt_n = sorted(alt_G.neighbors(i))
            if i in sorted(self.G.nodes()):
                # alt_r and alt_a must be from a model with the same topics.
                assert alt_r[i].shape[1] == self.r[i].shape[1]
                assert alt_a[i].shape[1] == self.a[i].shape[1]
                
                n = sorted(self.G.neighbors(i))
                for j in alt_n:
                    if j in n:
                        j_ = n.index(j)
                        alt_j_ = alt_n.index(j)

                        for k in xrange(self.T):
                            self.r[i][j_,k] = alt_r[i][alt_j_,k]
                            self.a[i][j_,k] = alt_a[i][alt_j_,k]

    def build(self, max_iter=1000):
        """
        Estimate the :class:`.TAPModel`\.
        
        This may take a considerable amount of time, depending on the size of
        the social graph and the number of features/topics.
        
        Parameters
        ----------
        max_iter : int
            (default: 500) Maximum number of iterations.
        """

        #	1.1 calculate g(vi,yi,z)
        self._calculate_g()
        logger.debug('Calculated g')

        #   1.2 Eq8, calculate bz,ij
        self._calculate_b()
        logger.debug('Calculated b')        
        
        logger.debug('start iterations')
        nc = 0
        self.iteration = 0
        cont = True

        while cont:
            self.iteration += 1
            
            # Check for convergence every 10 iterations.
            if self.iteration % 10 == 0:            
                nc,cont, dc = self._check_convergence(nc)            
                logger.debug('iteration {0}, nc={1}, dc={2}'
                                                .format(self.iteration, nc, dc))

            self._update_r()
            self._update_a()
            
            if self.iteration >= max_iter:
                cont = False

        self._calculate_mu()

    def graph(self, k):
        """
        Retrieve an influence graph for a particular topic.
           
        Parameters
        ----------
        k : int
            A topic index.
        
        Returns
        -------
        NetworkX DiGraph object
            An influence graph. Edge direction and their ``weight`` indicate
            influence strength. Node attribute ``theta`` is the probability
            that an author will generate a paper that includes topic ``k``.
            
        Examples
        --------
        
        .. code-block:: python
        
           >>> g = model.graph(0)   # model is a TAPModel.
           >>> g
           <networkx.classes.graph.Graph at 0x10b2692d0>
        
        You can then use a method from :mod:`.writers` to generate a network 
        datafile for visualization in `Cytoscape <http://www.cytoscape.org>`_ or 
        `Gephi <http://gephi.org>`_.
        
        .. figure:: _static/images/tap_topic0.png
           :width: 600
           :align: center
        
        """
    
        return self.MU[k]