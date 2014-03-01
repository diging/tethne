#from flask.ext.wtf import Form, TextField, PasswordField
#from flask.ext.wtf import Required, EqualTo, validators, Length
from wtforms import TextField,PasswordField
from wtforms import Form, BooleanField, TextField, PasswordField, validators
#from wtforms.validators import DataRequired
#from wtforms.validators import Required, EqualTo, validators, Length
from flask import * # do not use '*'; actually input the dependencies.
from ZODB import FileStorage, DB
import models as mod
# Set your classes here.

# storage = FileStorage('users.fs')
# db = DB(storage)
# connection = db.open()
# # dbroot is a dict like structure.
# dbroot = connection.root()  # retrieving the root of the tree
# #  
# if not dbroot.has_key('userdb'):
#     from BTrees.OOBTree import OOBTree
#     dbroot['userdb'] = OOBTree()

class RegisterForm(Form):

    
    name             = TextField('Username', [validators.Required(),validators.Length(min=6, max=35)])
    email            = TextField('Email', [validators.Required(),validators.Length(min=6, max=35)])
    password         = PasswordField('Password', [validators.Required(),validators.Length(min=6, max=30)])
    confirm          = PasswordField('Repeat Password',[validators.Required(), validators.EqualTo('password', message='Passwords must match')])
    institution      = TextField('Institution', [validators.Required(), validators.Length(min=4, max=40)])
    security_question= TextField('Security Question', [validators.Required(),validators.Length(min=10, max=40)])
    security_answer  = TextField('Security Answer', [validators.Required(), validators.Length(min=4, max=40)])
    
    
    
#     def __repr__(self):
#         print "comes here:"
#         return '<User %r>' % (userobj.name)

class LoginForm(Form):
    name        = TextField('Username', [validators.Required()])
    password    = PasswordField('Password', [validators.Required()])

class ForgotForm(Form):
    email       		= TextField('Email', [validators.Required(), validators.Length(min=6, max=40)] )
    security_question	= TextField('Security Question', [validators.Required(), validators.Length(min=10, max=40)])
    security_answer  	= TextField('Security Answer', [validators.Required(), validators.Length(min=6, max=40)])