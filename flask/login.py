#from flask import * # do not use '*'; actually input the dependencies.
from flask import Flask, session, redirect, url_for, escape, request,render_template,flash
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import LoginForm,RegisterForm,ForgotForm
import ZODB.config
import transaction
from hashlib import sha256
from persistent import Persistent
from persistent.list import PersistentList as List
from persistent.mapping import PersistentMapping as Dict
from flask_login import current_user,login_user,LoginManager,logout_user , \
                     current_user , login_required
from flask import abort
import json

app = Flask(__name__)
app.config.from_object('config')
app.debug = True

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import models as mod


@app.before_first_request
def set_db_defaults():
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    print "3.Login start:",conn, type(conn),
    dbroot = conn.open().root()

def get_user_details():
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
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    #print "Get User Deatails:",conn, type(conn),
    dbroot = conn.open().root() 
    
def update_user_details():
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    #print "Get User Deatails:",conn, type(conn),
    dbroot = conn.open().root() 
    

       #  try:
#             collection = [dict(zip(columns, each_list))]
#         except UnboundLocalError,KeyError:
#             collection = [dict(zip(columns, each_list))]
    #results = mod.BaseDataTables(request, columns, collection).output_result()
    print results
    return results 
    #return json.dumps(results)   
    
          

    

# @app.before_request
# def set_db_defaults():
# 	storage = FileStorage('./storage/users.fs')
# 	db = DB(storage)
# 	print "Type start:",db, type(db)
# 	connection = db.open()
# 	# dbroot is a dict like structure.
# 	dbroot = connection.root()  # retrieving the root of the tree
# 	for val in ['userdb']:
# 		if not val in dbroot.keys():
# 			print " donot create this always"
# 			dbroot[val] = Dict()
# 			print "user db dbroot:",dbroot['userdb'], type (dbroot['userdb'])

# Commented part
# ZEO commented as of now.

# db = ZODB.config.databaseFromURL('zodb.conf')
# connection = db.open()
# root = connection.root()

              


# if not dbroot.has_key('userdb'):
#     from BTrees.OOBTree import OOBTree
#     #dbroot['userdb'] = OOBTree()
#     print " donot create this always"
#     dbroot['userdb'] = Dict()
#     # userdb is a <BTrees.OOBTree.OOBTree object at some location>
#     # userdb is a dbroot: {} <class 'persistent.mapping.PersistentMapping'>

#userdb = dbroot['userdb']           
#print "user db init:",userdb, type(userdb)
#Ensure that a 'userdb' key is present
#in the DB
###

login_manager = LoginManager() #class
login_manager.init_app(app) #create a LoginManager Object from our 'app' object
login_manager.login_view = 'login' #set the view



@app.route('/auth', methods=['GET','POST'])
def auth():
    if current_user.is_authenticated():
         return render_template("forms/main.html",form=form)
    else:
         return render_template("forms/login.html")
            
@app.route('/index', methods=['GET','POST'])
def index():
    if 'username' in session:
        print " comes here in index", session, type(session) 
        return 'Logged in as %s' % escape(session['username'])
    #return render_template('forms/register.html', form = form)
    return 'You are not logged in'            
    
@app.route('/ok', methods=['GET','POST'])
def ok():
    #form = LoginForm(request.form)
    #return redirect(url_for('login'))
    return render_template('pages/placeholder.home.html')
               
@app.route('/admin', methods=['GET','POST'])
def admin():
    if request.method == 'GET'  : #and name != None
        # columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
		# return render_template('pages/admin.home.html', columns=columns)
		# print " Its coming out"
    	columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
    	results =get_user_details()
   	    #results = json.dumps(user_details)
   	    #print "results:", results
    return render_template('pages/admin.home.html', columns=columns,results=results)
    return 'Hello World!'
    
@app.route('/user_data')
def get_user_data():
    
        print "comes here"
        #columns = [ 'S.No chANGED', 'User Name', 'Institution', 'Email ID', 'Status', 'Active']
    
        #collection = [dict(zip(columns, [1,'Ramki',2,3,4,6])), dict(zip(columns, [2,'user889',5,5,33,7]))]
        
        #print "collection" , collection
        
        #results = BaseDataTables(request, columns, collection).output_result()
        
        #return the results as a string for the datatable
        #print "results:", results
        print " session can be accessed here as well", session, session['username']
        columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
        user_details =get_user_details()
        results = json.dumps(user_details)
            #results  = [ {"S.No" : "1"},{"User Name" : "Admin"} , {"Institution" : "ASU"} ,
    #		 {"Email ID" : "admin@asu.edu"} ]
        return results
               
