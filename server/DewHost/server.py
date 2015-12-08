
from DewServer import app as dewserver
from DewApi import app as dewapi
from DewApi.models import db as dewapidb
from DewApi.models import PollItem
from flask.ext.restless import APIManager, url_for

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple
import flask

dewserver.config.from_object('config')
dewapi.config.from_object('config')

    

app = DispatcherMiddleware(dewserver, {
    '/api':     dewapi
})


run_simple('localhost', 5000, app, use_reloader=True)
