import os
import re
import csv
import numpy as np
import sys

sys.path.append('/Users/erickpeirson/tethne')
from ..model.corpus.dtmmodel import DTMModel
from tethne.utilities import Dictionary

class DTMLoader(object):

    def __init__(self, target, metadata_path, vocabulary_path, metadata_key='doi',):
        self.target = target
        self.metadata_path = metadata_path
        self.vocabulary_path = vocabulary_path
        self.metadata_key = metadata_key
    
        self.handler = { 'prob': self._handle_prob,
                         'info': self._handle_info,
                         'obs': self._handle_obs     }
    
    def load(self):
        print self.target
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
        print self.model.print_topic(0, 0)

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
            for l in lines:
                self.metadata[l[0]] = l[1]

        return self.metadata

    def _handle_vocabulary(self):
        if self.vocabulary_path is None:
            raise RuntimeError("No vocabulary provided.")

        # Build vocabulary
        self.vocabulary = Dictionary()
        with open(self.vocabulary_path, 'rU') as f:
            i = 0
            for v in f.readlines():
                self.vocabulary[i] = v
                i += 1
                
        return self.vocabulary

def load(target, metadata, vocabulary, metadata_key='doi'):
    """
    Parse results from DTM modeling.
    
    """

    e_log_prob = 'topic-{0}-var-e-log-prob.dat'
    info = 'topic-{0}-info.dat'
    obs = 'topic-{0}-obs.dat'

    reader = DTMLoader(target, metadata, vocabulary)#, metadata, vocabulary)
    reader.load()

if __name__ == '__main__':
    import sys
    sys.path.append('/Users/erickpeirson/tethne')

#    opath = "/private/var/folders/f9/g7lw23jx7z3fw72byy3l11p80000gn/T/tmp88rYpV"
#
#    target = '/Users/erickpeirson/Downloads/dtm_release/dtm/example/model_run'
#
#    load(opath, vocabulary, metadata)
