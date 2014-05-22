"""
Classes for the User Management, persistence of tethne :class:`.GraphCollection` and 
:class:`.DataCollection` objects in ZODB. 


.. autosummary::

   User
   PersistentDataCollection
   PersistentGraphCollection
   Event
   
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
import time

class User(Persistent):
    """
    Class for handling user data. 
    The following fields (and corresponding data types) are required:
    
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
        Class for handling user data.
        Initialize the :class:`.User` object with registration details.
        
        Parameters
        ----------
        name : str
            Username of the user.
        password : str 
            Password of the user, stored after encryption.
        emailid : str     
            Email-id of the user.
        institution : str
            Institution to which the user belongs to.
        que : str     
            Secret Question for password recovery
        ans : str
            Answer for the secret question.
            
        Returns
        -------
        An :class:`.User` Object with "name" as the key. 
        It gets stored in the User data Binarytree. 

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
        self.role = 1    #all users who register will be "Normal Users"
        self._p_changed = 1 #for mutable objects

    def __repr__(self):
        return '<User %r>' % (self.name)

       
class PersistentGraphCollection(Persistent):
    
    """
    Persistent Class for accessing tethne's :class:`.GraphCollection` 
    and persist the :class:`.GraphCollection` object here.

    The following fields (and corresponding data types) are required:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    
    name            str     Name provided by the user for the collection.
    owner           str     User who created this collection.
    date            str     The date of GraphCollection creation.
    graph_obj       Obj     class:`.GraphCollection` object 
    datacoll_obj    Obj     class:`.DataCollection` object used to create this
                            class:`.GraphCollection` object.
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """
    
    def __init__(self,name,owner,graph_obj,datacoll_obj):

        """
        Persistent Class for accessing tethne's :class:`.GraphCollection` 
        and persist the :class:`.GraphCollection` object here.
        
        Parameters
        ----------
        name : str 
            Name provided by the user for the collection.    
        owner : str     
            User who created this collection. Got from the session variables.
        graph_obj : Obj     
            class:`.GraphCollection` object 
        datacoll_obj : Obj     
            class:`.DataCollection` object used to create this
            class:`.GraphCollection` object.
        
        Fields: (auto-generated)
        -------

        g_id : str     
            GraphCollection ID. Generated using the hash of GraphCollection 
            "name" provided by user. Unique name for each collection. 
        date : str     
            The date of GraphCollection creation. It is auto-generated.

        Returns
        -------
        A class:`.PersistentGraphCollection` Object with "g_id" 
        as the key gets stored in the PersistentGraphCollection data tree. 

        Raises
        ------
        None.
        
        """
        
        self.g_id = sha256(name)          #<sha256 HASH object @ 00002BA7AF0>         
        self.name = name
        self.owner = owner
        self.date = time.strftime("%c") #ex:'04/29/14 14:09:29'
        self.graph_obj = graph_obj
        self.dataobj = datacoll_obj; 
        
        
class PersistentDataCollection(Persistent):
    
    """
    Class for accessing :class:`.DataCollection` 
    from tethne and persist the :class:`.DataCollection` object in this class.

    The following fields (and corresponding data types) are allowed:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    name            str     Name provided by the user for the collection.
    owner           str     User who created this collection.
    date            str     The date of DataCollection creation.
    datacoll_obj    str     class:`.DataCollection` object 
    ===========     =====   ====================================================

    None values are not allowed for these fields.
    """
    
    def __init__(self,d_id, name, owner,date,datacoll_obj):

        """
        Persistent Class for accessing tethne's :class:`.DataCollection` 
        and persist the :class:`.DataCollection` object here.
        
        Parameters
        ----------
        owner : str     
            User who created this collection. Got from the session variables.
        
        datacoll_obj : Obj     
            class:`.DataCollection` object 

        Fields: (auto-generated)
        -------    
        d_id : str     
            DataCollection ID. Generated using the hash of DataCollection 
            "name" provided by user. Unique name for each collection. 
        date : str     
            The date of DataCollection creation. It is auto-generated.

        Returns
        -------
        A class:`.PersistentDataCollection` Object with "d_id" 
        as the key gets stored in the PersistentDataCollection data tree. 

        Raises
        ------
        None.
        
        """
        
        self.d_id = sha256(name) 
        self.name = name
        self.owner = owner
        self.date = time.strftime("%c") #ex:'04/29/14 14:09:29'
        self.dataobj = datacoll_obj; 
        self._p_changed = 1 # for mutable objects
  

class Event(Persistent):
    
    """
    Class for the users to track the events in the application.
    The following fields (and corresponding data types) are required:
    
    ===========     =====   ====================================================
    Field           Type    Description
    ===========     =====   ====================================================
    user_id         str     Logged in user who wants the Events details.
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
        Class for the users to track the events in the application.
        
        Parameters
        ----------
        user_id : str     
            Logged in user who wants the view Event details.
        datetime : str
            The date-time used for viewing events details. 
            i.e Activity since Apr 20, 2014.
        obj : obj     
            Either class:`.GraphCollection` object or 
            class:`.DataCollection` object which was 
            modified/created during the datetime period.
        action : str     
            The list of activity during that datetime period. 
        
        Returns
        -------
        An class:`.Event` Object with the activity details 
        
        Raises
        ------
        None.
        
        """

        self.id = user_id
        self.datetime = datetime
        self.obj = obj # The last object which got accessed / created
        self.activity = action
        self._p_changed = 1 # for mutable objects
