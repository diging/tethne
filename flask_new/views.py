"""
    This script contains various views of DataCollections 
    for user Login, creating DataCollection/Graph Collections
    and viewing the datasets/graph details.
    
    views 
    ```````
    1. /login       
    2. /register    
    3. /admin       
    4. /user         
    5. /forgot
    6. /logout
    7. /datacollection/list
    8. /datacollection/create
    9. /datacollection/view
    10./datacollection/create_slices/
    11./graphcollection/list
    12./graphcollection/create
    13./graphcollection/view
    14./graphcollection/analyze
    15./visualize/list
    16./visualize/<id>
    17./index    - dummy one, gets routed to /login
    
    18th, 19th views were delete_datasets and delete_graphcollections.
    Those are not views, to be viewed by users.
    Insted they will be just called as functions and returned back to
    /datacollection/list and /graphcollection/list accordingly.
    jquery/JS can be used to show the refreshed list to the user.
    
    
    run the views as http://127.0.0.1:5000/datacollection/list
    
"""

# Import Statements   
from flask import Flask, session, redirect, url_for, escape,\
                    request,render_template,flash
from flask_wtf import Form
from forms import LoginForm,RegisterForm,ForgotForm,GenerateDataSetsForm
from flask import abort,Blueprint
import datetime,logging
from logging import Formatter, FileHandler
import tethne.readers as rd
import random as random


# Importing helpers module
import helpers as help           

# Initializing the Blueprint. 
# Instead of @app the module will have @dataset
dataset = Blueprint('views',__name__,template_folder='templates')

"""
Test Views
"""
# test view
@dataset.route('/info')
def info():
	return "I am inside Show_info"
	
# To catch the URLs which are not defined 
@dataset.route('/', defaults={'path': ''})
@dataset.route('/<path:path>')
def catch_all(path):
    return 'You want path: %s, This one is a wrong path! Please check!' % path
    
"""
Login Views
"""
     
@dataset.route('/index', methods=['GET','POST'])
def index():
    """
    When the user provides /index as the URL, it automatically gets routed
    to the 
        
    """
    if 'username' not in session:
        #print " comes here in index", session, type(session)
        return redirect(url_for('.login'))
    else:
        return redirect(url_for('.user'))
    


@dataset.route('/', methods=['GET','POST'])
def home():
    """
    A dummy view for login routing.
    
    """
    return redirect(url_for('.login'))

@dataset.route('/login/', methods=['GET','POST'])
def login():
    """
    Login check for a user. 
    
    If its successful user would be redirected to either 
    "user" view or "admin" view.
    
    If the user is not registered then an error message is displayed and 
    redirected to Login page.
    
    Currently there is no DB hence there are no check
    
    """
    
    if request.method == 'GET'  :
        print "comes inside login"
        return render_template('forms/login_new.html')
    try:
            username = request.form['username']
            session['username'] = username
            password = request.form['password']
    except:
            print "comes to except"
            pass
    print "username" , username
        # Dummy routing to admin page and other pages.
    if username == 'admin':
            return redirect(url_for('.admin'))
    else:
            return redirect(url_for('.user'))
         
    return redirect(url_for('.login'))
            
    
@dataset.route('/register',methods=['GET','POST'])
def register():
    """
    Register a new user.
    Comes to Login Page after register.
    """
    form = RegisterForm(request.form)
   
    if request.method == 'POST':
        flash('Registered successfuly')
        return redirect(url_for('.login'))
    return render_template('forms/register.html', form = form)



@dataset.route('/forgot',methods=['GET','POST'])
def forgot():
    """
    This is when  user forgets his username / password
    This module is a TO- DO.
    
    """
    form = ForgotForm(request.form)
    return render_template('forms/forgot.html', form = form)    



@dataset.route('/logout')
def logout():
    """
    When the User logs out, the session is ended and  
    user is redirected to login page.
    """
    session.pop('logged_in', None)
    flash('You are logged out')
    return redirect(url_for('.login'))

"""
Admin and User Views

"""

#Admin view              
@dataset.route('/admin', methods=['GET','POST'])
def admin():
    """
    Admin view.
    It has the admin functions like,
    Listing the users, delete the users and approve the users.
    """
    # Handling if normal users try accessing this view.
    if session['username'] != 'admin':
        flash ("Only Admins can view this page!!")
        return redirect(url_for('.user'))    
    
    if request.method == 'GET'  : 
        columns = [ 'S.No', 'User Name', 'Institution', 'Email ID']
        results = [['1', 'Data#1156734', '20140408132211', 'dadsds'], ['2', 'Data#2356734', '20140308092211','adasda'], ['3', 'Data#4456734', '20140408112221', 'dadasd']]
    return render_template('pages/admin.home.html', columns=columns,results=results)


#@dataset.route('/<username>/home', methods=['GET','POST'])
@dataset.route('/user/home', methods=['GET','POST'])
def user():
    """
    User View
    """
    if request.method == 'GET'  :
        return render_template('pages/user.home.html', user = session['username'])
    return redirect(url_for('.dc_list'),username= session['username']) 


"""
DataCollection Views
"""

