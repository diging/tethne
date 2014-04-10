DEBUG = True
THREADS_PER_PAGE = 4
CSRF_ENABLED     = True
CSRF_SESSION_KEY = "secret"

import os   
from ZODB.FileStorage import FileStorage
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess' #This is important.

# ZODB TO BE ADDED HERE
#storage = FileStorage('./storage/new.fs')

