from flask import current_app as app
from flask.ext.zodb import Object, List, Dict
from hashlib import sha256

from BTrees.OOBTree import OOBTree as BTree
#from persistent import Persistent as Object
from persistent import Persistent
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import ZODB.config
import transaction
from hashlib import sha256




class User(Persistent):
        
    """
    User Class
    DocString to be added
    
    """

    def __init__(self,name, email, password,emailid,institution,que,ans):
        self.name = name
        self.email = email
        self.password = password
        self.id = emailid
        self.institution = institution
        self.secretque = que 
        self.secretans = ans    
        self.role = "user"
        self._p_changed = 1 # for mutable objects

    def get_user(self,name,password):
        initialize_userdb()
        print "In get_user"
        pass
    
    def is_authenticated(self):
        pass
    
    def is_anonymous(self):
        pass
    
    def initialize_userdb(self):
        """
        User DB is initialized
        """
        storage = FileStorage('./storage/userdb.fs')
        conn = DB(storage)
        dbroot = conn.open().root()
        print ("DB initialized")
        
    def is_active(self):
        return True
  
    def get_id(self):
        return unicode(self.id)
 
    def __repr__(self):
        return '<User %r>' % (self.name)

class ManageUsers(User):
	
	"""
	User Class
    DocString to be added
    
	"""
	def login(self,name):
		#pass the User Object and retrieve the user details
		self.name = name
		self._p_changed = 1
    	
   
    # def list_users(self):
#         # only for admin - whose role is "0"
#         pass
#     
#     def approve_user(self,UserObject):
#         # only for admin
#         pass
#     
#     def del_user(self,UserObject):
#         # only for admin
#         pass
#    
#         
        
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

    def __init__(self,user_id,dataset_obj,date):
        self.user_id = user_id
        self.dataset_obj = dataset_obj
        self.date = date
        self._p_changed = 1 # for mutable objects

    def list_datasets(self):
        # Call Users class here and show the existing data sets collection
        # List the existing data sets
        pass 
        
    def create_datasets(self,input_type, input_path, input_id):
        
        # Wos and Dfr type
        self.input_type = input_type # WOS or JSTOR
        self.input_path = input_path # The Path got from the user
        self.input_id = input_id # presently considering this as userID

    def update_datasets(self,user_id,dataset_obj,date):
        # Call Users Class here
        # Editing the existing data collection here
        self.user_id = user_id
        self.dataset_obj = dataset_obj
        self.date = date
        
        pass
            
class SaveNetworks(object):
    """
    SaveNetworks Class
    DocString to be added
    """
    
    def __init__(self,type):
        pass        
                   
