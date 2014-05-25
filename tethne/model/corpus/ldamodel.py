from ..basemodel import BaseModel
import numpy as np

class LDAModel(BaseModel):
    """
    Organizes parsed output from MALLET's LDA modeling algorithm.
    
    Used by :mod:`.readers.mallet`\.
    """

    def __init__(self, doc_topic, top_word, top_keys, metadata, vocabulary):
        """
        Initialize the :class:`.LDAModel`\.
        
        Parameters
        ----------
        doc_top : Numpy matrix
            Rows are documents, columns are topics. Values indicate the 
            contribution of a topic to a document, such that all rows sum to 
            1.0.
        top_word : Numpy matrix
            Rows are topics, columns are words. Values indicate the normalized
            contribution of each word to a topic, such that rows sum to 1.0.
        top_keys : dict
            Maps matrix indices for topics onto the top words in that topic.
        metadata : dict
            Maps matrix indices for documents onto a :class:`.Paper` key.
        """
        
        self.doc_topic = doc_topic
        self.top_word = top_word
        self.top_keys = top_keys
        self.metadata = metadata
        self.vocabulary = vocabulary
        
        self.lookup = { v:k for k,v in metadata.iteritems() }
    
    # Obligatory methods.
    def _item_description(self, i, **kwargs):
        """
        Yields proportion of each topic in document.
        """
        this_prop = self.doc_topic[i, :]
        return [ (t, this_prop[t]) for t in xrange(this_prop.size) ]
    
    def _item_relationship(self, i, j, **kwargs):
        """
        Yields the relationship between two documents.
        """
        # TODO: implement cosine-similarity or another similarity metric here.

        return None
    
    def _dimension_description(self, d, **kwargs):
        """
        Yields probability distribution over terms.
        """
        this_theta = self.top_word[z, :]
        return [ (w, this_theta[w]) for w in xrange(this_theta.size) ]
    
    def _dimension_relationship(self, d, e, **kwargs):
        """
        Simply returns (d,e); there is no additional information about 
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
#        td = self.doc_topic[index, :]
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
#            words = self.top_word[z,:].argsort()[-topW:][::-1]
#
#        return [ ( w, self.top_word[z,w]) for w in words ]

    def print_topic(self, z):
        words = [ self.vocabulary.by_int[w] for w,p
                    in self.words_in_topic(z, topW=topW) ]
        print ', '.join(words)
        return words

    def print_topics(self):
        """
        Prints a list of topics.
        """
        Z = self.top_word.shape[0]
        
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
        td = self.doc_topic[:, z]
        
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