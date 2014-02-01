# all the imports
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, \
    abort, render_template, flash

# configuration
DATABASE = '/tmp/flaskr.db'
DEBUG = True
SECRET_KEY = 'development key'
USERNAME = 'admin'
PASSWORD = 'default'

# create our little application
app = Flask(__name__)
app.config.from_object(__name__)

def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

if __name__ == '__main__':
        app.run(host='0.0.0.0')