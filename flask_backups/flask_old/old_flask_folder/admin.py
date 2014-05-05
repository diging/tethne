from flask import Flask
from flask import * 
from flask.ext.admin import Admin

app = Flask(__name__)

admin = Admin(app)
app.run()