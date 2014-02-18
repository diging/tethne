from flask import current_app as app
from flask.ext.zodb import Object, List, Dict
from hashlib import sha256

from BTrees.OOBTree import OOBTree as BTree
from persistent import Persistent as Object
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict

class User(Object):
    
    """
    User Class
    DocString to be added
    """
    
    def __init__(self):
        pass
    
    def register(self,user, email, password,emailid,que,ans):
        self.email = email
        self.passwordHash = sha256(password).hexdigest()
        self.id = email
        self.secretque = que
        self.secretans = answerpass
    
    def login(self,UserObject):
        pass
   
    def list_users(self):
        pass
    
    def edit_users(self,UserObject):
        pass
    
    def del_users(self):
        pass
   
        
        
class GraphCollection(Object):
    
    """
    GraphCollection Class
    DocString to be added
    """
    
    def __init__(self):
        pass
    
    
    def list_collections(self):
        # List the existing Graph Collections
        pass 
    
    def create_collections(self,DataObjectsdict):
        # List the existing Graph Collections
        pass 
    
    def analyze_collections(self,DataObject,method):
        # Method : Betweenness centrality
        # Call users class here
        pass
    
        
        
class DataCollection(Object):
    
    """
    DataCollection Class
    DocString to be added
    """

    
    def __init__(self):
        pass
    
    def list_datasets(self):
        # Call Users class here and show the existing data sets collection
        # List the existing data sets
        pass 
        
    def create_datasets(self,input_type, network_category, network_type):
        # Wos and Dfr type
        pass
    
    def update_datasets(self,DatasetObject):
        # Call Users Class here
        # Editing the existing data collection here
        pass
            
class SaveNetworks(object):
    """
    SaveNetworks Class
    DocString to be added
    """
    
    def __init__(self,type):
        pass                       

    
        
        
        