@app.route('/user', methods=['GET','POST'])
def user():
    print " session can be accessed here as well", session, session['username']
    return render_template('pages/user.home.html')
               
@app.route('/place', methods=['GET','POST'])
def place():
	print "Are u coming here or not?" 
	return render_template('pages/placeholder.home.html')

@app.route('/', methods=['GET','POST'])
def home():
    #form = LoginForm(request.form)
    #return render_template('forms/login.html', form = form)
    #flask.redirect(flask.url_for('login'))
    
    return redirect(url_for('login'))

# Loader callback. Reload the user-id from the value stored in the session.
@login_manager.user_loader
def load_user(userid):
    #here use the ZODB user class and returns the user object
    pass



# USing Login Manager
# @app.route('/login/', methods=['GET', 'POST'])
# def login():
#     print "Request Method", request.method, request.form
#     
#     if request.method == 'GET':
#         form = LoginForm(request.form)
#         #if 'Login' not in request.form.values:
#         if request.form["action"] == "Login":
#                     print "inside if"
#                     
#         else:
#             print "inside else"
#             print "request.form.values", reques.form.values
#             uname = request.form.get('name', None)
#             print "UNAME:::", uname
#             user = mod.User.get_user('admin')
#             if user and hash_password(request.form['password']) == user._password:
#                 login_user(user, remember=True)
#                 return redirect('/home/')
#             else:
#                 print "401"
#                 return abort(401)  # 401 Unauthorized
#     else:
#             print "Why here"
#             flash("No use get")
#             return abort(405)  # 405 Method Not Allowed
#         
#     return render_template('forms/login.html',form=form)


# Other Try
# @app.route('/login', methods=['GET','POST'])
# def login():
#     if request.method == 'GET':
#         form = LoginForm(request.form)
#         return render_template('forms/login.html',form=form)
#         username = request.form['name']
#         password = request.form['password']
#         print "Username and password :", username,password
#         #registered_user = somehow check if the user is 
#         if registered_user is None:
#             flash('Username or Password is invalid' , 'error')
#             return redirect(url_for('login'))
#         login_user(registered_user)
#         flash('Logged in successfully')
#         return redirect(request.args.get('next') or url_for('index'))
#     
#  
# Working method - my manual option
# Issue : Password is shown in the request, and form data is not retrieved.
#@app.route('/login/', methods=['GET','POST'])
#@app.route('/login/', methods=['POST'])
# def login():
#     #flash('Welcome to Tethne Website')
# #     form = LoginForm(request.form)
# #     name = request.args.get('name')
# #     userpassword = request.args.get('password')
# #     print "arguments",name,userpassword 
# #     print "Login Form Values", request.cookies.get('username'), "abc:"
#     #username = request.cookies.get('username')
#     if request.method == 'GET'  : #and name != None
#         form = LoginForm(request.form)
#         if not form.validate():
#         #if 1:
#             print "##form OBJECT::: Login--->", form, request.form
#             name = request.args.get('name')
#             userpassword = request.args.get('password')
#             print "1 : URL arguments",name,userpassword 
#             uname = form.name
#             pswd = form.password
#             print "\n 2. FORM arguments: Login form:#####", uname, pswd, type(uname), type(pswd)
#             print "#####Login Form Values", request.cookies.get('username'), "abc:"
#             storage = FileStorage('./storage/userdb.fs')
#             conn = DB(storage)
#             print "3.Login start:",conn, type(conn),form.name.data
#             dbroot = conn.open().root()
#             try: 
#             	print "dbroot['userdb'].values()", dbroot['userdb'].values(), "keys",dbroot['userdb'].keys() , dbroot['userdb']
#                 #for val in dbroot['userdb'].values():
#         		#		print "value is : " , val, val.name,val.email,"form", form
#                 
#                 # This gives error.  as the ImmutableDict request.form is empty
#                 #uname = request.form['name']
#                 #pswd = request.form['password']
#                 #print " 4.The arguments [ '' method]: Login form:", uname, pswd
#                 print " 4.Login form data:", form.name.data, form.name.description,form.name.label
#                 for key in dbroot['userdb'].keys():
#         					#print "Yess!!", key, session['username'] 
#                             #if  session['username'] == key :
#                     if name == 'admin' :
#                             # Need to get username from the form  password = sha256(password
#                             print "COOOL it works atlast", "password1",dbroot['userdb'][key].password,"password2", sha256(request.args.get('password'))
#                             print "inside login last loop:",dbroot, type(dbroot)
#                             return render_template('pages/admin.home.html')
#                     if name == key and name !='admin':
#                             print "he is a normal user"
#                             return render_template('pages/user.home.html')
#                     else :
#                             print "Error : No Such User"
#                             pass
#                               
#             except:
#                 #flash('Username or password failed')
#             	print " donot come here : except"
#                 pass           
#                	
#     else:
#             print "comes in else"
#             flash("Login Failed") #return redirect(url_for('login'))
#             return redirect(url_for('ok'))
#            
#     return render_template('forms/login.html', form = form)


