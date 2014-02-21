from flask.ext.wtf import Form, TextField, PasswordField
from flask.ext.wtf import Required, EqualTo, validators, Length
from flask import * # do not use '*'; actually input the dependencies.
from ZODB import FileStorage, DB
import models as m
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
    userobj = m.User()
    userobj.name        	 = TextField('Username', validators = [Required(), Length(min=6, max=20)])
    userobj.email      		 = TextField('Email', validators = [Required(), Length(min=6, max=30)])
    userobj.password    	 = PasswordField('Password', validators = [Required(), Length(min=6, max=30)])
    userobj.confirm     	 = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])
    userobj.institution 	 = TextField('Institution', validators = [Required(), Length(min=4, max=40)])
    userobj.security_question= TextField('Security Question', validators = [Required(), Length(min=10, max=40)])
    userobj.security_answer  = TextField('Security Answer', validators = [Required(), Length(min=4, max=40)])
    
    print " comes  RegisterForm"
    print "name:", userobj.name, "\n","email:",userobj.email
    
#     def __repr__(self):
#         print "comes here:"
#         return '<User %r>' % (userobj.name)

class LoginForm(Form):
    name        = TextField('Username', [Required()])
    password    = PasswordField('Password', [Required()])

class ForgotForm(Form):
    email       		= TextField('Email', validators = [Required(), Length(min=6, max=40)] )
    security_question	= TextField('Security Question', validators = [Required(), Length(min=10, max=40)])
    security_answer  	= TextField('Security Answer', validators = [Required(), Length(min=6, max=40)])