"""
    This script contains various views of  GraphCollections
    for User Login, creating GraphCollection
    and viewing the GraphCollection details.
    
    views 
    ```````
    /create_gc
    /list_gc
    /view_gc_details
    /del_gc
    /add_gc
    /results_gc
    .. autosummary::

  
    
"""



from flask import Blueprint
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
from datacollection.views import dataset


#
graphset = Blueprint('graph',__name__)


@graphset.route('/show')
def show():
#    return render_template('/graphcollection/pages/placeholder.home.html',dataset = dataset)
    return render_template('/graphcollection/pages/test.html',dataset = dataset)
@graphset.route('/register')
def register():
	return "I am inside graph register " 
