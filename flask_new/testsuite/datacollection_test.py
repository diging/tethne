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
from flask.new import controller

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

        filename = "../../testsuite/testin/wos_citations.txt" 
		input_type = "WOS"
		input_datacollection_name = "myDC1"     
		self.status=controller.CreatePersistentDataCollection(input_type,filename,input_datacollection_name)
		
		#Import DB and initialize the root node.


	def testProperWOSData(self):
		#Check the status returned from the controller was true
		self.assertEqual(self.status, "True")
		#Persistent DataCollection stored with correct ID. ( hash(name))

		#check the number of papers in Persistent DataCollection and the DataCollection

		
		#check that DataCollection is indexed by WOSID.
		

	
	def testIncorrectWOSData(self):

		#Should return false from the controller
		self.assertEqual(self.status, "False")


	def testProperWOSDataWrongInputFormat(self):

		#should return false from the controller.
		self.assertEqual(self.status, "False")
		pass



if __name__ == '__main__':
    unittest.main()