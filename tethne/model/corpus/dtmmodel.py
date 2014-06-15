from ..basemodel import BaseModel
import numpy as np
import os
import re
import csv

class DTMModel(BaseModel):

    def __init__(self, e_theta, topics, metadata, vocabulary):
        self.e_theta = e_theta
        self.topics = topics
        self.metadata = metadata
        self.vocabulary = vocabulary

        self.lookup = { v:k for k,v in metadata.iteritems() }

    def _item_description(self, i, **kwargs):
        """
        Proportion of each topic in document.
        """
        
        return [ (k, self.e_theta[k, i]) 
                    for k in xrange(self.e_theta[:, i].size) ]
        
    def _dimension_description(self, k, t=0, **kwargs):
        """
        Yields probability distribution over terms.
        """

        return [ (w, self.topics[k, w, t]) 
                    for w in xrange(self.topics[k, :, t].size) ]
        
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
        print self.metadata

        description = [ (self.metadata[i], self.e_theta[k,i]) 
                            for i in xrange(self.e_theta[k,:].size)
                            if self.e_theta[k,i] >= threshold ]
        return description    
        
    def topics_in_doc(self, d, topZ=None):
        """
        Deprecated; use :func:`BaseModel.item`\.
        """

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

    def words_in_topic(self, z, t, topW=5):
        """
        Deprecated; use :func:`BaseModel.dimension`\.
        """    
        if type(topW) is int:
            words = self.topics[z, :, t].argsort()[-topW:][::-1]

        return [ ( w, self.topics[z, w, t]) for w in words ]

    def print_topic(self, z, t):
        words = [ self.vocabulary[w] for w,p
                    in self.words_in_topic(z,t,topW=topw) ]
        print ', '.join(words)
        return words


class GerrishLoader(object):
    """
    Helper class for parsing results from S. Gerrish's C++ DTM implementation.
    
    http://code.google.com/p/princeton-statistical-learning/downloads/detail?name=dtm_release-0.8.tgz
    """

    def __init__(self, target, metadata_path, vocabulary_path, metadata_key='doi',):
        self.target = target
        self.metadata_path = metadata_path
        self.vocabulary_path = vocabulary_path
        self.metadata_key = metadata_key
    
        self.handler = { 'prob': self._handle_prob,
                         'info': self._handle_info,
                         'obs': self._handle_obs     }
    
    def load(self):
        try:
            contents = os.listdir(self.target)
            lda_seq_dir = os.listdir('{0}/lda-seq'.format(self.target))
        except OSError:
            raise OSError("Invalid target path.")
        
        # Metadata.
        self._handle_metadata()
        self._handle_vocabulary()
        
        # Meta-parameters.
        self._handle_metaparams()
        
        # Topic proportions.
        self._handle_gammas()
        
        # p(w|z)
        self.tdict = {}
        for fname in lda_seq_dir:
            fs = re.split('-|\.', fname)

            if fs[0] == 'topic':
                z_s = fs[1]
                z = int(z_s)

                self.handler[fs[-2]](fname, z)

        self.topics = np.array( [ self.tdict[z] for z in sorted(self.tdict.keys()) ])
    
        self.model = DTMModel(self.e_theta, self.topics, self.metadata, '')

        return self.model

    def _handle_metaparams(self):
        # Read metaparameters.
        with open('{0}/lda-seq/info.dat'.format(self.target), 'rb') as f:
            for line in f.readlines():
                ls = line.split()
                if ls[0] == 'NUM_TOPICS':
                    self.N_z = int(ls[1])

                elif ls[0] == 'NUM_TERMS':
                    self.N_w = int(ls[1])

                elif ls[0] == 'SEQ_LENGTH':
                    self.N_t = int(ls[1])

                elif ls[0] == 'ALPHA':
                    self.A = np.array(ls[2:])

    def _handle_gammas(self):
        # Read gammas -> e_theta
        with open('{0}/lda-seq/gam.dat'.format(self.target), 'rb') as f:
            data = np.array(f.read().split())
            self.N_d = data.shape[0]/self.N_z
            b = data.reshape((self.N_d, self.N_z)).astype('float32')
            rs = np.sum(b, axis=1)
            self.e_theta = np.array([ b[:,z]/rs for z in xrange(self.N_z) ])

    def _handle_prob(self, fname, z):
        """
        - topic-???-var-e-log-prob.dat: the e-betas (word distributions) for
        topic ??? for all times.  This is in row-major form,
       """
        with open('{0}/lda-seq/{1}'.format(self.target, fname), 'rb') as f:
            data = np.array(f.read().split()).reshape((self.N_w, self.N_t))
            self.tdict[z] = np.exp(data.astype('float32'))

    def _handle_info(self, fname, z):
        """
        No need to do anything with these yet.
        """
        pass

    def _handle_obs(self, fname, z):
        """
        TODO: Figure out what, if anything, this is good for.
        """
        pass

    def _handle_metadata(self):
        """
        Returns
        -------
        md : dict
            Keys are document indices, values are identifiers from a :class:`.Paper`
            property.
        """
        
        if self.metadata_path is None:
            self.metadata = None
            return
        
        self.metadata = {}

        with open(self.metadata_path, "rU") as f:
            reader = csv.reader(f, delimiter='\t')
            lines = [ l for l in reader ][1:]
            i = 0
            for l in lines:
                self.metadata[i] = l[0]
                i += 1

        return self.metadata

    def _handle_vocabulary(self):
        if self.vocabulary_path is None:
            raise RuntimeError("No vocabulary provided.")

        # Build vocabulary
        self.vocabulary = {}
        with open(self.vocabulary_path, 'rU') as f:
            i = 0
            for v in f.readlines():
                self.vocabulary[i] = v
                i += 1
                
        return self.vocabulary

def from_gerrish(target, metadata, vocabulary, metadata_key='doi'):
    """
    Parse results from S. Gerrish's C++ DTM implementation.
    
    http://code.google.com/p/princeton-statistical-learning/downloads/detail?name=dtm_release-0.8.tgz
    """

    e_log_prob = 'topic-{0}-var-e-log-prob.dat'
    info = 'topic-{0}-info.dat'
    obs = 'topic-{0}-obs.dat'

    reader = GerrishLoader(target, metadata, vocabulary)#, metadata, vocabulary)
    return reader.load()