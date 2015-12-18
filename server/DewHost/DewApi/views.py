from DewApi import app
from models import  PoliticalPoll, Pollster, PollUpdateReport, Politician, PollItem, Region, db, ElectionSummary, get_or_create, CandidateSummary


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
    pollster_list = Pollster.query.all()
    response_list = []
    
    for pollster in pollster_list[0:10]:
        
        response_list.append({
            'name' : pollster.name,
            'url' : pollster.url(),
            'group_type' : pollster.group_type,
            'uuid' : pollster.uuid,
            'count' : len(pollster.polls)
        })
    return Response(json.dumps(response_list), mimetype = 'text/json')
    
@app.route("/pollsters/summary")
def pollsters_summary():
    pollster_str_list = []
    pollster_list = Pollster.query.all()
    
    for pollster in pollster_list:
        pollster_str_list.append(pollster.name)
    response = {
        'total_count' : len(pollster_list),
        'pollsters' : pollster_str_list
    }
    return Response(json.dumps(response), mimetype = 'text/json')
    
@app.route("/pollsters/<pollster_slug>/")
def pollster_selcet(pollster_slug):
    print pollster_slug
    pollster = Pollster.query.filter_by(slug = pollster_slug).first()
    poll_list = []
    
    for poll in pollster.polls:
        poll_list.append({
          'pollster' : poll.pollster_str,
          'start_date' : poll.start_date.strftime("%m-%d-%y"),
          'end_date' : poll.end_date.strftime("%m-%d-%y"),
          'url' : poll.url(),
          'source_url' : poll.source_uri
        })
    response = {
            'name' : pollster.name,
            'url' : pollster.url(),
            'group_type' : pollster.group_type,
            'uuid' : pollster.uuid,
            'count' : len(pollster.polls),
            'polls' : poll_list
    }
    return Response(json.dumps(response), mimetype = "text/json")
    
@app.route("/politicians/us/")
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
            'region' : politician.region, 
            'url' : politician.url()})
        
    return Response(json.dumps(response_list), mimetype = "text/json")
    
@app.route("/polls/")
def polls():		
    region = Region.query.filter_by(abv='US').first()
    poll_list = PoliticalPoll.query.order_by(PoliticalPoll.start_date.desc()).limit(10)
    
    poll_list_json = []
    
    for poll in poll_list:
        poll_region_list = []
        poll_question_list = []
        
        for poll_question in poll.polls:
            poll_choice_list = []
            for poll_item in poll_question.poll_items:
                if poll_question.poll_class == 'horse_race' or poll_question.poll_class == 'head_to_head':
                    politician = Politician.query.filter_by(slug_human = poll_item.choice).first()
                    politician_url = ''
                    
                    if politician:
                        politician_url = politician.url()
                    else:
                        politician_url = ''
                    if poll_item.other:
                        poll_choice_list.append({'choice' : 'Undecided/Unknown', 'value' : poll_item.value, 'other' : poll_item.other})
                    else:  
                        poll_choice_list.append({'choice' : poll_item.choice,  'url' : politician_url, 'value' : poll_item.value, 'party' : poll_item.party, 'other' : poll_item.other})
                else:
                    poll_choice_list.append({'choice' : poll_item.choice, 'value' : poll_item.value, 'party' : poll_item.party, 'other' : poll_item.other})
            
            poll_question_list.append({
                'title' : poll_question.title,
                'sample_size' : poll_question.sample,
                'method' : poll_question.method,
                'screen' : poll_question.screen,
                'poll_class' : poll_question.poll_class,
                'choices' : poll_choice_list,
            })
            
            poll_region_dict = {'name' : poll_question.region.name, 'abv': poll_question.region.abv, 'url' : poll_question.region.url()}
            
            if poll_region_dict not in poll_region_list:
                poll_region_list.append(poll_region_dict)
                
        poll_list_json.append({
          'pollster' : poll.pollster_str,
          'start_date' : poll.start_date.strftime("%m-%d-%y"),
          'end_date' : poll.end_date.strftime("%m-%d-%y"),
          'url' : poll.url(),
          'source_url' : poll.source_uri,
          'regions' : poll_region_list,
          'questions' : poll_question_list
            
        })
    return Response(json.dumps(poll_list_json), mimetype = "text/json")
    
@app.route("/polls/<poll_slug>")
def polls_select():	
    pass
    	
@app.route("/politicians/us/<slug>")
def politician_select(slug):
    politician = Politician.query.filter_by(slug = slug).first()

    if politician:
        return Response(json.dumps({
            'name' : politician.slug_human, 
            'first_name' : politician.first_name, 
            'last_name' : politician.last_name, 
            'slug': politician.slug, 'uuid' : politician.uuid, 
            'seeking_office' : politician.seeking_office, 
            'party' : politician.party, 
            'region' : politician.region, 
            'url' : politician.url()}), mimetype = "text/json")
    else:
        return "not found"   
@app.route("/elections/us/<office>/snapshot")
def us_pres_snapshot(office):
    region = Region.query.filter_by(iso = "US").first()
    
    return Response(json.dumps(region.generate_snapshot(seeking_office = office)), mimetype = "text/json")
    
@app.route("/elections/us/<office>/<party>/snapshot")
def us_pres_party_snapshot(office, party):
    region = Region.query.filter_by(iso = "US").first()
    
    return Response(json.dumps(region.generate_snapshot(seeking_office = office, party = party)), mimetype = "text/json")

@app.route("/admin/reset_polls")
def reset_polls():
    return "Polls Reset"
    
@app.route("/admin/update_polls")
def update_polls():
    return "Polls Updated"

@app.route("/admin/poll_summary")
def poll_summary():
    return "Poll Summary"

