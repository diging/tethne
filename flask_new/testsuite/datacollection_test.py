"""
Unit Test case module to check the DataCollection operations.

"""
import sys
sys.path.append("../")
import unittest
from flask_new import run
from flask_new import views
from flask_new import models
from nose.tools import assert_equals

#app.config.from_object('config') # get the values from a config value


class MyTest(unittest.TestCase):
    
    def create_app(self):
        
        app = Flask(__name__)
        app.config['TESTING'] = True
        return app



class CreateDataCollection(unittest.TestCase):

	def setUp(self):
		server.app.testing=True
        self.app = server.app.test_client()
		pass

	def testProperWOSData(self):
		#Check the status returned from the controller was true

		#Persistent DataCollection stored with correct ID. ( hash(name))

		#check the number of papers in Persistent DataCollection and the DataCollection

		#check that DataCollection is indexed by WOSID.

		pass

	def testIncorrectWOSData(self):

		#Should return false from the controller

		pass

	def testProperWOSDataWrongInputFormat(self):

		#should return false from the controller.
		
		pass



if __name__ == '__main__':
    unittest.main()