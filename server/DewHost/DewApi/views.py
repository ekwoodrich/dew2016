from DewApi import app
from models import generate_snapshot, PoliticalPoll, PollUpdateReport, Politician, PollItem, Region, db, ElectionSummary, get_or_create, CandidateSummary


import json
from datetime import datetime
import jsonpickle
from sqlalchemy import desc
from flask import Response

@app.route("/")
def hello():
    return "Dewcaucus API"

@app.route("/pollsters/")
def pollsters():
    return Response(json.dumps(""))
    
@app.route("/pollsters/<pollster_slug>")
def pollster_selcet(pollster_slug):
    return Response(json.dumps(""), mimetype = "text/json")
    
@app.route("/politicians/")
def politician_all():
    politician_list = Politician.query.all()
    
    response_list = []
    
    for politician in politician_list:
        response_list.append({
            'name' : politician.slug_human, 
            'first_name' : politician.first_name, 
            'last_name' : politician.last_name, 
            'slug': politician.slug, 'uuid' : politician.uuid, 
            'seeking_office' : politician.seeking_office, 
            'party' : politician.party, 
            'url' : politician.url()})
        
    return Response(json.dumps(response_list), mimetype = "text/json")
    
@app.route("/politicians/<dew_id>")
def politician_select(dew_id):
    return "politicians"
    
@app.route("/elections/us/presidential/snapshot")
def us_pres_snapshot():
    return Response(json.dumps(generate_snapshot()), mimetype = "text/json")
    
@app.route("/elections/us/presidential/<party>/snapshot")
def us_pres_party_snapshot(party):
    return Response(json.dumps(generate_snapshot(party)), mimetype = "text/json")
    
@app.route("/elections/us/senate/snapshot")
def us_senate_snapshot():
    return Response(json.dumps(generate_snapshot()), mimetype = "text/json")
    
@app.route("/elections/us/senate/<party>/snapshot")
def us_senate_party_snapshot(party):
    return Response(json.dumps(generate_snapshot(party)), mimetype = "text/json")
    
@app.route("/elections/us/governor/snapshot")
def us_gov_snapshot():
    return Response(json.dumps(generate_snapshot()), mimetype = "text/json")
    
@app.route("/elections/us/governor/<party>/snapshot")
def us_gov_party_snapshot(party):
    return Response(json.dumps(generate_snapshot(party)), mimetype = "text/json")
    
@app.route("/reset_polls")
def reset_polls():
    return "Polls Reset"

