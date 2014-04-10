DEBUG = True
THREADS_PER_PAGE = 4
CSRF_ENABLED     = True
CSRF_SESSION_KEY = "secret"

import os   
from ZODB.DB import DB
from ZODB.FileStorage import FileStorage
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True
ADMIN = False
CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess' #This is important.
storage = FileStorage('./storage/userdb.fs')
conn = DB(storage)
#print "setting DB defaults:",conn, type(conn),
DBROOT = conn.open().root()
#print "DBROOT",DBROOT


# ZODB TO BE ADDED HERE
#storage = FileStorage('./storage/new.fs')

