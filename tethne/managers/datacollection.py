from tethne.classes import DataCollection
import tethne.readers as rd

class DCBuilder(object):
    """
    Base class for DataCollection builders.
    """
    
    def __init__(self, datapath):
        """
        
        Parameters
        ----------
        datapath : str
            Path to data.
        """

        self.datapath = datapath
        
class DFRBuilder(DCBuilder):
    """
    DataCollection builder for JSTOR Data-for-Research datasets.
    """
    
    def build(self, grams=['uni'], slice_by=['date',], **kwargs):
        """
        
        Parameters
        ----------
        grams : list or tuple
            N-grams that should be read from the DfR dataset.
        apply_stoplist : bool
            If True, will exclude all N-grams that contain words in the NLTK
            stoplist.
        slice_by : list or tuple
            Keys in :class:`.Paper` by which to slice data.
        """
            
        # Load papers.
        papers = rd.dfr.read(self.datapath)

        # Load N-grams.
        gram_data = {}
        for gram_type in grams:
            g = rd.dfr.ngrams(self.datapath, N=gram_type)
            g_tok, vocab, counts = rd.dfr.tokenize(g)                                        

            gram_data[gram_type] = (g_tok, vocab, counts)
        
        # Create DataCollection.
        D = DataCollection(papers, grams=gram_data, index_by='doi')
        
        # Slice DataCollection.
        kw = { 'method': kwargs.get('method', 'time_window'),
               'window_size': kwargs.get('window_size', 4),
               'step_size': kwargs.get('step_size', 1) }

        for axis in slice_by:
            D.slice(axis, **kw)
        
        return D