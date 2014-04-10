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


# @app.route('/create_data/', methods = ['GET','POST'])
# def create_data():
#          
#     if request.method == 'GET'  : 
#         print " comes inside"
#         
#         return render_template('pages/admin.home.html', columns=columns,results=results)
#         return 'Hello World!'
#     
#     return redirect(url_for('login'))






# Default port:
if __name__ == '__main__':
    #app.before_first_request()
    app.run()
    


