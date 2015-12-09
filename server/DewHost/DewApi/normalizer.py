import json
import uuid
import urllib2
import json
import datetime
from datetime import timedelta
import pprint
import copy
from politics import states

head_to_head_huffpo_uri = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president'
horserace_huffpo_uri_gop = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president-gop-primary'
horserace_huffpo_uri_dem = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president-dem-primary'

head_to_head_huffpo_senate_uri = 'http://elections.huffingtonpost.com/pollster/api/charts?topic=2016-president'



senate_huffpo_head_to_head_uri = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-senate'


def get_huffpo_poll_set(poll_type, after = '2014-11-1', race='president'):

	huffpo_poll_list = []
	page_num = 0
	poll_num = 0
	#print (head_to_head_huffpo_uri + '&page=' + str(page_num))
	
	while True:
		if race == 'president':
			if poll_type == "head_to_head":
				response = urllib2.urlopen(head_to_head_huffpo_uri + '&page=' + str(page_num) + "&after=" + after)
			elif poll_type == "horserace_gop":	
				response = urllib2.urlopen(horserace_huffpo_uri_gop + '&page=' + str(page_num) + "&after=" + after)
			elif poll_type == "horserace_dem":
				response = urllib2.urlopen(horserace_huffpo_uri_dem + '&page=' + str(page_num) + "&after=" + after)
			elif poll_type == "chart":
				response = urllib2.urlopen(horserace_huffpo_chart_uri)
		elif race == 'senate':
			if poll_type == "head_to_head":
				response = urllib2.urlopen(senate_huffpo_head_to_head_uri + '&page=' + str(page_num) + "&after=" + after)
		
		print race + " " + poll_type + " page " + str(page_num)
		
		html = response.read()
		huffpo_poll_page = json.loads(html)
		
		if poll_type == 'chart':
			return huffpo_poll_page

		for poll_json in huffpo_poll_page:
			poll_num += 1
			huffpo_poll_list.append(poll_json)
	
		page_num = page_num + 1

		#print page_num

		if not len(huffpo_poll_page):
			break
	return huffpo_poll_list

def normalize_huffpo_api(huffpo_set, set_type):

	if set_type == 'poll_list':
		return normalize_huffpo_poll_list(huffpo_set)


def normalize_date(poll):
		
	normal_date = {}
	
	normal_date['poll_start_date'] =  datetime.datetime.strptime(poll['start_date'], "%Y-%m-%d")			     
	normal_date['poll_end_date'] = datetime.datetime.strptime(poll['end_date'], "%Y-%m-%d")
	
	normal_date['poll_last_update'] =  datetime.datetime.strptime(poll['last_updated'].split('T')[0], "%Y-%m-%d")

	return normal_date


def normalize_favor(estimates, poll_estimate):
	very_normal_estimates = []
	
	semi_normal_estimates = convert_confused_responses(poll_estimate['poll_stats']['poll_class'], estimates)
	normal_estimates = semi_normal_estimates
	
	for estimate in normal_estimates:
		estimate['poll_class'] = 'favorable'
		if 'party' in estimate and estimate['party']:
			if estimate['party'].upper() == 'REP':		
				estimate['party'] = 'gop'
			else:
				estimate['party'] = estimate['party'].lower()
		very_normal_estimates.append(estimate)

	return very_normal_estimates
def normalize_horsetrack(estimates, poll_estimate):
	very_normal_estimates = []
	
	semi_normal_estimates = convert_confused_responses(poll_estimate['poll_stats']['poll_class'], estimates)
	normal_estimates = normalize_other_response(poll_estimate['poll_stats']['poll_class'], semi_normal_estimates)
	
	for estimate in normal_estimates:
		estimate['poll_class'] = poll_estimate['poll_stats']['poll_class'] 	
		if 'party' in estimate and estimate['party']:
			if estimate['party'].upper() == 'REP':		
				estimate['party'] = 'gop'
			else:
				estimate['party'] = estimate['party'].lower()
		very_normal_estimates.append(estimate)
	return very_normal_estimates

def normalize_other_response(poll_class, estimates):
	other_value = 0.0
	other_present = False
	normal_estimates = []

	if poll_class == 'unknown' or poll_class == 'favorable':
		return estimates
		
	for estimate in estimates:
		
		if estimate['other']:
			other_value += estimate['value']
			other_present = True
		else:
			normal_estimates.append(estimate)
			
	if other_present:
		normal_estimates.append({'choice' : 'Undecided/Unknown', 'value' : other_value, 'other' : True, 'first_name' : '', 'last_name' : ''})

	return normal_estimates
	
def convert_confused_responses(poll_class, response_list):
	normal_responses = []
	for response in response_list:
		if poll_class == 'unknown' or poll_class == 'favorable':
			response['other'] = False 	
			normal_responses.append(response)
		elif 'first_name' in response and response['first_name']:
			response['other'] = False 
			normal_responses.append(response)			
		else:
			response['other'] = True
			normal_responses.append(response)
			
	return normal_responses


