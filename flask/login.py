from flask import * # do not use '*'; actually input the dependencies.
import logging
from logging import Formatter, FileHandler
from forms import *


app = Flask(__name__)
app.config.from_object('config')

from ZODB.FileStorage import FileStorage
from ZODB.DB import DB
# storage = FileStorage('data.fs')
# db = DB(storage)
# connection = db.open()
# root = connection.root()

# from flaskext.zodb import ZODB
# db = ZODB(app)

# @app.before_request
# def set_db_defaults():
#     if 'entries' not in db:
#         db['entries'] = List()
        
        
        
# @app.route('/logout')
# def logout():
#     session.pop('logged_in', None)
#     flash('You were logged out')
#     return redirect(url_for('show_entries'))
            
            
            
@app.route('/', methods=['GET','POST'])
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


@app.route('/login', methods=['GET','POST'])
def login():
	flash('Welcome to Tethne Website')
	form = LoginForm(request.form)
        if request.method == 'POST':
            session['username'] = request.form['username']
            return redirect(url_for('index'))
	return render_template('forms/login.html', form = form)
    
    
@app.route('/register',methods=['GET','POST'])
def register():
    form = RegisterForm(request.form)
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
