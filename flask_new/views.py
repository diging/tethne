"""
    This script contains various views of DataCollections 
    for User Login, creating DataCollection
    and viewing the datasets details.
    
    views 
    ```````
    /login        - Login check
    /register     - register a new user.
    /admin        - admin view
    /user         - user view
    /forgot
    /logout
    /create_datasets
    /list_datasets
    /view_dataset_details
    /del_datasets
    /add_datasets
    /create_slices
    
    
    .. autosummary::
    
    login
    register
    admin
    user
    forgot
    logout
    create_datasets
    list_datasets
    view_dataset_details
    del_datasets
    add_datasets
    create_slices
    
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

#ZODB import
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
#Importing the database models module
import models as mod         
# Importing helpers module
import helpers as help           

# Initializing the Blueprint. 
# Instead of @app the module will have @dataset

dataset = Blueprint('views',__name__,template_folder='templates')

"""
Test Views
"""
# test view
@dataset.route('/info')
def info():
	return "I am inside Show_info"
	
# To catch the URLs which are not defined 
@dataset.route('/', defaults={'path': ''})
@dataset.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s, This one is a wrong path! Please check!' % path
    
@dataset.route('/ok', methods=['GET','POST'])
def ok():
    return render_template('pages/placeholder.home.html')

               
@dataset.route('/place', methods=['GET','POST'])
def place():
    """
    A placeholder view.
    """ 
    
    print "Are u coming here or not?" 
    return render_template('pages/placeholder.home.html')


"""
Login Views
"""
     
@dataset.route('/index', methods=['GET','POST'])
def index():
    
    if 'username' in session:
        print " comes here in index", session, type(session) 
        return 'Logged in as %s' % escape(session['username'])
        return redirect(url_for('.login'))
    return 'You are not logged in'        


@dataset.route('/', methods=['GET','POST'])
def home():
    """
    A dummy view for login routing.
    
    """
    return redirect(url_for('.login'))

@dataset.route('/login/', methods=['GET','POST'])
def login():
    """
    Login check for a user. 
    
    If its successful user would be redirected to either 
    "user" view or "admin" view.
    
    If the user is not registered then an error message is displayed and 
    redirected to Login/register page.
    
    """
    
    if request.method == 'GET'  :
        print "comes inside login"
        return render_template('forms/login_new.html')
        #print " Its coming out"
    try:
        username = request.form['username']
        password = request.form['password']
    except:
        print "comes to except"
        pass
  
    
    if 1:
          name = username
          session['username'] = username
          userpassword = password 
          #new
          #print "Session",session, session['username']
          # Need to make it call only once. set_defaults function should work.
          storage = FileStorage('./storage/userdb.fs')
          conn = DB(storage)
          #print "4.Login start:",conn, type(conn),
          dbroot = conn.open().root()
          if not 'userdb' in dbroot.keys():
            #print " donot create this always"
            dbroot[userdb] = Dict()
          try: 
              print "####values()", dbroot['userdb'].values(), "#####keys",dbroot['userdb'].keys(), type(dbroot['userdb'])
              if name in dbroot['userdb'].keys():
                  for key in dbroot['userdb'].keys(): #Traverse through keys
                      if key == 'admin' and name == 'admin':  #if the user is admin
                                  # Checking the Stored User password with the form password
                                  dbpswd = dbroot['userdb'][key].password
                                  loginpswd = sha256(userpassword).hexdigest()
                                  if dbpswd == loginpswd:                                 
                                      return redirect(url_for('.admin'))
                                  else:
                                      flash("Login Failed : Please provide the correct Username / password") 
                                      return redirect(url_for('.login'))
                                 
                                  
                      if key != 'admin' and name != 'admin':
                                 if name == key:
                                  # Need to get username from the form  password = sha256(password
                                  dbpswd = dbroot['userdb'][key].password
                                  loginpswd = sha256(userpassword).hexdigest()
                                  if dbpswd == loginpswd:          
                                      print "comes here:::before break" , username, session['username']                       
                                      return redirect(url_for('.user'))
                                  else:
                                      flash("Login Failed : Please provide the correct Username / password") 
                                      return redirect(url_for('.login'))
                                
                      else:
                          print "No such user"
                          pass
              else:       
                    
                  flash("User, Please register First !!") 
                  return redirect(url_for('.login'))       
          except:
              print " donot come here : except"
              pass           
 
    return redirect(url_for('.login'))
            
    
@dataset.route('/register',methods=['GET','POST'])
def register():
    """
    register a new user.
    """
    form = RegisterForm(request.form)
   
    if request.method == 'POST':
        storage = FileStorage('./storage/userdb.fs')
        conn = DB(storage)
        print "Type start:",conn, type(conn)
        dbroot = conn.open().root()
        # to check if the DB is already initialized
        # this part is commented as it is moved up 
        if not 'userdb' in dbroot.keys():
            print " donot create this always"
            dbroot['userdb'] = Dict()
        print "gdbroot", dbroot    
        print "else:::::-->", request.form , form.email.data
        u=mod.User(form.name.data,form.email.data,\
                    sha256(form.password.data).hexdigest(), \
                    form.password.data,form.institution.data,\
                    form.security_question.data, form.security_answer.data        
                   )
        print "User:--->", u, "form.name.data",form.name.data
        dbroot['userdb'][u.name] = u
        session['username'] = u.name
        transaction.commit()
        #print "Database added successfully", dbroot['userdb'][u.name], u.name, u
        flash('Registered successfuly')
        return redirect(url_for('.login'))
    return render_template('forms/register.html', form = form)



@dataset.route('/forgot',methods=['GET','POST'])
def forgot():
    """
    This is when  user forgets his username / password
    This module is a TO- DO.
    
    """
    
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)    



@dataset.route('/logout')
def logout():
    """
    When the User logs out, the session is ended and  
    user is redirected to login page.
    """
    session.pop('logged_in', None)
    flash('You are logged out')
    return redirect(url_for('.login'))

"""
Admin and User Views

