
from DewServer import app as dewserver
from DewApi import app as dewapi

from werkzeug.wsgi import DispatcherMiddleware
from werkzeug.serving import run_simple

app = DispatcherMiddleware(dewserver, {
    '/api':     dewapi
})
run_simple('localhost', 5000, app, use_reloader=True)

