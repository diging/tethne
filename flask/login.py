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
from flask_login import current_user,login_user,LoginManager

app = Flask(__name__)
app.config.from_object('config')

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import models as mod



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

login_manager = LoginManager()
login_manager.init_app(app)

@app.route('/auth', methods=['GET','POST'])
def auth():
    if current_user.is_authenticated():
         return render_template("forms/main.html",form=form)
    else:
         return render_template("forms/login.html")
            
@app.route('/index', methods=['GET','POST'])
def index():
    form = LoginForm(request.form)
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    #return render_template('forms/register.html', form = form)
    return 'You are not logged in'            
    
@app.route('/ok', methods=['GET','POST'])
def ok():
    form = LoginForm(request.form)
    #return redirect(url_for('login'))
    return render_template('forms/home.html', form = form)
               
@app.route('/place', methods=['GET','POST'])
def place():
	print "Are u coming here or not?" 
	return render_template('pages/placeholder.home.html')

@app.route('/', methods=['GET','POST'])
def home():
    #form = LoginForm(request.form)
    #return render_template('forms/login.html', form = form)
    return redirect(url_for('login'))


@login_manager.user_loader
def load_user(userid):
    return User.get(userid)
 


@app.route('/login', methods=['GET','POST'])
def login():
    flash('Welcome to Tethne Website')
    form = LoginForm(request.form)
    name = request.args.get('name')
    userpassword = request.args.get('password')
    print "arguments",name,userpassword 
    print "Login Form Values", request.cookies.get('username'), "abc:"
    #username = request.cookies.get('username')
    if request.method == 'GET'  : #and name != None
        #if form.validate_on_submit():
        #if 1:
            storage = FileStorage('./storage/userdb.fs')
            conn = DB(storage)
            print "Login start:",conn, type(conn),form.name.data
            dbroot = conn.open().root()
            try: 
            	print "dbroot['userdb'].values()", dbroot['userdb'].values(), "keys",dbroot['userdb'].keys() , dbroot['userdb']
                #for val in dbroot['userdb'].values():
        		#		print "value is : " , val, val.name,val.email,"form", form
                for key in dbroot['userdb'].keys():
        					#print "Yess!!", key, session['username'] 
                            #if  session['username'] == key :
                    if name == 'admin' :
                            # Need to get username from the form  password = sha256(password
                            print "COOOL it works atlast", "password1",dbroot['userdb'][key].password,"password2", sha256(request.args.get('password'))
                            print "inside login last loop:",dbroot, type(dbroot)
                            return render_template('pages/admin.home.html')
                    if name == key and name !='admin':
                            print "he is a normal user"
                            return render_template('pages/user.home.html')
                    else :
                            print "Error : No Such User"
                            pass
                            
            except:
                #flash('Username or password failed')
            	print " donot come here : except"
                pass           
             	
    else:
            print "comes in else"
            flash("Login Failed") #return redirect(url_for('login'))
            return redirect(url_for('ok'))
         
    return render_template('forms/login.html', form = form)

  
    
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    print "##form OBJECT::: register---->", form, form.email.data
    if request.method == 'POST':
            #session['username'] = request.form['username']
            if 'Register' in request.form:
                print "inside if"
            else:
            	print "inside else"
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
                # u.name = form.name.data
#                 u.email = form.email.data
#                 u.password = sha256(form.password.data).hexdigest()
#                 #u.password = form.password.data
#               	u.confirm = form.confirm.data
#               	u.institution = form.institution.data
#               	u.security_question = form.security_question.data
#               	u.security_answer = form.security_answer.data
                #userdb[u.name]=u
                dbroot['userdb'][u.name] = u
                session['username'] = u.name
                transaction.commit()
                print "Database added successfully", dbroot['userdb'][u.name], u.name, u
                #print "db now",db,type(db),db.__str__(),db.__getattribute__('databases'),"next",db.databases,db.database_name   
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
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
