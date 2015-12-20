import json
from pprint import pprint
import os

with open('secrets.json') as data_file:    
    data = json.load(data_file)

# Statement for enabling the development environment
DEBUG = True

# Define the application directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))  

DATABASE_CONNECT_OPTIONS = {}

SQLALCHEMY_TRACK_MODIFICATIONS = False

THREADS_PER_PAGE = 2

# Enable protection agains *Cross-site Request Forgery (CSRF)*
CSRF_ENABLED     = True

# Use a secure, unique and absolutely secret key for
# signing the data. 
CSRF_SESSION_KEY = data["CSRF_SESSION_KEY"]

# Secret key for signing cookies
SECRET_KEY = data["SECRET_KEY"]

SERVER_NAME = "localhost:5000"