"""

#Admin view              
@dataset.route('/admin', methods=['GET','POST'])
def admin():
    """
    Admin view.
    """
    # Handling if normal users try accessing this view.
    if session['username'] != 'admin':
        flash ("Only Admins can view this page!!")
        return redirect(url_for('.user'))    
    
    if request.method == 'GET'  : 
        columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
        results =help.get_user_details()
    return render_template('pages/admin.home.html', columns=columns,results=results)


#@dataset.route('/<username>/home', methods=['GET','POST'])
@dataset.route('/user/home', methods=['GET','POST'])
def user():
    """
    User View
    """
    if request.method == 'GET'  :
        return render_template('pages/user.home.html', user = session['username'])
    return redirect(url_for('.dc_list'),username= session['username']) 


"""
DataCollection Views
"""

@dataset.route('/datacollection/list', methods=['GET','POST'])
def dc_list():
    """
    List Data Collection 
    Show the user the existing collection of datacollection.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C', 'S.No', 'DataCollection ID', 'Created Date' ]
        checkboxes = ['','','']
        results =  [['1', 'Data#1156734', '20140408132211'], ['2', 'Data#2356734', '20140308092211'], ['3', 'Data#4456734', '20140408112221']]   
        return render_template('pages/list.datasets.html', user = session['username'])
    
