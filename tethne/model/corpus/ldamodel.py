from ..basemodel import BaseModel
import numpy as np

class LDAModel(BaseModel):
    """
    Latent Dirichlet Allocation topic model.
    
    Items are documents, dimensions are topics.
    
    See: http://jmlr.org/papers/v3/blei03a.html
    """

    def __init__(self, theta, phi, metadata, vocabulary=None):
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

        self.metadata = metadata
        self.vocabulary = vocabulary
        
        self.lookup = { v:k for k,v in metadata.iteritems() }
    
    # Obligatory methods.
    def _item_description(self, i, **kwargs):
        """
        Yields proportion of each topic in document.
        """
        theta_i = self.theta[i, :]
        return [ (t, theta_i[t]) for t in xrange(theta_i.size) ]
    
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
        phi_k = self.phi[k, :]
        return [ (w, phi_k[w]) for w in xrange(phi_k.size) ]
    
    def _dimension_relationship(self, k, e, **kwargs):
        """
        Simply returns (k,e); there is no additional information about
        dimensions.
        """
        # TODO: imlement a similarity metric for topics.

        return None
        
#    def topics_in_doc(self, d, topZ=None):
#        """
#        Returns a list of the topZ most prominent topics in a document.
#        
#        Parameters
#        ----------
#        d : str or int
#            An identifier from a :class:`.Paper` key.
#        topZ : int or float
#            Number of prominent topics to return (int), or threshold (float).
#            
#        Returns
#        -------
#        topics : list
#            List of (topic, proportion) tuples.
#        """
#        
#        index = self.lookup[d]
#        td = self.theta[index, :]
#        
#        if topZ is None:
#            topZ = td.shape[0]
#            
#        if type(topZ) is int:   # Return a set number of topics.
#            top_indices = td.argsort()[-topZ:][::1]
#        elif type(topZ) is float:   # Return topics above a threshold.
#            top_indices = [ z for z in np.argsort(td) if td[z] > topZ ]
#
#        top_values = [ td[z] for z in top_indices ]
#        
#        topics = zip(top_indices, top_values)
#        
#        return topics
#
#    def words_in_topic(self, z, topW=None):
#        if topW is None:
#            topW = 5
#
#        if type(topW) is int:
#            words = self.phi[z,:].argsort()[-topW:][::-1]
#
#        return [ ( w, self.phi[z,w]) for w in words ]

    def print_topic(self, z):
        words = [ self.vocabulary.by_int[w] for w,p
                    in self.words_in_topic(z, topW=topW) ]
        print ', '.join(words)
        return words

    def print_topics(self):
        """
        Prints a list of topics.
        """
        Z = self.phi.shape[0]
        
        for z in xrange(Z):
            print z, ', '.join(self.words_in_topic(z))
            
    
    def docs_in_topic(self, z, topD=None):
        """
        Returns a list of the topD documents most representative of topic z.
        
        Parameters
        ----------
        z : int
            A topic index.
        topD : int or float
            Number of prominent topics to return (int), or threshold (float).
            
        Returns
        -------
        documents : list
            List of (document, proportion) tuples.
        """    
        td = self.theta[:, z]
        
        if topD is None:
            topD = td.shape[0]
        
        if type(topD) is int:   # Return a set number of documents.
            top_indices = np.argsort(td)[topD]
        elif type(topD) is float:   # Return documents above a threshold.
            top_indices = [ d for d in np.argsort(td) if td[d] > topD ]
        
        top_values = [ td[d] for d in top_indices ]
        top_idents = [ self.metadata[d] for d in top_indices ]
        
        documents = zip(top_idents, top_values)
        
        return documents



def from_mallet(top_doc, word_top, metadata=None, metadata_key='doi'):
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
    metadata : string (optional)
        Path to tab-separated metadata file with IDs and :class:`.Paper` keys.

    Returns
    -------
    ldamodel : :class:`.LDAModel`

    """

    theta = _handle_top_doc(top_doc)
    phi = _handle_word_top(word_top)

    if metadata is not None:
        md = _handle_metadata(metadata)
    else:
        md = None

    return LDAModel(theta, phi, md)

def _handle_top_doc(path):
    """
    
    
    Returns
    -------
    td : Numpy array
        Rows are documents, columns are topics. Rows sum to ~1.
    """
    from scipy.sparse import coo_matrix

    D = []
    T = []
    P = []

    with open(path, "rb") as f:
        i = -1
        reader = csv.reader(f, delimiter='\t')
        for line in reader:
            i += 1
            if i == 0: continue     # Avoid header row.
            
            d = int(line[0])
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

    return coo_matrix((P, (D,T)), shape=(M,K)).todense()
    
def _handle_word_top(path):
    """
    Returns
    -------
    wt : Numpy array
        Rows are topics, columns are words. Rows sum to ~1.
    vocabulary : :class:`.Dictionary`
        Maps words to word-indices in wt.
    """
    from scipy.sparse import coo_matrix
    
    words = {}
    topics = set()

    W = []
    T = []
    C = []
    
    with open(path, "rb") as f:
        reader = csv.reader(f, delimiter=' ')
        for line in reader: # TODO: figure out why this is so complicated.
            w = int(line[0])
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
    
    return phi

def _handle_metadata(path):
    """
    Returns
    -------
    md : dict
        Keys are document indices, values are identifiers from a :class:`.Paper`
        property.
    """
    md = {}

    with open(path, "rU") as f:
        reader = csv.reader(f, delimiter='\t')
        lines = [ l for l in reader ][1:]
        for l in lines:
            md[int(l[0])] = l[1]

    return md
