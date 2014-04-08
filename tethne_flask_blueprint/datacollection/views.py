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
    
     functions (methods) 
    ```````
    get_user_details()        - list the users
    del_user()                - delete an user.
    auth()                    - restrict admin view to normal user
    update_user_details()     - update user details
    
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
from flask import Flask, session, redirect, url_for, escape, request,render_template,flash
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
    
    storage = FileStorage('.datacollection/storage/userdb.fs')
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
    
    storage = FileStorage('./datacollection/storage/userdb.fs')
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
    storage = FileStorage('./datacollection/storage/userdb.fs')
    conn = DB(storage)
    #print "Get User Deatails:",conn, type(conn),
    dbroot = conn.open().root() 
    
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
    storage = FileStorage('./datacollection/storage/userdb.fs')
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

     
@dataset.route('/index', methods=['GET','POST'])
def index():
    if 'username' in session:
        print " comes here in index", session, type(session) 
        return 'Logged in as %s' % escape(session['username'])
    #return render_template('forms/register.html', form = form)
    return 'You are not logged in'            
    
@dataset.route('/ok', methods=['GET','POST'])
def ok():
    #form = LoginForm(request.form)
    #return redirect(url_for('.login'))
    return render_template('pages/placeholder.home.html')
 
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
        results =get_user_details()
    return render_template('pages/admin.home.html', columns=columns,results=results)


@dataset.route('/user', methods=['GET','POST'])
def user():
    """
    User View
    """
    print " session can be accessed here as well", session, session['username']
    return render_template('pages/user.home.html', user = session['username'])

# View for displaying user details     
@dataset.route('/user_data')
def get_user_data():
        """
        The view where actually get_user_details gets called and 
        the details are returned to the web page.
        
        """
        columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
        results =get_user_details()
        return results
               

               
@dataset.route('/place', methods=['GET','POST'])
def place():
    """
    A placeholder view.
    """ 
    
    print "Are u coming here or not?" 
    return render_template('pages/placeholder.home.html')

@dataset.route('/', methods=['GET','POST'])
def home():
    """
    A dummy view for login routing.
    
    """
    return redirect(url_for('.login'))

# TRY WITH GET. the perfect method
test1 = 100
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
    #print "comes out", request.form , "uname", username , "pass", password, type(password)
    
    if 1:
          #new
          name = username
          session['username'] = username
          userpassword = password 
          #new
          print "Session",session, session['username']
          # Need to make it call only once. set_defaults function should work.
          #storage = FileStorage('./storage/userdb.fs')
          storage = FileStorage('./datacollection/storage/userdb.fs')
          conn = DB(storage)
          print "4.Login start:",conn, type(conn),
          dbroot = conn.open().root()
          if not 'userdb' in dbroot.keys():
            print " donot create this always"
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
    #print "##form OBJECT::: register---->", form, request.form,
    if request.method == 'POST':
        storage = FileStorage('./datacollection/storage/userdb.fs')
        conn = DB(storage)
        print "Type start:",conn, type(conn)
        dbroot = conn.open().root()
        # to check if the DB is already initialized
        # this part is commented as it is moved up 
        if not 'userdb' in dbroot.keys():
            print " donot create this always"
            dbroot['userdb'] = Dict()
            
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


@dataset.route('/create_datasets/', methods = ['GET','POST'])
def create_datasets():
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
        storage = FileStorage('./datacollection/storage/userdb.fs')
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


@dataset.route('/create_slices/', methods = ['GET','POST'])
def create_slices():
    """
    Create datasets slices
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    if request.method == 'POST'  :
        try:
            input_type = request.form['filetype']
            input_path = request.form['fileinput']
        
        except:
            print "comes to except"
            pass
        print " comes out here"
        print "comes out create data", request.form, request.form['filetype'],request.form['fileinput']
        
        #status = os.system("python ../tethne -I example_data -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F WOS | tee datasets_log.txt")
        status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P  /Users/ramki/tethne/testsuite/testin/2_testrecords.txt -F " + input_type + "| tee datasets_log.txt")
        #status = os.system("python ../tethne -I " + session['username'] + " -O ./ --read-file  -P " + input_path + " -F " + input_type + "| tee datasets_log.txt")
        print "try", status
        print os.getcwd()
        # Check if the command succeeded.
        if status is 0:
            log = "Dataset created successfully."
        else:
            log = "There seems to be some error while creating datasets."
        
        # Read the log file line by line and display it in the webpage.
        cmd  = 'cat datasets_log.txt'
        cmd2 = os.popen(cmd,'r',1)
        log=""
        for file in cmd2.readlines():
            log +=file
            if file in "pickle":
                print "inside",file

        #Initialize the DB
        
        storage = FileStorage('./datacollection/storage/userdb.fs')
        conn = DB(storage)
        print "3.Login start:",conn, type(conn),
        dbroot = conn.open().root()
        if not dbroot.has_key('dsdb'):
            dbroot['dsdb'] = Dict()

        #db() # call to check dsdb is initialized - this is not working

        # Add it to the DB
        dataobj=mod.DataCollection(session['username'],"samplepickleobject",datetime.datetime.now().strftime("%Y-%m-%d %H:%M"))
        print "DS:--->", dataobj
        dbroot['dsdb'][dataobj.user_id] = dataobj
        transaction.commit()
        print "Database added successfully", dbroot['dsdb'][dataobj.user_id].date

        return render_template('pages/generate.datasets.slices.html', user = user, text= log)

    return render_template('pages/generate.datasets.slices.html', user = user, form= form)




@dataset.route('/logout')
def logout():
    """
    When the User logs out, the session is ended and  
    user is redirected to login page.
    """
    session.pop('logged_in', None)
    flash('You are logged out')
    return redirect(url_for('.login'))

# # Error handlers.
# @dataset.errorhandler(500)
# def internal_error(error):
#     #db_session.rollback()
#     return render_template('errors/500.html'), 500
# 
# @dataset.errorhandler(404)
# def internal_error(error):
#     return render_template('errors/404.html'), 404

# if not dataset.debug:
#     file_handler = FileHandler('error.log')
#     file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
#     '[in %(pathname)s:%(lineno)d]'))
#     app.logger.setLevel(logging.INFO)
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
#     app.logger.info('errors')


@dataset.errorhandler(404)
def page_not_found(error):
    return 'This page does not exist', 404


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
