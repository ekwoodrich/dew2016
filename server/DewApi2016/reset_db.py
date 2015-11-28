import os

try:
	os.remove('db/dew2016.db')
except OSError:
	print "error removing db"

from models import db

db.create_all()
