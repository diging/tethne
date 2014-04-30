"""
    This script contains various controller methods which controls the flow
    between the models and views.

    views 
    ```````
    1. /create_datacollection       
    
    
    
"""

# Import Statements   
from flask import Flask, session, redirect, url_for, escape,\
                    request,render_template,flash
from flask_wtf import Form
from forms import LoginForm,RegisterForm,ForgotForm,GenerateDataSetsForm,ListDataSetsForm
from flask import abort,Blueprint
import datetime,logging
from logging import Formatter, FileHandler

import random as random
import models as db
import views as view

# Initializing the Blueprint. 
# Instead of @app the module will have @dataset
dataset = Blueprint('controllers',__name__,template_folder='templates')

@dataset.route('/create_datacollection/', methods=['GET','POST'])
def create_datacollection():
    """
    This is the controller from the CreateDataCollection View. 
    It gets the following data from user form.
    
    Input data:
    -----------

    1.Input file, 
    2.Input filetype, 
    3.Input DataCollection Name 

    Funtions:
    ---------

    a. Parse the data using the input file and input filetype
       and create a list of papers.
    b. Create a DataCollection from the list of papers. 
    c. Interact with the model and store the details in the 
       Persistent DataCollection object.
    d. Return true or false to the view. 

     
    """
    
    if request.method == 'GET'  :
        print "comes inside controller"
        #return nothing.
    try:
            file_format = input_file_format         # got from the view. 
            username    = session['username']
            input_file  = input_file_with_path      # with full path
    except:
            print "comes to except"
            pass
         
    return redirect(url_for('.login'))
            
