import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('ERROR')

import numpy as np
import networkx as nx

from ..basemodel import BaseModel
from tethne.utilities import swap

class TAPModel(BaseModel):
    def __init__(self, G, theta, damper=0.5):
        """
        
        Parameters
        ----------
        G : :class:`.nx.Graph()`
            Should have 'weight' attribute in [0.,1.].
        theta : dict
            Should have N keys, with values shaped T; N == len(G.nodes()) and T
            is the number of topics.
        """
        
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
        
        #	1.1 calculate g(vi,yi,z)
        self._calculate_g()
        logger.debug('Calculated g')

        #   1.2 Eq8, calculate bz,ij
        self._calculate_b()
        logger.debug('Calculated b')
    
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
                this = t
                for k in xrange(self.T):
                    w = float(attr['weight'])     
                    sumout[k] = sumout[k] + w * self.theta[this][k]

            for t, attr in self.G[i].iteritems():
                for k in xrange(self.T):
                    w = float(attr['weight'])
                    this = i
                    sumin[k] = sumin[k] + w * self.theta[this][k]
                
                    # calculate y z, i=i ;; [n,] should be the last row.
                    self.g[i][len(n),k] = sumin[k] / (sumin[k] + sumout[k])
                
            j = 0
            for t,attr in self.G[i].iteritems():
                for k in xrange(self.T):
                    w = float(attr['weight'])
                    this = i
                    self.g[i][j,k] = w*self.theta[this][k]/(sumin[k]+sumout[k])
                j+=1
            
    def _calculate_b(self):
        """eq. 8"""
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
            self.b[i] = np.zeros((len(n)+1, self.T))
            self.r[i] = np.zeros((len(n)+1, self.T))
            self.a[i] = np.zeros((len(n)+1, self.T))
            
            sum_ = np.zeros((self.T))
        
            for j in xrange(len(n)+1):   # +1 to include self.
                for k in xrange(self.T):
                    sum_[k] += self.g[i][j,k]
            for j in xrange(len(n)+1):
                for k in xrange(self.T):
                    self.b[i][j,k] = np.log(self.g[i][j,k] / sum_[k])

    def _update_r(self):
        """eq. 5"""
    
        for i in sorted(self.G.nodes()):
            n = sorted(self.G.neighbors(i))
        
            fmx = np.zeros((self.T))
            smx = np.zeros((self.T))
            temp = 0.
            maxk = {}
        
            if len(n) < 1:  # node has no neighbors
                for k in xrange(self.T):
                    self.r[i][0,k] = self.b[i][0,k]
            else:
                for k in xrange(self.T):
                    fmx[k] = self.b[i][0,k] + self.a[i][0,k]
                    smx[k] = self.b[i][1,k] + self.a[i][1,k]
                    maxk[k] = 0
                    # Setting a minimum difference >> 1e-5 to avoid weird
                    # precision issues.
                    if smx[k] - fmx[k] > float(1e-5):
                        fmx[k], smx[k] = swap(fmx[k], smx[k])
                        maxk[k] = 1

                for j in xrange(2, len(n)+1):
                    for k in xrange(self.T):
                        temp = self.a[i][j,k] + self.b[i][j,k]
                        # (see above) precision issues.
                        if temp - smx[k] > float(1e-5):
                            temp, smx[k] = swap(temp, smx[k])
                    
                        # (see above) precision issues.
                        if smx[k] - fmx[k] > float(1e-5):
                            fmx[k], smx[k] = swap(fmx[k], smx[k])
                            maxk[k] = j
            
                for j in xrange(len(n) + 1):
                    for k in xrange(self.T):
                        if j == maxk[k]:
                            self.r[i][j,k] = ((self.b[i][j,k] - smx[k]) *      \
                                                (1. - self.damper) ) +         \
                                              ( self.r[i][j,k] * self.damper )
                        else:
                            self.r[i][j,k] = ((self.b[i][j,k] - fmx[k]) *      \
                                                (1. - self.damper) ) +         \
                                              ( self.r[i][j,k] * self.damper )
                

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
                pos = self.G.neighbors(neighbour).index(j)
            
                for k in xrange(self.T):
                    fmx[j][k] = min( self.r[neighbour][pos, k], 0. )
                    maxk[j][k] = neighbour
            
                if len(n) >= 2:
                    neighbour = n[1]
                    pos = self.G.neighbors(neighbour).index(j)
                
                    for k in xrange(self.T):
                        smx[j][k] = min( self.r[neighbour][pos, k], 0. )
                        # (see above) precision issues.
                        if smx[j][k] - fmx[j][k] > float(1e-5):
                            fmx[j][k], smx[j][k] = swap(fmx[j][k],smx[j][k])
                            maxk[j][k] = neighbour
            
                    for i in xrange(2, len(n)):
                        neighbour = n[i]
                        pos = self.G.neighbors(neighbour).index(j)
                    
                        for k in xrange(self.T):
                            temp = min ( self.r[neighbour][pos,k] , 0. )
                            # (see above) precision issues.
                            if temp - smx[j][k] > float(1e-5):
                                temp, smx[j][k] = swap(temp, smx[j][k])
                            # (see above) precision issues.
                            if smx[j][k] - fmx[j][k] > float(1e-5):
                                fmx[j][k], smx[j][k] = swap(fmx[j][k],smx[j][k])
                                maxk[j][k] = neighbour                                          

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
                    f = self.r[i][j, k] + self.a[i][j, k]
                    if f > last:
                        j_max = int(j)
                        j_max_value = float(f)
                        last = float(f)
    
                if self.iteration > 20:
                    if self.yold[i][k] != j_max \
                        and j_max_value - self.yold_values[i][k] > float(1e-5):
                        dc += 1
                        self.yold[i][k] = int(j_max)
                        self.yold_values[i][k] = float(j_max_value)

        if dc == 0: # No change?
            nc += 1
        else:
            nc = 0
    
        cont = True
        if nc == 50:
            cont = False
        
        return nc, cont

    def _calculate_mu(self):
        self.MU = {}

        # Export
        for k in xrange(self.T):
            subg = nx.DiGraph()
            
            # Influence
            for i in sorted(self.G.nodes()):
                n = sorted(self.G.neighbors(i))
                for j in sorted(self.G.nodes()):
                    if j in n:
                        j_ = n.index(j)
                        i_ = self.G.neighbors(j).index(i)
                
                        # Equation 9.
                        j_i = 1./ (1. + \
                              np.exp(-1. * (self.r[i][j_,k] + self.a[i][j_,k])))
                        i_j = 1./ (1. + \
                              np.exp(-1. * (self.r[j][i_,k] + self.a[j][i_,k])))
                
                        if j_i > i_j:   # Add only strongest edge.
                            subg.add_edge(j, i, weight=float(j_i))
                        else:
                            subg.add_edge(i, j, weight=float(i_j))
                            
            # Add theta as node attribute.
            for i in sorted(self.G.nodes()):
                 # Networkx doesn't like Numpy dtypes.
                subg.node[i]['theta'] = float(self.theta[i][k])
                
            self.MU[k] = subg
    
    def prime(self, alt_r, alt_a, alt_G):
        """
        Prime r and a with values from a previous model.
        
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
            alt_n = alt_G.neighbors(i)            
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

    def graph(self, k):
        return self.MU[k]

    def build(self, max_iter=500):
        logger.debug('start iterations')
        nc = 0
        self.iteration = 0.
        cont = True

        while cont:
            self.iteration += 1
            if self.iteration % 10 == 0:
                logger.debug('iteration {0}, nc={1}'.format(self.iteration, nc))

            self._update_r()
            self._update_a()
            nc,cont = self._check_convergence(nc)
            
            if self.iteration >= max_iter:
                cont = False

        self._calculate_mu()