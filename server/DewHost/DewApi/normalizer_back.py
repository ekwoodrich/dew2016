import json
import uuid
import urllib2
import json
import datetime
from datetime import timedelta
import pprint
import copy

head_to_head_huffpo_uri = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president'
horserace_huffpo_uri_gop = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president-gop-primary'
horserace_huffpo_uri_dem = 'http://elections.huffingtonpost.com/pollster/api/polls?topic=2016-president-dem-primary'

horserace_huffpo_chart_uri = 'http://elections.huffingtonpost.com/pollster/api/charts?topic=2016-president'




def get_huffpo_poll_set(poll_type, after = '2014-11-1'):

	huffpo_poll_list = []
	page_num = 0
	poll_num = 0
	#print (head_to_head_huffpo_uri + '&page=' + str(page_num))
	
	while True:

		if poll_type == "head_to_head":
			response = urllib2.urlopen(head_to_head_huffpo_uri + '&page=' + str(page_num) + "&after=" + after)
		elif poll_type == "horserace_gop":	
			response = urllib2.urlopen(horserace_huffpo_uri_gop + '&page=' + str(page_num) + "&after=" + after)
		elif poll_type == "horserace_dem":
			response = urllib2.urlopen(horserace_huffpo_uri_dem + '&page=' + str(page_num) + "&after=" + after)
		elif poll_type == "chart":
			response = urllib2.urlopen(horserace_huffpo_chart_uri)

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


def normalize_horsetrack(estimates):
	very_normal_estimates = []
	
	semi_normal_estimates = convert_confused_responses(estimates)
	normal_estimates = normalize_other_response(semi_normal_estimates)
	
	for estimate in normal_estimates:
		
		if 'party' in estimate and estimate['party']:
			if estimate['party'].upper() == 'REP':		
				estimate['party'] = 'gop'
			else:
				estimate['party'] = estimate['party'].lower()
		very_normal_estimates.append(estimate)

	return very_normal_estimates

def normalize_other_response(estimates):
	other_value = 0.0
	normal_estimates = []

	for estimate in estimates:
		if estimate['other']:
			other_value += estimate['value']
			normal_estimates.append(estimate)
		else:
			normal_estimates.append(estimate)


	return normal_estimates
	
