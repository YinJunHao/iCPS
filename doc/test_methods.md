# Method used for development testing
References to get started:
1. For <python>(https://realpython.com/python-testing/#understanding-test-output)
## Unit testing
Unit test only runs for one component when there is no interaction with the other components.
### Python scripts
To test modules with access to MongoDB, test databases must be used. In the ```__init__``` of the class object, provide an object to create test database.
```
   def __init__(self, client, test=False):
        if test:
            self.job_history_db = client["test-job-history"]
        else:
            self.job_history_db = client["job-history"]
```
A python built-in package ```unittest``` is used. Create a test file in ```<parent dir>/test/unit/``` with that begins with "test".
Import the followings, and drop the involved test databases (if any).
```
import unittest
from bson import ObjectId
from pymongo import MongoClient
from CognitiveEngine.modules import <file to be tested>
from config import *

client = MongoClient(mongo_ip, mongo_port)
client.drop_database("test-job-history")
target = <module to be instantiated>(client, test=True)
```
Create a class that inherits from unittest.TestCase and write test scripts as its functions. Then allow the script to run all test functions when it's called as the ```__main__```.
```
class Tester(unittest.TestCase):
    def setUp(self):
		pass
	
	def test_<function name to be tested>(self):
		# preparations
		# input
		# actual
		# test the function
		# assertions
		pass		


if __name__ == '__main__':
    unittest.main()
```