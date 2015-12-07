from DewApi import app
from models import PoliticalPoll, PollUpdateReport, Politician, PollItem, Region, db, ElectionSummary, get_or_create, CandidateSummary
import flask.ext.restless
from json2html import *
import json
from datetime import datetime
import jsonpickle
from sqlalchemy import desc
@app.route("/")
def hello():
    return "Dewcaucus API"

@app.route("/api/snapshot/us/gop.html")
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
@app.route("/api/snapshot/us/dem.html")
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
@app.route("/api/reset_polls")
def reset_polls():
    return "Polls Reset"
manager = flask.ext.restless.APIManager(app, flask_sqlalchemy_db=db)

manager.create_api(PollUpdateReport, methods=['GET'])
manager.create_api(ElectionSummary, exclude_columns = ['snapshot_blob'], methods=['GET'])
manager.create_api(CandidateSummary, methods=['GET'])
manager.create_api(PollItem, methods=['GET'])
manager.create_api(PoliticalPoll, methods=['GET'], primary_key = 'dewid', exclude_columns=['survey', 'survey_uuid'])
manager.create_api(Region, methods=['GET'])
manager.create_api(Politician, exclude_columns = ['poll_items'], methods=['GET'], primary_key = 'slug')
