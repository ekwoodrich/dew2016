
from flask import Flask
from models import db, PoliticalPoll
from flask.ext.superadmin import Admin, model
from DewApi2016 import app

@app.route("/")
def hello():
    return "Hola, me gusta Oceano Digital!"

@app.route("/api/reset_polls")
def reset_polls():
    return "Polls Reset"

