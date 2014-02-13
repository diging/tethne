from flask.ext.wtf import Form, TextField, PasswordField
from flask.ext.wtf import Required, EqualTo, validators, Length

# Set your classes here.

class RegisterForm(Form):
    name        	 = TextField('Username', validators = [Required(), Length(min=6, max=25)])
    email      		 = TextField('Email', validators = [Required(), Length(min=6, max=40)])
    password    	 = PasswordField('Password', validators = [Required(), Length(min=6, max=40)])
    confirm     	 = PasswordField('Repeat Password', [Required(), EqualTo('password', message='Passwords must match')])
    institution 	 = TextField('Institution', validators = [Required(), Length(min=6, max=40)])
    security_question= TextField('Security Question', validators = [Required(), Length(min=10, max=40)])
    security_answer  = TextField('Security Answer', validators = [Required(), Length(min=6, max=40)])

class LoginForm(Form):
    name        = TextField('Username', [Required()])
    password    = PasswordField('Password', [Required()])

class ForgotForm(Form):
    email       		= TextField('Email', validators = [Required(), Length(min=6, max=40)] )
    security_question	= TextField('Security Question', validators = [Required(), Length(min=10, max=40)])
    security_answer  	= TextField('Security Answer', validators = [Required(), Length(min=6, max=40)])