@dataset.route('/datacollection/list', methods=['GET','POST'])
def dc_list():
    """
    List Data Collection 
    Show the user the existing collection of datacollection.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C', 'S.No', 'DataCollection ID', 'Created Date' ]
        checkboxes = ['','','']
        #results is not used as of now.
        results =  [['1', 'Data#1156734', '20140408132211'], ['2', 'Data#2356734', '20140308092211'], ['3', 'Data#4456734', '20140408112221']]   
        return render_template('pages/list.datasets.html', user = session['username'])


@dataset.route('/datacollection/dc_del', methods=['GET','POST'])
def dc_del():
    """
    Delete Data Collection
    Show the user the existing collection of datacollection.
    """
    flash("Dataset deleted successfully")
    return redirect(url_for('.dc_list'))


@dataset.route('/datacollection/create/', methods = ['GET','POST'])
def dc_create():
    """
    Create Data Collection
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    if request.method == 'POST' :
    
        # Parse data.
        # Actually it should be the file taken from the server.
        # Currently this is a dummy one.
        papers = rd.wos.read("/Users/ramki/tethne/testsuite/testin/2_testrecords.txt")
    
        # Create a DataCollection
        from tethne.data import DataCollection, GraphCollection
        D = DataCollection(papers)
        log = "Dataset #127846748 created successfully"
        return render_template('pages/generate.datasets.html', user = user, text= log)
    
    return render_template('pages/generate.datasets.html', user = user, form= form)



@dataset.route('/datacollection/create_slices/', methods = ['GET','POST'])
def dc_create_slices():
    """
    Create datasets slices
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    if request.method == 'POST'  :
        # take a DataCollection, and slice it.
        log = "Silces created and added in DB successfully"

        return render_template('pages/list.datasets.html', user = user, text= log)

    return render_template('pages/generate.datasets.slices.html', user = user, form= form)


@dataset.route('/datacollection/view/<data>', methods=['GET','POST'])
def dc_stats(data=None):
    """
    List the stats for a selected Data Collection 
    
    """
    if request.method == 'GET'  :
        print "Data is ", data
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C','S No', 'Paper ID', 'No. of nodes', 'No. of edges' ]
        checkboxes = ['','','','']
        results =  [['', '1', 'paper#113', '34', '250'], \
                    ['2', 'paper#1234',  '43', '250'], \
                    ['3', 'paper#4734',  '134', '2510']]
        
        return render_template('pages/view.datasets.html', user = session['username'],data=data)


"""
Graph Collection Views
"""


@dataset.route('/graphcollection/list', methods=['GET','POST'])
def gc_list():
    """
    List Graph Collection 
    Show the user the existing GraphCollection.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C', 'S.No', 'GraphCollection ID', 'Created Date' ]
        checkboxes = ['','','']
        results =  [['1', 'gc#1156734', '20140408132211'], ['2', 'gc#2356734', '20140308092211'], ['3', 'gc#4456734', '20140408112221']]   
        return render_template('pages/list.graphcollection.html', user = session['username'])


@dataset.route('/graphcollection/gc_del', methods=['GET','POST'])
def gc_del():
    """
        Delete GraphCollection
        Show the user the existing collection of Graphcollection.
        
    """
    flash("GraphCollection deleted successfully")
    return redirect(url_for('.gc_list'))

@dataset.route('/graphcollection/create', methods = ['GET','POST'])
def gc_create():
    """
    Create a new Graph Collection from existing DataCollection
    """
    form = GenerateDataSetsForm(request.form)
    user = session['username']
    if request.method == 'POST' :
        G = "Gc#11124"
        #As of now displaying some random GC number and date.
        log = "GraphCollection" +str (G) +"created successfully and added in the database at " + "201404061223412 "
        return render_template('pages/generate.graphsets.html', user = user, text= log)
    
    return render_template('pages/generate.graphsets.html', user = user, form= form)
    

@dataset.route('/graphcollection/analyze', methods=['GET','POST'])
def gc_analyze():
    """
        Analyze the  selected GraphCollection (ex: between centrality)
        
        """
    if request.method == 'GET'  :
        
        return render_template('pages/analyze.graphcollection.html', user = session['username'])


@dataset.route('/graphcollection/view/<data>', methods=['GET','POST'])
def gc_stats(data=None):
    """
    List the stats for a selected GraphCollection 
    
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        columns = ['C','S No', 'Paper ID', 'No. of nodes', 'No. of edges' ]
        checkboxes = ['','','','']
        results =  [['', '1', 'paper#113', '34', '250'], ['2', 'paper#1234',  '43', '250'], ['3', 'paper#4734',  '134', '2510']]   
        return render_template('pages/view.graphcollection.html', user = session['username'],data=data)



"""
Visualize Networks View
"""


@dataset.route('/visualize/list', methods=['GET','POST'])
def viz():
    """
    Visualize Graph Collection using D3.
    """
    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        return render_template('pages/viz.graphcollection.html', user = session['username'])

@dataset.route('/visualize/#23412334', methods=['GET','POST'])
def dc_viztest():
   
    """
    Visualize Graph Collection using D3.
    #23412334 -This is a to-do, this has to be replaced with the
    original graphCollection ID.
    """

    if request.method == 'GET'  :
        # hard code the values for showing demo on wednesday Apr 08 2014.
        return render_template('pages/viz.network.html', user = session['username'])


    
"""
Not used
"""

# # Default port:
# if __name__ == '__main__':
#     app.run()
#     before_first_request()
#     

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
