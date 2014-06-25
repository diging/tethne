from ..basemodel import BaseModel
import numpy as np

import csv
from scipy.sparse import coo_matrix

class LDAModel(BaseModel):
    """
    Latent Dirichlet Allocation topic model.
    
    Items are documents, dimensions are topics.
    
    See: http://jmlr.org/papers/v3/blei03a.html
    """

    def __init__(self, theta, phi, metadata, vocabulary):
        """
        Initialize the :class:`.LDAModel`\.
        
        Parameters
        ----------
        theta : matrix-like
            Distribution of topics (cols) in documents (rows). Rows sum to 1.
        phi : matrix-like
            Distribution over words (cols) for topics (rows). Rows sum to 1.
        metadata : dict
            Maps matrix indices for documents onto a :class:`.Paper` key.
        """
        
        self.theta = theta
        self.M = theta.shape[0] # Number of documents.

        self.phi = phi
        self.Z = phi.shape[0]   # Number of topics.
        self.W = phi.shape[1]   # Number of terms.

        self.metadata = metadata
        self.vocabulary = vocabulary
        
        self.lookup = { v['id']:k for k,v in metadata.iteritems() }
    
    # Obligatory methods.
    def _item_description(self, i, **kwargs):
        """
        Yields proportion of each topic in document.
        """

        return [ (t, self.theta[i, t]) for t in xrange(self.theta.shape[1] ) ]
    
    def _item_relationship(self, i, j, **kwargs):
        """
        Yields the relationship between two documents.
        """
        # TODO: implement cosine-similarity or another similarity metric here.

        return None
    
    def _dimension_description(self, k, **kwargs):
        """
        Yields probability distribution over terms.
        """
        return [ (w, self.phi[k, w]) for w in xrange(self.phi.shape[1]) ]
    
    def _dimension_relationship(self, k, e, **kwargs):
        """
        Simply returns (k,e); there is no additional information about
        dimensions.
        """
        # TODO: imlement a similarity metric for topics.

        return None
        
    def _dimension_items(self, k, threshold, **kwargs):
        """
        Returns items that contain ``k`` at or above ``threshold``.
        
        Parameters
        ----------
        k : int
            Topic index.
        threshold : float
            Minimum representation of ``k`` in document.
            
        Returns
        -------
        description : list
            A list of ( item, weight ) tuples.
        """

        description = [ (self.metadata[i]['id'], self.theta[i, k])
                            for i in xrange(self.theta[:, k].size)
                            if self.theta[i, k] >= threshold ]
        return description
    
    def list_topic(self, k, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_list : list
            List of words in topic.
        """
        words = self.dimension(k, top=Nwords)
        as_list = [ self.vocabulary[w] for w,p in words ]

        return as_list
    
    def print_topic(self, k, Nwords=10):
        """
        Yields the top ``Nwords`` for topic ``k``.
        
        Parameters
        ----------
        k : int
            A topic index.
        Nwords : int
            Number of words to return.
        
        Returns
        -------
        as_string : str
            Joined list of words in topic.
        """

        as_string = ', '.join(self.list_topic(k, Nwords))
    
        return as_string
    
    def list_topics(self, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_dict : dict
            Keys are topic indices, values are list of words.
        """
        
        as_dict = {}
        for k in xrange(self.Z):
            as_dict[k] = self.list_topic(k, Nwords)
    
        return as_dict
    
    def print_topics(self, Nwords=10):
        """
        Yields the top ``Nwords`` for each topic.
        
        Parameters
        ----------
        Nwords : int
            Number of words to return for each topic.
        
        Returns
        -------
        as_string : str
            Newline-delimited lists of words for each topic.
        """
            
        as_dict = self.list_topics(Nwords)
        s = []
        for key, value in as_dict.iteritems():
            s.append('{0}: {1}'.format(key, ', '.join(value)))
        as_string = '\n'.join(s)
        
        return as_string

def from_mallet(top_doc, word_top, metadata):
    """
    Parse results from LDA modeling with MALLET.

    MALLET's LDA topic modeling algorithm produces a collection of output files.
    :func:`.read` takes the topic-document and (sparse) word-topic matrices, as
    tab-separated value files, along with a metadata file that maps
    each MALLET document id to a :class:`.Paper`\, using the `metadata_key`.

    Parameters
    ----------
    top_doc : string
        Path to topic-document datafile generated with --output-doc-topics.
    word_top : string
        Path to word-topic datafile generated with --word-topic-counts-file.
    metadata : string
        Path to tab-separated metadata file with :class:`.Paper` keys.

    Returns
    -------
    ldamodel : :class:`.LDAModel`

    """

    loader = MALLETLoader(top_doc, word_top, metadata)
    model = loader.load()

    return model

class MALLETLoader(object):
    def __init__(self, top_doc, word_top, metapath):
        self.top_doc = top_doc
        self.word_top = word_top
        self.metapath = metapath
    
    def load(self):
        self._handle_top_doc()
        self._handle_metadata()
        self._handle_word_top()
    
        self.model = LDAModel(self.theta, self.phi, self.metadata, self.vocabulary)
        return self.model

    def _handle_top_doc(self):
        """
        Used by :func:`.from_mallet` to reconstruct theta posterior
        distributions.
        
        Returns
        -------
        td : Numpy array
            Rows are documents, columns are topics. Rows sum to ~1.
        """

        path = self.top_doc

        D = []
        T = []
        P = []
        
        doc_index = {}

        with open(path, "rb") as f:
            i = -1
            reader = csv.reader(f, delimiter='\t')
            for line in reader:
                i += 1
                if i == 0: continue     # Avoid header row.
                
                d = int(line[0])
                id = str(line[1])
                doc_index[d] = id

                t = line[2:]
                tops = []
                for i in xrange(0,len(t)-1,2):
                    tops.append( (int(t[i]), float(t[i+1])) )
            
                for k,p in tops:
                    D.append(d)     # Document indices.
                    T.append(k)     # Topic indices.
                    P.append(p)     # Proportions.

            M = len(set(D)) # Number of documents.
            K = len(set(T)) # Number of topics.
            
        self.theta = coo_matrix((P, (D,T)), shape=(M,K)).todense()
        self.doc_index = doc_index

        return self.theta, self.doc_index
        
    def _handle_word_top(self):
        """
        Used by :func:`.from_mallet` to reconstruct phi posterior distributions.
        
        Returns
        -------
        wt : Numpy array
            Rows are topics, columns are words. Rows sum to ~1.
        """
        path = self.word_top

        vocabulary = {}

        W = []
        T = []
        C = []
        
        with open(path, "rb") as f:
            reader = csv.reader(f, delimiter=' ')
            for line in reader:
                w = int(line[0])
                term = str(line[1])
                vocabulary[w] = term
                for l in line[2:]:
                    k,c = l.split(':')
                    W.append(w)
                    T.append(int(k))
                    C.append(float(c))

        K = len(set(T))
        V = len(set(W))
                    
        phi = coo_matrix((C, (T,W)), shape=(K,V)).todense()

        # Normalize
        for k in xrange(K):
            phi[k,:] /= np.sum(phi[k,:])    
        
        self.phi = phi
        self.vocabulary = vocabulary
        
        return phi, vocabulary

    def _handle_metadata(self):
        """
        Used by :func:`.from_mallet` to read metadata file.    
        
        Returns
        -------
        md : dict
            Keys are document indices, values are identifiers from a 
            :class:`.Paper` property.
        """
        path = self.metapath

        lookup = { v:k for k,v in self.doc_index.iteritems() }
        
        md = {}

        with open(path, "rU") as f:
            reader = csv.reader(f, delimiter='\t')
            all_lines = [ l for l in reader ]
            keys = all_lines[0]
            lines = all_lines[1:]
            for l in lines:
                md[lookup[l[0]]] = { keys[i]:l[i] for i in xrange(0, len(l)) }

        self.metadata = md

        return md
