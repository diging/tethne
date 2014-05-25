from ..basemodel import BaseModel
import numpy as np



class DTMModel(BaseModel):

    def __init__(self, e_theta, topics, metadata, vocabulary):
        self.e_theta = e_theta
        self.topics = topics
        self.metadata = metadata
        self.vocabulary = vocabulary

        self.lookup = { v:k for k,v in metadata.iteritems() }

    def topics_in_doc(self, d, topZ=None):
        if topZ is None:
            topZ = 5
            
        if type(topZ) is int:   # Return a set number of topics.
            top_indices = self.e_theta[:, d].argsort()[-topZ:][::1]
        elif type(topZ) is float:   # Return topics above a threshold.
            top_indices = [ z for z in np.argsort(self.e_theta[:, d])
                                if self.e_theta[z, d] > topZ ]

        top_values = [ self.e_theta[z, d] for z in top_indices ]
        
        topics = zip(top_indices, top_values)
        
        return topics

    def words_in_topic(self, z, t, topW=None):
        if topW is None:
            topW = 5

        if type(topW) is int:
            words = self.topics[z, :, t].argsort()[-topW:][::-1]

        return [ ( w, self.topics[z, w, t]) for w in words ]

    def print_topic(self, z, t):
        words = [ self.vocabulary.by_int[w] for w,p
                    in self.words_in_topic(z,t,topW=topw) ]
        print ', '.join(words)
        return words