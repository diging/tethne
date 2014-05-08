from flask import Flask
app = Flask(__name__)
app.config.from_object('config') # get the values from a config value

# adding all
from flask import Flask, session, redirect, url_for, escape, request,render_template,flash
from flask_wtf import Form
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
from ZODB.FileStorage import FileStorage
from ZODB.DB import DB



#registering blueprints for datacollection
from views import dataset
import controllers as control
#print "gdb root in app", app.config['DBROOT'], app.config['CSRF_ENABLED']
app.register_blueprint(dataset)

# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('/errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('/errors/404.html'), 404


def set_db_defaults():
     
    """
    This is to be called only once during the script.
    Setting the ZODB databases. 
     
    """
    storage = FileStorage('./storage/userdb.fs')
    conn = DB(storage)
    #print "setting DB defaults:",conn, type(conn),
    dbroot = conn.open().root()
    DBROOT=app.config['DBROOT']
#     print "gdb root in app:::::", DBROOT
 
#    try:
#        for val in ['userdb','graphdb','datadb','dsdb']:
#            if val in dbroot.keys():
#                print "val", val
#                pass
#            else:
#                print "else"
#                DBROOT[val] = Dict()
#    except:          
#        print "except user db dbroot:",DBROOT['dsdb'], type (DBROOT['dsdb'])

    
if __name__ == "__main__":
    app.debug = True
    #set_db_defaults()
    app.run()
    




