import warnings

class CollectionManager(object):
    """
    Base class for collection managers.

    """
    def __init__(self, **kwargs):
        """
        Base constructor. If reimplemented in a subclass, should be called via
        super().
        """
        if 'prep' not in type(self).__dict__:
            warnings.warn('Manager has no prep() method.', DeprecationWarning)
        if 'build' not in type(self).__dict__:
            warnings.warn('Manager has no build() method.', DeprecationWarning)
        if 'write' not in type(self).__dict__:
            warnings.warn('Manager has no write() method.', DeprecationWarning)

    def run(self, **kwargs):
        """
        Execute CollectionManager workflow (prep, build, run).
        
        Optional kwargs can provide workflow-specific parameters.
        """
        if 'prep' in type(self).__dict__: self.prep(**kwargs)
        if 'build' in type(self).__dict__: self.build(**kwargs)
        if 'write' in type(self).__dict__: self.write(**kwargs)
