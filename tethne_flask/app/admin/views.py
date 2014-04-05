# from flask import Blueprint, request, render_template
# 
# datacollection = Blueprint("auth", __name__, url_prefix="/auth")
# 
# @datacollection.route("/hello")
# def hello():
#     return render_template("datacollection/pages/placeholder.home.html")


# 2nd try

# from flask import Blueprint, render_template,request
# datacollection = Blueprint('datacollection', __name__, template_folder='pages')
# 
# 
# 
# @datacollection.route('/', methods=['GET','POST'])
# def index():
#     """
#     A dummy view for login routing.
#     
#     """
#     print "comes here"
#     return redirect(url_for('login'))
# 
# @datacollection.route('/login', methods=['GET','POST'])
# def login():
#     return render_template('admintest.html')
# 
# 
# @datacollection.route('/ok', methods=['GET','POST'])
# def ok():
#     return render_template('pages/placeholder.home.html')
#  

from flask import Blueprint, render_template
admin = Blueprint('admin', __name__, template_folder='pages')

@admin.route('/')
def index():
    return render_template('index.html')
