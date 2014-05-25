import logging
logging.basicConfig()
logger = logging.getLogger(__name__)
logger.setLevel('DEBUG')

class ModelCollection(object):
    """
    A collection of models.
    
    """

    models = {}
    metadata = {}
    
    item_index = {}
    dimension_index = {}

    def __init__(self):
        pass

    def __setitem__(self, index, model, metadata=None):
        """
        """

        self.models[index] = model
        self.metadata[index] = metadata

    def __getitem__(self, key):
        return self.models[key]

    def __delitem__(self, key):
        del self.models[key]

    def __len__(self):
        return len(self.models)        