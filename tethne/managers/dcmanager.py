from collectionmanager import CollectionManager

from ..classes import DataCollection

class DataCollectionManager(CollectionManager):
    """
    Base class for DataCollection managers.
    """

    def __init__(self, datapath, **kwargs):
        """
        
        Parameters
        ----------
        datapath : str
            Path to data.
        """
        super(DataCollectionManager, self).__init__(**kwargs)

        self.datapath = datapath
        
class SampleDFRManager(DataCollectionManager):
    """
    Sample :class:`.DataCollectionManager` for JSTOR Data-for-Research datasets.
    """
    
    slice_axis='date'
    slice_method = 'time_window'
    window_size = 4
    step_size = 1
    
    slice_axis2 = 'jtitle'
    
    gram_type = 'uni'

    def prep(self):
        from ..readers import dfr
        self.papers = dfr.read(self.datapath)
        self.features = { 'unigrams':dfr.ngrams(self.datapath, self.gram_type) }

    def build(self):
        from nltk.corpus import stopwords
        exclude = set(stopwords.words())
        self.D = DataCollection(self.papers, self.features, index_by='doi',
                                                       exclude_features=exclude)
        self.D.slice(self.slice_axis, method=self.slice_method,
                     window_size=self.window_size, step_size=self.step_size)
        self.D.slice(self.slice_axis2)


    def write(self, target='./distribution.png'):
        import matplotlib.pyplot as plt
        fig = plt.figure(figsize=(25,10))
        self.D.plot_distribution(self.slice_axis2, self.slice_axis, fig=fig,
                                                           interpolation='none')
        plt.savefig(target)
