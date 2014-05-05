"""
Classes for the persistence of tethne data in ZODB and to perform
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
    aulast          list    Authors' last name, as a list.
    auinit          list    Authors' first initial as a list.
    institution     dict    Institutions with which the authors are affiliated.
    atitle          str     Article title.
    jtitle          str     Journal title or abbreviated title.
    volume          str     Journal volume number.
    issue           str     Journal issue number.
    spage           str     Starting page of article in journal.
    epage           str     Ending page of article in journal.
    date            int     Article date of publication.
    country         dict    Author-Country mapping.
    citations       list    A list of :class:`.Paper` instances.
    ayjid           str     First author's name (last fi), pubdate, and journal.
    doi             str     Digital Object Identifier.
    pmid            str     PubMed ID.
    wosid           str     Web of Science UT fieldtag value.
    accession       str     Identifier for data conversion accession.
    ===========     =====   ====================================================

    None values are also allowed for all fields.
    """

    def __init__(self,name,password,emailid=None,institution=None,\
                                    que=None,ans=None): 
        """
        Initialize the User with registration details.
        """   
        self.name = name
        self.password = password
        self.id = emailid
        self.institution = institution
        self.secretque = que 
        self.secretans = ans    
        self.role = 1 #all users who register will be "Normal Users"
        self._p_changed = 1 #for mutable objects

    def get_user_details(self,name):
        return 
    
    def is_authenticated(self,name,password):
       """

       To check if the user details are present in the DB
       Return a boolean true or false

       The input password is encrypted before checking it with the stored user

       """
       #Perform the check, return the boolean result.
       pass
    
    def is_anonymous(self,name):

        pass
    
    def initialize_userdb(self):
        """
        User DB is initialized
        """
        storage = FileStorage('./storage/userdb.fs')
        conn = DB(storage)
        dbroot = conn.open().root()
        print ("DB initialized")
        

    def __repr__(self):
        return '<User %r>' % (self.name)

    

       
class PersistentGraphCollection(Persistent):
    
    """
    PersistentGraphCollection Class.
    It is used to persist the Tethne GraphCollection objects
    This has the following methods.


    """
    
    def __init__(self,g_id,name,owner,date,graph_obj):
        
        self.id = g_id
        self.name = name
        self.owner = owner
        self.date = date
        self.graph_obj = graph_obj
        pass
    
    def ListRecentGraphcollections(self,owner,date):
        '''
        List the recent existing Graph Collections in the Home page
         
        parameters
        ``````````
        owner   - the userID 
        date    - the system date and to fetch only 
                  top 5 Collections less than the date.
        '''
        pass  

    def ListAllGraphcollections(self,owner):
        '''
        List all the existing Graph Collections in the 
        List Graph Collections page
         
        parameters
        ``````````
        owner   - the userID 
        date    - the system date and to fetch only 
                  top 5 Collections less than the date.

        return
        ```````
        A List of values for the tables in List Details view.
        '''
        pass     
    
    def DelGraphCollection(self,graph_obj,owner):
        '''
        Delete the existing GraphCollections in the Home page.
         
        parameters
        ``````````
        graph_obj = the GraphCollection to be deleted
        owner   - the userID 
        
        '''

        return     
        
    
    def AnalyseGraphCollection(self,graph_obj,owner):
        '''
        Analyze the existing GraphCollections in the Home page.
         
        parameters
        ``````````
        graph_obj = the GraphCollection to be analyzed
        owner   - the userID 
        
        '''

        return  
      
    
    def ListDetails(self,graph_obj):
        # provide the details of the selected dataset
        # On-the fly computation or DB storage of the 
        # No.of.slices, No of Papers is unsure.But keeping this class
        # as an option for the same.
        pass 
       

    def analyze_collections(self,graph_obj,method):
        # Method : Betweenness centrality
        pass
    
        
        
class PersistentDataCollection(Persistent):
    
    """
    PersistentDataCollection Class
    DocString to be added
    """

    def __init__(self,id, name, owner,date,dataset_obj):
        
        self.id = data_id
        self.name = name
        self.owner = owner
        self.date = date
        self.dataobj = dataset_obj; 
        self._p_changed = 1 # for mutable objects


    def ListDetails(self,dataset_obj):
        # provide the details of the selected dataset
        # On-the fly computation or DB storage of the 
        # No.of.slices, No of Papers is unsure.But keeping this class
        # as an option for the same.

        self.dataobj = dataset_obj
        print "dataset_obj" , self.dataobj
        pass 
    

    def ListRecentDatacollections(self,owner,date):
        '''
        List the recent existing Data Collections in the Home page
         
        parameters
        ``````````
        owner   - the userID 
        date    - the system date and to fetch only 
                  top 5 Collections less than the date.
        '''

        pass  

    def ListAllDatacollections(self,owner):
        '''
        List all the existing Data Collections in the 
        List DataCollections page
         
        parameters
        ``````````
        owner   - the userID 
        date    - the system date and to fetch only 
                  top 5 Collections less than the date.

        return
        ```````
        A List of values for the tables in ListDetails view.
        '''
        pass         

    def CreateDataCollection(self,input_type, input_path, owner):
        
        # Wos and Dfr type
        self.input_type = input_type # WOS or JSTOR
        self.input_path = input_path # The Path got from the user
        self.input_id = owner # presently considering this as userID
        self.dataset_obj = data.DataCollection()

    def UpdateDatasets(self,user_id,dataset_obj,date):
        # Call Users Class here
        # Editing the existing data collection here
        self.user_id = user_id
        self.dataset_obj = dataset_obj
        self.date = date
        
        pass
    
    def DelDataCollection(self,data_obj,owner):
        '''
        Delete the existing DataCollections in the Home page.
         
        parameters
        ``````````
        data_obj = the DataCollection to be deleted
        owner   - the userID 
        
        '''
        return     
            

class AdminActivities(Persistent):
    
    """
    Admin Class
    Admin can perform the following activities. 
    1. List all Users.
    2. Remove Users.
    3. List all the DataCollections or filtered by user(s)
    4. Monitor the recent activity in the system 
    (any DataCollection or GraphCollection) 
    
    """
    def __init__(self,user_id,date,obj,activity):

        self.id = user_id
        self.date = date
        self.dataset_obj = obj # The last object which got accessed / created
        self.activity = activity
        self._p_changed = 1 # for mutable objects
    
    def GetActivityDetails(self,startdate,enddate):
        """
        Admin provides the date and he will get the history of events happened in that period

        """

        pass