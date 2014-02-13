import os

# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.
DEBUG = True

CSRF_ENABLED = True
SECRET_KEY = 'you-will-never-guess'

# ZODB TO BE ADDED HERE

# Connect to the database
# SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'database.db')