@dataset.route('/datacollection/create/', methods = ['GET','POST'])
def dc_create():
    """
    Create Data Collection
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    #if request.method == 'POST' and user == 'admin' :
    if request.method == 'POST' :
        try:
            input_type = request.form['filetype']
            input_path = request.form['fileinput']
           
        except:
            print "comes to except"
            pass
        print " comes out here"
        print "comes out create data", request.form, request.form['filetype'],request.form['fileinput']
        # Parse data.
        import tethne.readers as rd
        papers = rd.wos.read("/Users/ramki/tethne/testsuite/testin/2_testrecords.txt")
        # Create a DataCollection, and slice it.    
        from tethne.data import DataCollection, GraphCollection
        D = DataCollection(papers)
        print "Object", D
        slice = D.slice('date', 'time_window', window_size=4)   
        print "Object", slice 
        #status = os.system("python ../tethne -I example_data -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F WOS | tee datasets_log.txt")
        #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F " + input_type + "| tee datasets_log.txt")
        #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P " + input_path + " -F " + input_type + "| tee datasets_log.txt")
        #print "try", status
#         print os.getcwd()
#         # Check if the command succeeded.
#         if status is 0:
#            log = "Dataset created successfully."
#         else:
#            log = "There seems to be some error while creating datasets."
# 
#         # Read the log file line by line and display it in the webpage.
#         cmd  = 'cat datasets_log.txt'
#         cmd2 = os.popen(cmd,'r',1)
#         log=""
#         for file in cmd2.readlines():     
#              log +=file
#              if file in "pickle":
#                 print "inside",file
# 
        #Initialize the DB
        storage = FileStorage('./storage/userdb.fs')
        conn = DB(storage)
        dbroot = conn.open().root()
        if not dbroot.has_key('dsdb'):
            dbroot['dsdb'] = Dict()
          
        # Add it to the DB
        dataobj=mod.DataCollection(session['username'],D,datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print "DS:--->", dataobj
        dbroot['dsdb'][dataobj.user_id] = dataobj
        transaction.commit()
        #As of now keeping datasets coupled with users. Need to change it.
        log = "Dataset" +str (D) +"created successfully and added in the database at " +  str(dbroot['dsdb'][dataobj.user_id].date)   
        return render_template('pages/generate.datasets.html', user = user, text= log)
    
    return render_template('pages/generate.datasets.html', user = user, form= form)
    #return render_template('pages/user.home.html', user = user, form= form)


@dataset.route('/datacollection/create_slices/', methods = ['GET','POST'])
def dc_create_slices():
    """
    Create datasets slices
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    if request.method == 'POST'  :
#         try:
#             input_type = request.form['filetype']
#             input_path = request.form['fileinput']
#         
#         except:
#             print "comes to except"
#             pass
#         print " comes out here"
#         print "comes out create data", request.form, request.form['filetype'],request.form['fileinput']
#         
#         #status = os.system("python ../tethne -I example_data -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F WOS | tee datasets_log.txt")
#         status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F " + input_type + "| tee datasets_log.txt")
#         #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P " + input_path + " -F " + input_type + "| tee datasets_log.txt")
#         print "try", status
#         print os.getcwd()
#         # Check if the command succeeded.
#         if status is 0:
#             log = "Dataset created successfully."
#         else:
#             log = "There seems to be some error while creating datasets."
#         
#         # Read the log file line by line and display it in the webpage.
#         cmd  = 'cat datasets_log.txt'
#         cmd2 = os.popen(cmd,'r',1)
#         log=""
#         for file in cmd2.readlines():
#             log +=file
#             if file in "pickle":
#                 print "inside",file
# 
#         #Initialize the DB
#         
#         storage = FileStorage('./storage/userdb.fs')
#         conn = DB(storage)
#         print "3.Login start:",conn, type(conn),
#         dbroot = conn.open().root()
#         if not dbroot.has_key('dsdb'):
#             dbroot['dsdb'] = Dict()
# 
#         #db() # call to check dsdb is initialized - this is not working
# 
#         # Add it to the DB
#         dataobj=mod.DataCollection(session['username'],"samplepickleobject",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
#         print "DS:--->", dataobj
#         dbroot['dsdb'][dataobj.user_id] = dataobj
#         transaction.commit()
        log = "Silces created and added  in DB successfully"

        return render_template('pages/generate.datasets.slices.html', user = user, text= log)

    return render_template('pages/generate.datasets.slices.html', user = user, form= form)


@dataset.route('/datacollection/view', methods=['GET','POST'])
def dc_stats():
    """
    List the stats for a selected Data Collection 
    
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C','S No', 'Paper ID', 'No. of nodes', 'No. of edges' ]
        checkboxes = ['','','','']
        results =  [['', '1', 'paper#113', '34', '250'], ['2', 'paper#1234',  '43', '250'], ['3', 'paper#4734',  '134', '2510']]   
        return render_template('pages/view.datasets.html', user = session['username'])
    
"""
Graph Collection Views
"""


@dataset.route('/graphcollection/list', methods=['GET','POST'])
def gc_list():
    """
    List Graph Collection 
    Show the user the existing collection of datacollection.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C', 'S.No', 'GraphCollection ID', 'Created Date' ]
        checkboxes = ['','','']
        results =  [['1', 'gc#1156734', '20140408132211'], ['2', 'gc#2356734', '20140308092211'], ['3', 'gc#4456734', '20140408112221']]   
        return render_template('pages/list.graphcollection.html', user = session['username'])
    

