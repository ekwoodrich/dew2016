from DewApi import app
from models import generate_snapshot, PoliticalPoll, PollUpdateReport, Politician, PollItem, Region, db, ElectionSummary, get_or_create, CandidateSummary
import flask.ext.restless
from flask.ext.restless import url_for, APIManager
from json2html import *
import json
from datetime import datetime
import jsonpickle
from sqlalchemy import desc
from flask import Response

@app.route("/")
def hello():
    return "Dewcaucus API"

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
    
@app.route("/snapshot/us/gop.html")
def gop_snapshot():
    summary_region = Region.query.filter_by(abv='US').first()
    gop_new_summary = ElectionSummary.query.filter_by(party='gop').order_by(desc(ElectionSummary.snapshot_date)).limit(3).first()
    if gop_new_summary:
        output_html = ""
    
        output_html += "<h2>"+ str(gop_new_summary.output_snapshot()[0]['snapshot_date']) +"</h2>" 
        output_html += "<h3>"+ str(gop_new_summary.output_snapshot()[0]['created_time']) +"</h3>" 
        output_html += "<h1>Republican Presidential Snapshot</h1>"
        position = 1
        for candidate in gop_new_summary.output_snapshot():
            output_html += "<h3>#" + str(position) + " " + candidate['politician'] + "</h3>"
            output_html += json2html.convert(json=jsonpickle.encode(candidate))
            output_html += "<br>"
            position += 1
        
        return output_html
    else:
        "No snapshots found."
@app.route("/snapshot/us/dem.html")
def dem_snapshot():
    summary_region = Region.query.filter_by(abv='US').first()
    dem_new_summary = ElectionSummary.query.filter_by(party='dem').order_by(desc(ElectionSummary.snapshot_date)).limit(3).first()

    if dem_new_summary:
        output_html = ""
    
    
        output_html += "<h2>"+ str(dem_new_summary.output_snapshot()[0]['snapshot_date']) +"</h2>" 
        output_html += "<h3>"+ str(dem_new_summary.output_snapshot()[0]['created_time']) +"</h3>" 
        output_html += "<h1>Democratic Presidential Snapshot</h1>"
        position = 1
        for candidate in dem_new_summary.output_snapshot():
            output_html += "<h3>#" + str(position) + " " + candidate['politician'] + "</h3>"
            output_html += json2html.convert(json=jsonpickle.encode(candidate))
            output_html += "<br>"
            position += 1
        
        return output_html
    else:
        return "No snapshots found."
@app.route("/reset_polls")
def reset_polls():
    return "Polls Reset"

