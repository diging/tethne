from flask import Blueprint
graphset = Blueprint('graph',__name__)

@graphset.route('/login')
def login():
	return "I am graph login"

@graphset.route('/register')
def register():
	return "I am inside graph register " 
