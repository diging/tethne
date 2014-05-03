#from flask.ext.wtf import Form, TextField, PasswordField
#from flask.ext.wtf import Required, EqualTo, validators, Length
from wtforms import TextField,PasswordField
from wtforms import Form, BooleanField, TextField, PasswordField, validators,RadioField
#from wtforms.validators import DataRequired
#from wtforms.validators import Required, EqualTo, validators, Length
from flask import * # do not use '*'; actually input the dependencies.
from ZODB import FileStorage, DB
import models as mod
# Set your classes here.


class RegisterForm(Form):
    """
    
    """
    #Need to change the email using Email validator.
    
    name             = TextField('Username', [validators.Required(),validators.Length(min=4, max=35)])
    email            = TextField('Email', [validators.Required(),validators.Length(min=4, max=35)])
    password         = PasswordField('Password', [validators.Required(),validators.Length(min=6, max=30)])
    confirm          = PasswordField('Repeat Password',[validators.Required(), validators.EqualTo('password', message='Passwords must match')])
    institution      = TextField('Institution', [validators.Required(), validators.Length(min=4, max=40)])
    security_question= TextField('Security Question', [validators.Required(),validators.Length(min=10, max=40)])
    security_answer  = TextField('Security Answer', [validators.Required(), validators.Length(min=4, max=40)])
    
    
class LoginForm(Form):
    """
    
    """
    name        = TextField('Username', [validators.Required()])
    password    = PasswordField('Password', [validators.Required()])

class ForgotForm(Form):
    """
    
    """
    email       		= TextField('Email', [validators.Required(), validators.Length(min=6, max=40)] )
    security_question	= TextField('Security Question', [validators.Required(), validators.Length(min=10, max=40)])
    security_answer  	= TextField('Security Answer', [validators.Required(), validators.Length(min=6, max=40)])
    

class UserDetailsForm(Form):
    """
    
    """
    #Need to change the email using Email validator.
    
    name             = TextField('Username', [validators.Required(),validators.Length(min=4, max=35)])
    email            = TextField('Email', [validators.Required(),validators.Length(min=4, max=35)])
    institution      = TextField('Institution', [validators.Required(), validators.Length(min=4, max=40)])


class GenerateDataSetsForm(Form):
    """
    Create Data Sets form
    """
    #Need to check on the input dataset ID.
    
    input_type            = RadioField('input_type', [validators.Required()])
    input_path            = TextField('input_path', [validators.Required()])
    input_name            = TextField('dc_name', [validators.Required()])

class ListDataSetsForm(Form):
    """
    List DataColleection form
    """
    #Need to check on the input dataset ID.
    input_type = RadioField('input_type',[validators.Required()])

   