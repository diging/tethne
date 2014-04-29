"""
Classes for  accessing persistence of tethne data in ZODB and to perform
various operations on them.


.. autosummary::

   User
   PersistentDataCollection
   PersistentGraphCollection
   Events
   
"""


from flask import current_app as app
from flask.ext.zodb import Object, List, Dict
from BTrees.OOBTree import OOBTree as BTree
from persistent import Persistent
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import ZODB.config,transaction
from hashlib import sha256

# Import tethne classes
import tethne.data as data
import tethne.readers as rd
# from tethne.data import DataCollection 
# from tethne.data import GraphCollection 

#Errors:

#import tethne.networks as nt 
# >>> import models as m
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "models.py", line 15, in <module>
#     import tethne.networks as nt
#   File "E:\program_files\Anaconda\lib\site-packages\tethne\networks.py", line
# 1, in <module>
#     for paper in meta_list:
# NameError: name 'meta_list' is not defined


class User(Persistent):
    """
    Class for handling user data. 
    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    name            str     Username of the user.
    password        str     Password of the user, stored after encryption.
    emailid         str     email-id of the user.
    institution     str     Institution to which the user belongs to.
    que             str     Secret Question for password recovery
    ans             str     Answer for the secret question.
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """

    def __init__(self,name,password,emailid,institution,\
                                    que,ans): 
        """
        Initialize the User object with registration details.
        
        Parameters
        ----------
        name     : str
        password : str
        email-id : str
        institution: str
        que : str
        ans : str

        Returns
        -------
        None. 
            An User Object with "name" as the key gets stored in the 
            User data tree. 

        Raises
        ------
            None.
        
        """

    
        self.name = name
        self.password = sha256(password)
        self.id = emailid
        self.institution = institution
        self.secretque = que 
        self.secretans = ans    
        self.role = 1 #all users who register will be "Normal Users"
        self._p_changed = 1 #for mutable objects

    def __repr__(self):
        return '<User %r>' % (self.name)

       
class PersistentGraphCollection(Persistent):
    
    """
    Class for accessing :class:`.GraphCollection` 
    from tethne and persist the :class:`.GraphCollection` object in this class.

    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    g_id            str     GraphCollection ID. Unique name for each collection.
    name            str     Name provided by the user for the collection.
    owner           str     User who created this collection.
    date            str     The date of GraphCollection creation.
    graph_obj       Obj     class:`.GraphCollection` object 
    data_obj       Obj     class:`.DataCollection` object used to create this
                            class:`.GraphCollection` object.
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """
    
    def __init__(self,g_id,name,owner,date,graph_obj,data_obj):

        """
        Initialize the PersistentGraphCollection object.
        
        Parameters
        ----------
        g_id : str
        name : str
        owner: str
        date : str
        graph_obj: class:`.GraphCollection` object 
        

        Returns
        -------
        None. 
            A PersistentGraphCollection Object with "g_id" 
            as the key gets stored in the PersistentGraphCollection data tree. 

        Raises
        ------
            None.
        
        """
        
        self.id = g_id
        self.name = name
        self.owner = owner
        self.date = date
        self.graph_obj = graph_obj
        pass
    
        
class PersistentDataCollection(Persistent):
    
    """
    Class for accessing :class:`.DataCollection` 
    from tethne and persist the :class:`.DataCollection` object in this class.

    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    d_id            str     DataCollection ID. Unique name for each collection.
    name            str     Name provided by the user for the collection.
    owner           str     User who created this collection.
    date            str     The date of DataCollection creation.
    dataset_obj     str     class:`.DataCollection` object 
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """
    
    def __init__(self,d_id, name, owner,date,dataset_obj):

        """
        Initialize the PersistentDataCollection object.
        
        Parameters
        ----------
        d_id : str
        name : str
        owner: str
        date : str
        dataset_obj: class:`.DataCollection` object 
        

        Returns
        -------
        None. 
            A PersistentDataCollection Object with "d_id" 
            as the key gets stored in the PersistentDataCollection data tree.

        Raises
        ------
            None.
        
        """
        
        self.id = data_id
        self.name = name
        self.owner = owner
        self.date = date
        self.dataobj = dataset_obj; 
        self._p_changed = 1 # for mutable objects
  

class Events(Persistent):
    
    """
    Class for the admin to track the events in the application.
    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    user_id         str     Activity corresponding to the user.
    datetime        str     The date-time used for viewing events details.
    obj             obj     Either class:`.GraphCollection` object or 
                            class:`.DataCollection` object which was 
                            accessed/modified/created during the datetime period.
    action          str     The list of activity during that datetime period.                        
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """
    
    def __init__(self,user_id,datetime,obj,action):

        """
        Initialize the PersistentDataCollection object.
        
        Parameters
        ----------
        user_id : str
        datetime : str
        obj:  class:`.DataCollection` object or class:`.GraphCollection` object
        action : str
        
        Returns
        -------
        An Events Object with the activity details for the datetime window, for
        the respective user.

        Raises
        ------
            None.
        
        """

        self.id = user_id
        self.datetime = datetime
        self.obj = obj # The last object which got accessed / created
        self.activity = action
        self._p_changed = 1 # for mutable objects