@dataset.route('/graphcollection/create', methods = ['GET','POST'])
def gc_create():
    """
    Create Graph Collection Collection
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    #if request.method == 'POST' and user == 'admin' :
    if request.method == 'POST' :
#         try:
#             input_type = request.form['filetype']
#             input_path = request.form['fileinput']
#            
#         except:
#             print "comes to except"
#             pass
#         print " comes out here"
#         print "comes out create data", request.form, request.form['filetype'],request.form['fileinput']
#         # Parse data.
#         import tethne.readers as rd
#         papers = rd.wos.read("/Users/ramki/tethne/testsuite/testin/2_testrecords.txt")
#         # Create a DataCollection, and slice it.    
#         from tethne.data import DataCollection, GraphCollection
#         D = DataCollection(papers)
#         print "Object", D
#         slice = D.slice('date', 'time_window', window_size=4)   
#         print "Object", slice 
        #status = os.system("python ../tethne -I example_data -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F WOS | tee datasets_log.txt")
        #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F " + input_type + "| tee datasets_log.txt")
        #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P " + input_path + " -F " + input_type + "| tee datasets_log.txt")
        #print "try", status
#         print os.getcwd()
#         # Check if the command succeeded.
#         if status is 0:
#            log = "Dataset created successfully."
#         else:
#            log = "There seems to be some error while creating datasets."
# 
#         # Read the log file line by line and display it in the webpage.
#         cmd  = 'cat datasets_log.txt'
#         cmd2 = os.popen(cmd,'r',1)
#         log=""
#         for file in cmd2.readlines():     
#              log +=file
#              if file in "pickle":
#                 print "inside",file
# 
        #Initialize the DB
#         storage = FileStorage('./storage/userdb.fs')
#         conn = DB(storage)
#         dbroot = conn.open().root()
#         if not dbroot.has_key('dsdb'):
#             dbroot['dsdb'] = Dict()
#           
#         # Add it to the DB
#         dataobj=mod.DataCollection(session['username'],D,datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
#         print "DS:--->", dataobj
#         dbroot['dsdb'][dataobj.user_id] = dataobj
#         transaction.commit()
        D = "Gc#11124"
        #As of now keeping datasets coupled with users. Need to change it.
        log = "GraphCollection" +str (D) +"created successfully and added in the database at " +  "201404061223412 "  
        return render_template('pages/generate.graphsets.html', user = user, text= log)
    
    return render_template('pages/generate.graphsets.html', user = user, form= form)
    #return render_template('pages/user.home.html', user = user, form= form)


@dataset.route('/graphcollection/view', methods=['GET','POST'])
def gc_stats():
    """
    List the stats for a selected GraphCollection 
    
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C','S No', 'Paper ID', 'No. of nodes', 'No. of edges' ]
        checkboxes = ['','','','']
        results =  [['', '1', 'paper#113', '34', '250'], ['2', 'paper#1234',  '43', '250'], ['3', 'paper#4734',  '134', '2510']]   
        return render_template('pages/view.graphcollection.html', user = session['username'])

@dataset.route('/graphcollection/analyze', methods=['GET','POST'])
def gc_analyze():
    """
    Analyze the  selected GraphCollection (ex: between centrality)
    
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C','S No', 'Paper ID', 'No. of nodes', 'No. of edges' ]
        checkboxes = ['','','','']
        results =  [['', '1', 'paper#113', '34', '250'], ['2', 'paper#1234',  '43', '250'], ['3', 'paper#4734',  '134', '2510']]   
        return render_template('pages/analyze.graphcollection.html', user = session['username'])




"""
Visualize Networks View
"""


@dataset.route('/visualize', methods=['GET','POST'])
def viz():
    """
    Visualize Graph Collection using D3.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        return render_template('pages/viz.graphcollection.html', user = session['username'])

@dataset.route('/visualize/#23412334', methods=['GET','POST'])
def dc_viztest():
    """
    Visualize Graph Collection using D3.
    #23412334 -This is a to-do, this has to be replaced with the
    original graphCollection ID.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        return render_template('pages/viz.network.html', user = session['username'])


    
"""
Not used

"""

# # Default port:
# if __name__ == '__main__':
#     app.run()
#     before_first_request()
#     

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
