from flask import Flask
app = Flask(__name__)
#app.config.from_object('config') # get the values from a config value


from flask.ext.testing import TestCase

class MyTest(TestCase):
    
    def create_app(self):
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app