"""
    This script contains helper functions.    
        
     functions (methods) 
    ```````
    get_user_details()        - list the users
    del_user()                - delete an user.
    auth()                    - restrict admin view to normal user
    update_user_details()     - update user details
        
"""

# Import Statements   
from flask import Flask, session, redirect, url_for, escape,\
                    request,render_template,flash
from flask_wtf import Form
from forms import LoginForm,RegisterForm,ForgotForm,GenerateDataSetsForm
import ZODB.config
import transaction
from hashlib import sha256 # for password
from persistent import Persistent
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict
from flask_login import current_user,login_user,LoginManager,logout_user , \
                    current_user , login_required
from flask import abort,Blueprint
import json
import subprocess,os
import datetime
import logging
from logging import Formatter, FileHandler


# Initializing the Blueprint. 
# Instead of @app the whole module will have @dataset.
dataset = Blueprint('views',__name__,template_folder='templates')

@dataset.route('/info')
def info():
	print "I am inside Data Sets Show_info"
	
#ZODB import
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
#Importing the database models module
import models as mod                    



def set_db_defaults():
     
    """
    This is to be called only once during the script.
    Setting the ZODB databases. 
     
    """
    
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    print "3.Login start:",conn, type(conn),
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
             
    
def get_user_details():
    
    """
    Getting user details to display in the web page.
    This is only for admin view.
    
    Returns
    -------
    A list  - "results" in the form of 
    SNo      UserName     Institution
    
    """
    
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    #print "Get User Deatails:",conn, type(conn),
    dbroot = conn.open().root() 
    columns = [ 'S.No', 'User Name', 'Institution', 'Email ID'] 
    results = []
    abc = [('1',dbroot['userdb'][key].name,dbroot['userdb'][key].id, dbroot['userdb'][key].institution) for key in dbroot['userdb'].keys()]
    #remove unicode characters
    new_list =[','.join(list(each_item)) for each_item in abc]
    unicode_removed_list = [n.encode('ascii','ignore') for n in new_list]
    for val1 in unicode_removed_list:
        each_list = val1.split(',') 
        results.append(each_list)
    return results
     

def del_user_details():
    
    """
    Deleting the user details when the admin calls this method.
    This is only for admin view.
    
    Returns
    -------
    Status : If the user removal is a success/failure. 
    
    """
#    storage = FileStorage('./storage/userdb.fs')
#    conn = DB(storage)
#    #print "Get User Deatails:",conn, type(conn),
#    dbroot = conn.open().root()



def del_dc():
    
    """
        Deleting the selected Dataset and update the DB and redirect back to
        View DataCollections page.
        
        Returns
        -------
        
        
    """
    flash("Dataset deleted successfully")
    return redirect(url_for('.dc_list'))


def update_user_details():
   
    """
    Convert aulast, auinit, and jtitle into the fuzzy identifier ayjid
    Returns 'Unknown paper' if all id components are missing (None).

    Parameters
    ----------
    None
    
    Returns
    -------
    ayj : string
        Fuzzy identifier ayjid, or 'Unknown paper' if all id components are
        missing (None).
    """
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    #print "Get User Deatails:",conn, type(conn),
    dbroot = conn.open().root() 
    return results 
    #return json.dumps(results)   



@dataset.route('/auth', methods=['GET','POST'])
def auth():
    print "comes in auth"
    #print session
    if session is None:
        flash ( "Please Login First!!!!!")
        return redirect(url_for(".login"))
    if session['username'] is None:
         flash ( "Please Login First!!")
         return redirect(url_for(".login"))
    if session['username'] != 'admin':
        flash ("Only Admins can view this page!!")
        return redirect(url_for('.user'))
    else:
    	return 0
 