class BaseModel(object):
    """
    Base class for models. Should not be instantiated directly.
    
    Use a model class in :mod:`tethne.model` instead.
    """
    
    def __init__(self, **kwargs):
        raise RuntimeError('BaseModel should not be instantiated directly.' + \
                           ' Use a model class in tethne.model instead.')

    def item(self, i, top=None, **kwargs):
        """
        Describes an item in terms of dimensions and weights.
        
        Subclass must provide _item_description(i) method.
        
        Parameters
        ----------
        i : int
            Index for an item.
        top : int
            (optional) Number of (highest-w) dimensions to return.
            
        Returns
        -------
        description : list
            A list of ( dimension , weight ) tuples.
        """
    
        try:
            description = self._item_description(i, **kwargs)
        except KeyError:
            raise KeyError('No such item index in this model.')
        except AttributeError:
            raise NotImplementedError('_item_description() not implemented' + \
                                      ' for this model class.')
        
        # Optionally, select only the top-weighted dimensions.
        if type(top) is int:
            D,W = zip(*description) # Dimensions and Weights.
            D = list(D)     # To support element deletion, below.
            W = list(W)            
            top_description = []
            while len(top_description) < top:   # Avoiding Numpy argsort.
                d = W.index(max(W)) # Index of top weight.
                top_description.append((D[d], W[d]))
                del D[d], W[d]

            description = top_description

        return description

    def item_relationship(self, i, j, **kwargs):
        """
        Describes the relationship between two items.
        
        Subclass must provide _item_relationship(i, j) method.
        
        Parameters
        ----------
        i : int
            Item index.
        j : int
            Item index.
        
        Returns
        -------
        relationship : list
            A list of ( dimension ,  weight ) tuples.
        """
        
        try:
            relationship = self._item_relationship(i, j, **kwargs)
        except AttributeError:
            raise NotImplementedError('_item_relationship() not implemented' + \
                                      ' for this model class.')

        return relationship

    def dimension(self, d, top=None, **kwargs):
        """
        Describes a dimension (e.g. a topic).
        
        Subclass must provide _dimension_description(d) method.
        
        Parameters
        ----------
        d : int
            Dimension index.
            
        Returns
        -------
        description : list
            A list of ( feature, weight ) tuples (e.g. word, prob ).
        """

        try:
            description = self._dimension_description(d, **kwargs)
        except AttributeError:
            raise NotImplementedError('_dimension_description() not' + \
                                      ' implemented for this model class.')

        # Optionally, select only the top-weighted dimensions.
        if type(top) is int:
            D,W = zip(*description) # Dimensions and Weights.
            D = list(D)     # To support element deletion, below.
            W = list(W)
            top_description = []
            while len(top_description) < top:   # Avoiding Numpy argsort.
                d = W.index(max(W)) # Index of top weight.
                top_description.append((D[d], W[d]))
                del D[d], W[d]

            description = top_description

        return description
        
    def dimension_items(self, d, threshold, **kwargs):
        """
        Describes a dimension in terms of the items that contain it.
        
        Parameters
        ----------
        d : int
            Dimension index.
        threshold : float
            Minimum representation of ``d`` in item.
            
        Returns
        -------
        description : list
            A list of ( item, weight ) tuples.
        """
        
        try:
            description = self._dimension_items(d, threshold, **kwargs)
        except AttributeError:
            raise NotImplementedError('_dimension_items() not' + \
                                      ' implemented for this model class.')
        return description

    def dimension_relationship(self, d, e, **kwargs):
        """
        Describes the relationship between two dimensions.
        
        Subclass must provide _dimension_relationship(d, e) method.
        
        Parameters
        ----------
        d : int
            Dimension index.
        e : int
            Dimension index.
        
        Returns
        -------
        relationship : list
            A list of ( factor ,  weight ) tuples.
        """
        
        try:
            relationship = self._dimension_relationship(d, e, **kwargs)
        except AttributeError:
            raise NotImplementedError('_dimension_relationship() not' + \
                                      ' implemented for this model class.')

        return relationship