# TRY WITH GET. the perfect method
@app.route('/login/', methods=['GET','POST'])
def login():
    if request.method == 'GET'  : #and name != None
        #form = LoginForm(request.form)
        return render_template('forms/login_new.html')
        print " Its coming out"
    try:
        username = request.form['username']
        password = request.form['password']
    except:
        print "comes to except"
        pass
    print "comes out", request.form , "uname", username , "pass", password, type(password)
    #if form.validate():
    if 1:
          #new
          name = username
          session['username'] = username
          userpassword = password 
          #new
          print "Session",session, session['username']
          storage = FileStorage('./storage/userdb.fs')
          conn = DB(storage)
          print "3.Login start:",conn, type(conn),
          dbroot = conn.open().root()
          try: 
              print "####values()", dbroot['userdb'].values(), "#####keys",dbroot['userdb'].keys(), type(dbroot['userdb'])
              if name in dbroot['userdb'].keys():
                  for key in dbroot['userdb'].keys():
                      print "\nkey is" , key 
                      print "\ndbroot['userdb'][key]", dbroot['userdb'][key]
                      if key == 'admin' and name == 'admin':
                                  # Need to get username from the form  password = sha256(password
                                  dbpswd = dbroot['userdb'][key].password
                                  loginpswd = sha256(userpassword).hexdigest()
                                  if dbpswd == loginpswd:                                 
                                      print "COOOL it works atlast", "password1",dbroot['userdb'][key].password,"password2", sha256(userpassword).hexdigest()
                                      print "inside login last loop:",
                                      #return render_template('pages/admin.home.html')
                                      return redirect(url_for('admin'))
                                  else:
                                      flash("Login Failed : Please check the Username / password") 
                                      return redirect(url_for('login'))
                                 
                                  
                      if key != 'admin' and name != 'admin':
                                 if name == key:
                                  # Need to get username from the form  password = sha256(password
                                  dbpswd = dbroot['userdb'][key].password
                                  loginpswd = sha256(userpassword).hexdigest()
                                  if dbpswd == loginpswd:                                 
                                      print "COOOL it works atlast", "password1",dbroot['userdb'][key].password,"password2", sha256(userpassword).hexdigest()
                                      print "inside login last loop:",
                                      print "he is a normal user"
                                      #return render_template('pages/user.home.html')
                                      return redirect(url_for('user'))
                                  else:
                                      flash("Login Failed : Please check the Username / password") 
                                      return redirect(url_for('login'))
                                
                      else:
                          print "No such user"
                          pass
              else:       
                      #render_template('pages/user.error.html')
                  flash("User, Please register First") 
                  return redirect(url_for('login'))       
          except:
              print " donot come here : except"
              pass           
                     

    return redirect(url_for('login'))
            
#return render_template('forms/login.html', form = form)


def generate_user_list(template_name, **kwargs):
    user_count = get_user_count()
    return render_template(template_name, uc = usercount, var2=var2, var3=var3, **kwargs)
    
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    print "##form OBJECT::: register---->", form, request.form,
    if request.method == 'POST':
            #session['username'] = request.form['username']
#                 if 'Register' in request.form:
#                     print "inside if"
#                 else:
#                 	print "inside else"
    	storage = FileStorage('./storage/userdb.fs')
    	conn = DB(storage)
    	print "Type start:",conn, type(conn)
    	dbroot = conn.open().root()
        try:
            for val in ['userdb','graphdb','datadb']:
        		if val in dbroot.keys():
					pass
        except:
        		if not val in dbroot.keys():
					print " donot create this always"
					dbroot[val] = Dict()
					print "TRY user db dbroot:",dbroot['userdb'], type (dbroot['userdb'])
					
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
        print "Database added successfully", dbroot['userdb'][u.name], u.name, u
        flash('Registered successfuly')
    	return redirect(url_for('login'))
    return render_template('forms/register.html', form = form)

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)    

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))

# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('errors/404.html'), 404

if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
    '[in %(pathname)s:%(lineno)d]'))
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')








# Default port:
if __name__ == '__main__':
    #app.before_first_request()
    app.run()
    

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
