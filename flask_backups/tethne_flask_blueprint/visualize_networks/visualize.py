from flask import Blueprint
viz = Blueprint('visualize',__name__)

@viz.route('/login')
def show_info():
	return "I am inside viz login"

@viz.route('/register')
def speak():
	return "I am inside viz register " 