def normalize_huffpo_poll_list(poll_list, poll_type):
	normal_poll_list = []
	huffpo_poll_id_list = []

	for poll in poll_list:
			#print poll	
			normal_poll = {}

			#copy basic poll info
			normal_poll['poll_info'] = {}
			normal_poll['poll_info']['poll_date'] = normalize_date(poll)
			normal_poll['poll_info']['poll_source_id'] = 3 * int(poll["id"])
			normal_poll['poll_info']['poll_source'] =  "ofhu"
			normal_poll['poll_info']['poll_source_uri'] =  poll["source"]
		

			#copy pollster info
			if poll['pollster']:	
				normal_poll['pollster_info'] = {'pollster_str' : poll['pollster'], 'pollster_partisan' : poll['partisan'].lower(), 'group_type' : 'pollster'}
				
			#remove party from naming
			normal_poll['pollster_info']['pollster_str'] = normal_poll['pollster_info']['pollster_str'].replace('(D)', '')
			normal_poll['pollster_info']['pollster_str'] = normal_poll['pollster_info']['pollster_str'].replace('(R)', '')
			
	
			normal_poll['pollster_info']['pollster_list'] = []
			normal_poll['pollster_info']['pollster_list_json'] = ''
			
			#iterate through "survey houses" and assign as pollster sponsors
			for house in poll['survey_houses']:
				house['party'] = house['party'].lower()
				house['party'] = house['party'].replace('n/a', 'nonpartisan')
				house['party'] = house['party'].replace('rep', 'gop')
				
	
				house['name'] = house['name'].replace('(D)', '')
				house['name'] = house['name'].replace('(R)', '')
				
				#normalize naming, deprecated
				if "PPP" in normal_poll['pollster_info']['pollster_str']:
					normal_poll['pollster_info']['pollster_str'] = "Public Policy Polling"
					
				house['group_type'] = 'pollster'
				
				normal_poll['pollster_info']['pollster_list'].append(house)
				
			for sponsor in poll['sponsors']:
				sponsor['party'] = sponsor['party'].lower()
				sponsor['party'] = sponsor['party'].replace('n/a', 'nonpartisan')
				sponsor['party'] = sponsor['party'].replace('rep', 'gop')
				
	
				sponsor['name'] = sponsor['name'].replace('(D)', '')
				sponsor['name'] = sponsor['name'].replace('(R)', '')
				
				#normalize naming, deprecated
				if "PPP" in normal_poll['pollster_info']['pollster_str']:
					normal_poll['pollster_info']['pollster_str'] = "Public Policy Polling"
					
				sponsor['group_type'] = 'sponsor'
				
				normal_poll['pollster_info']['pollster_list'].append(sponsor)
			
			normal_poll['pollster_info']['pollster_list_json'] = json.dumps(normal_poll['pollster_info']['pollster_list'])
	
			#create dict for poll stats
			normal_poll['poll_stats'] = {}
			normal_poll['poll_stats']['poll_method'] = poll['method'].lower().replace(' ', '_')
					
			#assign uuid for parent survey
			normal_poll['poll_info']['survey_uuid'] =  'dew-uuid-'+str(uuid.uuid1())[0:10]
		
			question_num = 0			
			
			#iterate through poll questions and generate normalized poll item responses 
			for question in poll['questions']:
					question_num += 1
					normal_poll_question = copy.deepcopy(normal_poll)
					subpop = 0
					
					
					poll_topic = question['topic']	

					normal_poll_question['poll_info']['uuid'] =  'dew-uuid-'+str(uuid.uuid1())[0:10]
					
					#normalize region for the poll
					if question['state'] == 'US':
						normal_poll_question['poll_info']['poll_region'] = 'US'
					else:
						normal_poll_question['poll_info']['poll_region'] = question['state']
					 
					#determine party scope for poll question
					
					

					normal_poll_question['poll_info']['poll_name'] = question['name']

					if not normal_poll_question['poll_info']['poll_region']:
						for abv, name in states.iteritems():
							if name in normal_poll_question['poll_info']['poll_name']:
								normal_poll_question['poll_info']['poll_region'] = abv
								break
								
					#copy poll stats to question object	
					normal_poll_question['poll_stats']['poll_sample'] = question['subpopulations'][subpop]['observations']	
					normal_poll_question['poll_stats']['poll_margin_of_error'] = question['subpopulations'][subpop]['margin_of_error']
				
					#determine screen method for poll
					if "Likely" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "likely_voters"
					if "Registered" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "registered_voters"
							
					if "Adult" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "adult_respondents"
					

					#determine class of eletion (primary/general/etc)
					#as well as format of poll (head to head, hor race, etc#
					if 'vs' in question['name']:
						normal_poll_question['poll_stats']['poll_class'] = 'head_to_head'
					elif 'Approval' in question['name'] or 'Favorable' in  question['name']:	
						normal_poll_question['poll_stats']['poll_class'] = 'favorable'	
						normal_poll_question['poll_info']['poll_office'] = None
					elif 'Primary' in question['name'] or 'Caucus' in question['name']:
						normal_poll_question['poll_stats']['poll_class'] = 'horse_race'
						normal_poll_question['poll_info']['poll_race'] = 'primary'
					elif 'General' in question['name'] and 'vs' not in question['name'] :
						normal_poll_question['poll_stats']['poll_class'] = 'horse_race'	
						normal_poll_question['poll_info']['poll_race'] = 'general'
					elif 'GE' in question['name']:
						normal_poll_question['poll_stats']['poll_class'] = 'head_to_head'
					else:
						normal_poll_question['poll_stats']['poll_class'] = 'unknown'	
						normal_poll_question['poll_info']['poll_office'] = None
					
					#determine the election year from topic
					if poll_topic:
						if '2016' in poll_topic:
							normal_poll_question['poll_info']['election_year'] = 2016
						elif '2014' in poll_topic:
							normal_poll_question['poll_info']['election_year'] = 2014
						elif '2012' in poll_topic:
							normal_poll_question['poll_info']['election_year'] = 2012
						else:
							normal_poll_question['poll_info']['election_year'] = None
					

					#Determine the political office based on title or topic	
					if 'Presidential' in question['name'] or 'President' in question['name']:
						normal_poll_question['poll_info']['poll_office'] = 'president'
					elif 'Senate' in question['name']:
						normal_poll_question['poll_info']['poll_office'] = 'senate'
					elif 'President' in question['name']:
						normal_poll_question['poll_info']['poll_office'] = 'president'
					else:	
						normal_poll_question['poll_info']['poll_office'] = None
					if poll_topic:
						if 'senate' in poll_topic :
							normal_poll_question['poll_info']['poll_office'] = 'senate'
						elif 'governor' in poll_topic:
							normal_poll_question['poll_info']['poll_office'] = 'governor'	
						elif 'president' in poll_topic:	
							normal_poll_question['poll_info']['poll_office'] = 'president'
						else:
							normal_poll_question['poll_info']['poll_office'] = None

					#check if current question is party id, if so, copy party id data to parent survey 
					if 'Identification' in question['name']:
						for current_poll in normal_poll_list:
							if current_poll['poll_info']['poll_source_id'] == poll['id']:
								current_poll['poll_stats']['poll_party_id'] = question['subpopulations'][subpop]['responses']	
						continue
					#normalize estimates(PollItem)s for head to head and horse race
					if normal_poll_question['poll_stats']['poll_class'] == 'head_to_head' or normal_poll_question['poll_stats']['poll_class'] == 'horse_race':
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'], normal_poll_question)
					#normalize estiamtes (PollItem)s for favorable polls
					elif normal_poll_question['poll_stats']['poll_class'] == 'favorable':	
						normal_poll_question['estimates'] = normalize_favor(question['subpopulations'][subpop]['responses'], normal_poll_question)
					#normalize unknown class of poll using horserace
					else:
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'], normal_poll_question)
					#add populated poll question to main list
					normal_poll_list.append(normal_poll_question)
				
	return normal_poll_list

