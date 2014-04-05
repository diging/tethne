
#1st try
# from flask import Blueprint, request, render_template
# 
# graphcollection = Blueprint("auth", __name__, url_prefix="/auth")
# 
# @datacollection.route("/hello")
# def hello():
#     return render_template("datacollection/pages/placeholder.home.html")

# 2nd try
# from flask import Blueprint, render_template,request
# graphcollection = Blueprint('graphcollection', __name__, template_folder='pages')
# 
# 
# @graphcollection.route('/', methods=['GET','POST'])
# def index():
#     """
#     A dummy view for login routing.
#     
#     """
#     print "comes here"
#     return redirect(url_for('login'))
# 
# @graphcollection.route('/login', methods=['GET','POST'])
# def login():
#     return render_template('graphtest.html')


from flask import Blueprint, render_template
main = Blueprint('main', __name__, template_folder='pages')

@main.route('/')
def index():
    return render_template('index.html')