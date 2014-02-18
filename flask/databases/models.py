from flask import current_app as app
from flask.ext.zodb import Object, List, Dict
from hashlib import sha256


from BTrees.OOBTree import OOBTree as BTree
from persistent import Persistent as Object
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict

class User(Object):
    
    """
    Users Class
    DocString to be added
    """
    
    def __init__(self):
        pass
    
    def register(self,user, email, password,emailid,que,ans):
        self.email = email
        self.passwordHash = sha256(password).hexdigest()
        self.id = email
        self.secretque = que
        self.secretque = answerpass
    
    def login_user(self,UserObject):
        pass
    
    def login_error(self):
        pass
        
        
class GraphCollection(Object):
    
    """
    GraphCollections Class
    DocString to be added
    """
    
    def __init__(self):
        pass
    
    
    def register(self,userObject):
        self.email = email
        self.passwordHash = sha256(password).hexdigest()
        self.id = email
        self.secretque = que
        self.secretque = answerpass
    
    def login_user(self,UserObject):
        pass
    
    def login_error(self):
        pass
    
        
        
class DataCollection(Object):
    
    """
    Users Class
    DocString to be added
    """
    
    def __init__(self):
        pass
    
    def list_datasets(self):
        # List the existing data sets
        pass 
        
    def create_wosdatasets(self):
        pass
   
    def create_dfrdatasets(self):
        pass
     
    def update_wosdatasets(self):
        # Call Users Class here
        pass
    def update_dfrdatasets(self):
        # Call Users Class here
        pass
       
    def view_datasets(self):
        # Call users class here
        pass    
    
    
class Networks(object):
  """
    Users Class
    DocString to be added
  """
    
    def __init__(self):
        pass
    
    def list_datasets(self):
        # List the existing data sets
        pass 
        
    def create_wosdatasets(self):
        pass
    
        
                       

        
        
        