def get_polls(update = False):
	
	if update:
		now_datetime = datetime.datetime.now()
		print 'Getting polls ending after ' + str((now_datetime -timedelta(days=10)).strftime('%Y-%m-%d'))
		return get_huffpo((now_datetime -timedelta(days=5)).strftime('%Y-%m-%d'))
	else:
		return get_huffpo()


def get_huffpo(after = '2014-11-01'):
	poll_set = []




	horserace_gop = get_huffpo_horserace_gop(after)
	horserace_dem = get_huffpo_horserace_dem(after)
	head_to_head = get_huffpo_head_to_head(after)
	senate_head_to_head = get_huffpo_head_to_head_senate(after)

	for poll in horserace_gop:
		poll_set.append(poll)

	for poll in horserace_dem:
		poll_set.append(poll)
	for poll in head_to_head:
		poll_set.append(poll)
	for poll in senate_head_to_head:
		poll_set.append(poll)

	return poll_set
def get_huffpo_horserace_gop(after):
	poll_set = get_huffpo_poll_set('horserace_gop', after = after)
	
	return normalize_huffpo_poll_list(poll_set, 'horserace_gop')
	
def get_huffpo_horserace_dem(after):
	poll_set = get_huffpo_poll_set('horserace_dem', after = after)
	
	return normalize_huffpo_poll_list(poll_set, 'horserace_dem')
def get_huffpo_head_to_head(after):
	poll_set = get_huffpo_poll_set('head_to_head', after = after);

	return normalize_huffpo_poll_list(poll_set, 'head_to_head')
def get_huffpo_head_to_head_senate(after):
	poll_set = get_huffpo_poll_set('head_to_head', after = after, race = 'senate');

	return normalize_huffpo_poll_list(poll_set, 'head_to_head')

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(get_huffpo_horserace_gop())
