"""
Unit Test case module to check the DataCollection operations.

"""
import sys
sys.path.append("../")
import unittest
from flask_new import run
from flask_new import views
from flask_new import models

#app.config.from_object('config') # get the values from a config value


class MyTest(unittest.TestCase):
    
    def create_app(self):
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app



class CreateDataCollection(unittest.TestCase):

	def setUp(self):
		pass

	def testProperWOSData(self):
		pass

	def testIncorrectWOSData(self):
		pass

	def testProperWOSDataWrongInputFormat(self):
		pass


