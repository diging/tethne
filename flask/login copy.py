#from flask import * # do not use '*'; actually input the dependencies.
#This will create an error

from flask_wtf import Form
from wtforms import TextField
from wtforms.validators import DataRequired
import logging
from logging import Formatter, FileHandler
#from ZODB import *
from flask import Flask,render_template,url_for

app = Flask(__name__)
#app.config.from_object('config')

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
import models as mod

storage = FileStorage('./storage/users.fs')
db = DB(storage)
connection = db.open()
# dbroot is a dict like structure.
dbroot = connection.root()  # retrieving the root of the tree


# ZEO commented as of now.

# db = ZODB.config.databaseFromURL('zodb.conf')
# connection = db.open()
# root = connection.root()

# 
# from flaskext.zodb import ZODB
# db = ZODB(app)


# # setting the defaults 
# @app.before_request
# def set_db_defaults():
#     if 'userdb' not in db:
#         db['userdb'] = List()
              
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))


#Ensure that a 'userdb' key is present
#in the root
if not dbroot.has_key('userdb'):
    from BTrees.OOBTree import OOBTree
    dbroot['userdb'] = OOBTree()
    # userdb is a <BTrees.OOBTree.OOBTree object at some location>
userdb1 = dbroot['userdb']           
print userdb1
            
@app.route('/index', methods=['GET','POST'])
def index():
    form = LoginForm(request.form)
    if 'username' in session:
        return 'Logged in as %s' % escape(session['username'])
    # return render_template('forms/register.html', form = form)
    return 'You are not logged in'            


@app.route('/', methods=['GET','POST'])
def home():
    form = LoginForm(request.form)
    return render_template('forms/login.html', form = form)



@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db['userdb'].append(request.form)
    flash('New entry was successfully posted')
    
    
    return redirect(url_for('show_entries'))
@app.route('/login', methods=['GET','POST'])
def login():
	flash('Welcome to Tethne Website')
	form = LoginForm(request.form)
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
        else :
            return redirect(url_for('register'))
        
	return render_template('forms/login.html', form = form)
    
    
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
    print "form OBJECT:::", form
    if request.method == 'POST':
            #session['username'] = request.form['username']
            if 'Register' in request.form:
                print " inside if"
            else:
                print " else", request.form
                u=mod.User()
                print "User:", u
                u.name = request.form['username']
                #db['userdb'] = request.form['username']
                print " user name",request.form['username']
                
            flash('Registered successfuly')
    return render_template('forms/register.html', form = form)

@app.route('/forgot',methods=['GET','POST'])
def forgot():
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)    

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
