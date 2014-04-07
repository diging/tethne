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



#registering blueprints for datacollection
from graphcollection.graph import graphset
from datacollection.views import dataset
from visualize_networks.visualize import viz
from jinja2 import TemplateNotFound

app.register_blueprint(graphset,url_prefix="/graph",template_folder='templates')
app.register_blueprint(dataset,url_prefix="/data",template_folder='templates')
app.register_blueprint(viz,url_prefix="/viz",template_folder='templates')

app.register_blueprint(graphset,url_prefix="/graph",template_folder='templates')
app.register_blueprint(dataset,template_folder='datacollection/templates')
app.register_blueprint(viz,url_prefix="/viz",template_folder='templates')


# app.register_blueprint(graphset,url_prefix="/",template_folder='/datacollection/templates')
# app.register_blueprint(dataset,url_prefix="/",template_folder='/datacollection/templates')
# app.register_blueprint(viz,url_prefix="/",template_folder='/datacollection/templates')


# Error handlers.
@app.errorhandler(500)
def internal_error(error):
    #db_session.rollback()
    return render_template('/errors/500.html'), 500

@app.errorhandler(404)
def internal_error(error):
    return render_template('/errors/404.html'), 404
# 
# if not app.debug:
#     file_handler = FileHandler('error.log')
#     file_handler.setFormatter(Formatter('%(asctime)s %(levelname)s: %(message)s '
#     '[in %(pathname)s:%(lineno)d]'))
#     app.logger.setLevel(logging.INFO)
#     file_handler.setLevel(logging.INFO)
#     app.logger.addHandler(file_handler)
#     app.logger.info('errors')


if __name__ == "__main__":
    app.debug = True
    app.run()




