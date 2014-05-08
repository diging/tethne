"""
    This script contains various controller methods which controls the flow
    between the models and views.

    views 
    ```````
    1. /CreatePersistentDataCollection       
    
    
    
"""

# Import Statements   
from flask import Flask, session, redirect, url_for, escape,\
                    request,render_template,flash
from flask_wtf import Form
from forms import LoginForm,RegisterForm,ForgotForm,GenerateDataSetsForm,ListDataSetsForm
from flask import abort,Blueprint
import datetime,logging
from logging import Formatter, FileHandler
from hashlib import sha256
import time
 



import random as random
import models as db
import views as view
import tethne.readers as rd


#ZODB import
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
#Importing the models module
import models as mod                    




def set_db_defaults():
    
    """
    This is to be called only once during the script.
    Setting the ZODB databases. 
    
    """
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    dbroot = conn.open().root()
    try:
        for val in ['userdb','graphdb','datadb','dsdb']:
            if val in dbroot.keys():
                pass
    except:
        if not val in dbroot.keys():
            print " donot create this always"
            dbroot[val] = Dict()
            print "TRY user db dbroot:",dbroot['dsdb'], type (dbroot['dsdb'])

def CreatePersistentDataCollection(input_file_format,input_file,input_datacollectionname):
    """
    This is the controller method called from CreateDataCollection View. 
    It gets the following data from user form/CreateDataCollection View.
    
    Input data:
    -----------

    1.Input file, 
    2.Input filetype, 
    3.Input DataCollection Name 

    Funtions:
    ---------

    a. Parse the data using the input file and input filetype
       and create a list of papers.
    b. Create a DataCollection from the list of papers. 
    c. Interact with the model and store the details in the 
       Persistent DataCollection object.
    d. Return true or false to the view. 

     
    """
        
    try:
        
        file_format = input_file_format         # got from the view. 
        username    = session['username']
        filename    = input_datacollectionname
        input_file  = input_file_with_path      # with full path

    except:
        print "comes to except"
        pass
        
        # Parse data.
        # Actually it should be the file taken from the server.
        # Currently this is a dummy one.
        
        #Create a DataCollection
        from tethne.data import DataCollection, GraphCollection
        from tethne.readers import wos
        import tethne.data as dc
        import tethne.readers as rd
        
        file_format = 'wos' #temporary hardcode
        
        #Temporary filename hardcode as the files should be ideally the ones
        # Which user gives as input and it should be taken from the server.
        papers = rd.wos.read("C:/Users/Ramki/Documents/2_testrecords.txt")
        
        #indexed_by value changes according to the input.
        if file_format == 'wos' :
            D = DataCollection(papers)
            print D
        else:
            #Handle for DFR collection using DOI. 
            pass

        #Create a PersistentDataCollection Object.
        dataCollUniqueID = sha256(input_datacollectionname).hexdigest()
        date = time.strftime("%c")
        # These are not "persisted" into ZODB as on yet (ZODB part is not written)
        status = mod.PersistentDataCollection(dataCollUniqueID,input_datacollectionname,username,date,D)
        #print "status", status
        #print status.name, status.date,status.dataobj

        #return render_template('pages/generate.datasets.html')
        return redirect(url_for('.dc_create'))


    return render_template('pages/generate.datasets.html', user = user)