def convert_confused_responses(response_list):
	normal_responses = []
	
	for response in response_list:
		if 'first_name' in response and response['first_name']:
			normal_responses.append(response)
			response['other'] = False 			
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
	
			normal_poll['poll_info'] = {}
			normal_poll['poll_info']['poll_date'] = normalize_date(poll)
			normal_poll['poll_info']['poll_source_id'] = 3 * int(poll["id"])
			normal_poll['poll_info']['poll_source'] =  "ofhu"
			normal_poll['poll_info']['poll_source_uri'] =  poll["source"]
			
			if poll_type == "head_to_head":
				normal_poll['poll_info']['poll_race'] = "general"
				normal_poll['poll_info']['poll_party'] = 'all'
			else:
				normal_poll['poll_info']['poll_race'] = 'primary'


			
			if poll['pollster']:	
				normal_poll['pollster_info'] = {'sponsor_name' : poll['pollster'], 'pollster_partisan' : poll['partisan'].lower()}
			
			normal_poll['pollster_info']['sponsor_name'] = normal_poll['pollster_info']['sponsor_name'].replace('(D)', '')
			normal_poll['pollster_info']['sponsor_name'] = normal_poll['pollster_info']['sponsor_name'].replace('(R)', '')
			
			if "PPP" in normal_poll['pollster_info']['sponsor_name']:
				normal_poll['pollster_info']['sponsor_name'] = "Public Policy Polling"
	
			normal_poll['pollster_info']['pollster_list'] = []
			normal_poll['pollster_info']['pollster_list_json'] = ''
			normal_poll['pollster_info']['pollster_name'] = str(poll['survey_houses'])

			for house in poll['survey_houses']:
				house['party'] = house['party'].lower()
				house['party'] = house['party'].replace('n/a', 'nonpartisan')
				house['party'] = house['party'].replace('rep', 'gop')
				
	
				house['name'] = house['name'].replace('(D)', '')
				house['name'] = house['name'].replace('(R)', '')
				
				normal_poll['pollster_info']['pollster_list'].append(house)
			
			normal_poll['pollster_info']['pollster_list_json'] = json.dumps(normal_poll['pollster_info']['pollster_list'])
	
			normal_poll['poll_stats'] = {}
			
			normal_poll['poll_stats']['poll_method'] = poll['method'].lower().replace(' ', '_')
					
			normal_poll['poll_info']['survey_uuid'] =  'dew-uuid-'+str(uuid.uuid1())[0:10]
		
			question_num = 0			
			for question in poll['questions']:
					question_num += 1
					normal_poll_question = copy.deepcopy(normal_poll)
					subpop = 0
					
					
					normal_poll_question['poll_info']['uuid'] =  'dew-uuid-'+str(uuid.uuid1())[0:10]
	
					if question['state'] == 'US':
						normal_poll_question['poll_info']['poll_region'] = 'US'
					else:
						normal_poll_question['poll_info']['poll_region'] = question['state']
					try:	
						if 'topic' in question:	
							if "gop" in question['topic']:
								normal_poll_question['poll_info']['poll_party'] = "gop"
							elif "dem" in question['topic']:
								normal_poll_question['poll_info']['poll_party'] = "dem"
					except TypeError:
						normal_poll_question['poll_info']['poll_party'] = "dem"
					
					normal_poll_question['poll_info']['poll_name'] = question['name']
										
	
					#print normal_poll_question['poll_info']['poll_uuid'] 	
					#print normal_poll_question['pollster_info']['sponsor_name'] 
					#print normal_poll_question['poll_info']['poll_name'] 
	
					normal_poll_question['poll_stats']['poll_sample'] = question['subpopulations'][subpop]['observations']	
					normal_poll_question['poll_stats']['poll_margin_of_error'] = question['subpopulations'][subpop]['margin_of_error']
				

					if "Likely" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "likely_voters"
						
					
					if "Registered" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "registered_voters"
							
					if "Adult" in question['subpopulations'][subpop]['name']:
						normal_poll_question['poll_stats']['poll_screen'] = "adult_respondents"
					
					if 'vs' in question['name']:
						normal_poll_question['poll_stats']['poll_class'] = 'head_to_head'
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
					
						normal_poll_question['poll_info']['poll_office'] = 'president'
					elif 'Favorable' in question['name']:	
						normal_poll_question['poll_stats']['poll_class'] = 'favorable'
						normal_poll_question['poll_info']['poll_office'] = None
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
					elif 'Approval' in question['name']:	
						normal_poll_question['poll_stats']['poll_class'] = 'favorable'	
						normal_poll_question['poll_info']['poll_office'] = None
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
					elif 'Primary' in question['name'] or 'Caucus' in question['name']:
						normal_poll_question['poll_stats']['poll_class'] = 'horse_race'
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])	
						normal_poll_question['poll_info']['poll_race'] = 'primary'
						normal_poll_question['poll_info']['poll_office'] = 'president'
					elif 'General' in question['name'] and 'vs' not in question['name'] :
						normal_poll_question['poll_stats']['poll_class'] = 'horse_race'
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
						normal_poll_question['poll_info']['poll_office'] = 'president'
			
						normal_poll_question['poll_info']['poll_race'] = 'general'
					elif 'GE' in question['name']:	
							
						normal_poll_question['poll_stats']['poll_class'] = 'horse_race'
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
						normal_poll_question['poll_info']['poll_office'] = 'president'
					else:
						normal_poll_question['poll_stats']['poll_class'] = 'unknown'	
						normal_poll_question['poll_info']['poll_office'] = None
						normal_poll_question['estimates'] = normalize_horsetrack(question['subpopulations'][subpop]['responses'])
					if 'Presidential' in question['name'] or 'President' in question['name']:
						normal_poll_question['poll_info']['poll_office'] = 'president'
					
					if 'Identification' in question['name']:
						for current_poll in normal_poll_list:
							if current_poll['poll_info']['poll_source_id'] == poll['id']:
								current_poll['poll_stats']['poll_party_id'] = question['subpopulations'][subpop]['responses']	
						continue
					
					normal_poll_list.append(normal_poll_question)

	return normal_poll_list

def get_polls(update = False):
	
	if update:
		now_datetime = datetime.datetime.now()
		print 'Getting polls ending after ' + str((now_datetime -timedelta(days=3)).strftime('%Y-%m-%d'))
		return get_huffpo((now_datetime -timedelta(days=3)).strftime('%Y-%m-%d'))
	else:
		return get_huffpo()


def get_huffpo(after = '2014-11-01'):
	poll_set = []




	horserace_gop = get_huffpo_horserace_gop(after)
	horserace_dem = get_huffpo_horserace_dem(after)
	head_to_head = get_huffpo_head_to_head(after)

	for poll in horserace_gop:
		poll_set.append(poll)

	for poll in horserace_dem:
		poll_set.append(poll)
	for poll in head_to_head:
		poll_set.append(poll)

	return poll_set
def get_huffpo_horserace_gop(after):
	poll_set = get_huffpo_poll_set('horserace_gop')
	
	return normalize_huffpo_poll_list(poll_set, 'horserace_gop', after = after)
	
def get_huffpo_horserace_dem(after):
	poll_set = get_huffpo_poll_set('horserace_dem')
	
	return normalize_huffpo_poll_list(poll_set, 'horserace_dem', after = after)
def get_huffpo_head_to_head(after):
	poll_set = get_huffpo_poll_set('head_to_head', after = after);

	return normalize_huffpo_poll_list(poll_set, 'head_to_head')

#pp = pprint.PrettyPrinter(indent=4)
#pp.pprint(get_huffpo_horserace_gop())
