from models import db, Region, PoliticalPollQuestion, Pollster, PollItem, Politician, ElectionSummary, PoliticalPoll
from models import  get_or_create
from normalizer import get_polls
from sqlalchemy.exc import IntegrityError
from politics import states, senate_class_3_states
from datetime import datetime, timedelta
from models import app, generate_presidential_snapshot, PollUpdateReport
from sqlalchemy import desc
import sys
import pprint 
from operator import itemgetter
from subprocess import call

for abv, name in states.iteritems():
	try:
		reg = Region(national = False, name = name, abv = abv, iso = "US-" + abv)
		db.session.add(reg)
		db.session.commit()
		#print reg
	except IntegrityError:
		db.session.rollback()
		
try:	
	reg = Region(national = True, name = "United States", abv = "US", iso = "US")
	db.session.add(reg)
	db.session.commit()
except IntegrityError:
		db.session.rollback()
	
#app.debug = False



db.session.autoflush = False

poll_failure_count = 0
poll_count = 0
poll_iteration = 0

update_pollset = False
if 'summary_only' in sys.argv:
	print 'Generating new snapshot'
	
	if len(sys.argv) == 3:
		sum_reg = Region.query.filter_by(abv = sys.argv[2])
		print sys.argv[2]
	else:
		sum_reg = reg
	new_snapshot = generate_presidential_snapshot(db.session, region = sum_reg, force_new=True)
	sys.exit()

if 'update' in sys.argv:
	update_pollset = True	
	print "Updating polls..."


new_poll_count = 0

poll_list = get_polls(update = update_pollset)
for poll in poll_list:	
	print "Iteration:"	
	print poll_iteration
	print " "
	poll_iteration += 1

	try:			
		new_poll = PoliticalPollQuestion()
		
		for estimate in poll['estimates']:
			xstr = lambda s: s or ""

			new_poll_item = PollItem(value=estimate['value'])
			
			new_poll_item.choice = xstr(estimate['first_name'])+ " " + xstr(estimate['last_name'])
			if new_poll_item.choice == ' ':
				new_poll_item.choice = estimate['choice']
			
			new_poll_item.region = Region.query.filter_by(abv=poll['poll_info']['poll_region']).first()	
			new_poll_item.poll_class = estimate['poll_class']
			new_poll_item.poll_date = poll['poll_info']['poll_date']['poll_end_date']
			new_poll_item.poll_date_str = poll['poll_info']['poll_date']['poll_end_date'].strftime('%Y-%m-%d')

			new_poll_item.office = poll['poll_info']['poll_office'] 
			if 'first_name' in estimate:
				if estimate['first_name']:
					new_politician = get_or_create(db.session, Politician, first_name = estimate['first_name'], last_name = estimate['last_name'], party = estimate['party'])[0]		
		
					new_politician.update()
	
					if poll['poll_info']['poll_office']:
						new_politician.seeking_office = poll['poll_info']['poll_office']
					
					if poll['poll_info']['poll_office']:
						new_politician.seeking_office = poll['poll_info']['poll_office']
						
					new_politician.set_dewhash()
					db.session.add(new_politician)
					new_poll_item.politician = new_politician
			
			if 'party' in estimate:
				new_poll_item.party = estimate['party']
			
			if estimate['choice'] == 'other':
				new_poll_item.other = True

			db.session.add(new_poll_item)
			
			new_poll.poll_items.append(new_poll_item)
		

		if poll['pollster_info']['pollster_partisan'] == 'nonpartisan':
			new_poll.partisan = False		
		else:
			new_poll.partisan = True
		
		new_poll.region = Region.query.filter_by(abv=poll['poll_info']['poll_region']).first()	
		
		new_poll.office = poll['poll_info']['poll_office'] 
		new_poll.survey_uuid = str(poll['poll_info']['survey_uuid'])
		new_poll.title = poll['poll_info']['poll_name']


		new_poll.sample = poll['poll_stats']['poll_sample']
		new_poll.screen = poll['poll_stats']['poll_screen']
		new_poll.method = poll['poll_stats']['poll_method']
		new_poll.margin_of_error = poll['poll_stats']['poll_margin_of_error']

		new_poll.poll_class = poll['poll_stats']['poll_class']

		new_poll.start_date = poll['poll_info']['poll_date']['poll_start_date']
		new_poll.end_date = poll['poll_info']['poll_date']['poll_end_date']

		new_poll.added_date = datetime.now()

		
		for pollster in poll['pollster_info']['pollster_list']:
			new_pollster = get_or_create(db.session, Pollster, name = pollster['name'], party = pollster['party'], group_type = pollster['group_type'])[0]	
			new_poll.pollster_list.append(new_pollster)
			
			new_pollster.set_dewhash()
		
		
		

		new_poll.pollster_str = poll['pollster_info']['pollster_str']
		
		new_poll.set_dewhash()
		
		new_survey_query = get_or_create(db.session, PoliticalPoll,source_id = poll['poll_info']['poll_source_id'])
		
		if new_survey_query[1]:
			new_survey_source_id  = new_survey_query[0].id
			new_survey_item = new_survey_query[0]
			new_survey_item.poll_date = poll['poll_info']['poll_date']['poll_end_date']
			new_survey_item.uuid = str(poll['poll_info']['survey_uuid'])
			new_survey_item.start_date = poll['poll_info']['poll_date']['poll_start_date']
			new_survey_item.end_date = poll['poll_info']['poll_date']['poll_end_date']
			new_survey_item.added_date = datetime.now()
			new_survey_item.pollster_list = new_poll.pollster_list
			new_survey_item.pollster_str = poll['pollster_info']['pollster_str']

			new_survey_item.source = poll['poll_info']['poll_source']
			new_survey_item.source_id = poll['poll_info']['poll_source_id']	
			new_survey_item.source_uri = poll['poll_info']['poll_source_uri']
			new_survey_item.set_dewhash()
			
			db.session.commit()

			print 'New Survey Added'
			print new_survey_item.pollster_str

		db.session.add(new_poll)
		db.session.commit()
		
		new_survey_query[0].polls.append(new_poll)


		poll_count += 1



		print "New Polls Added:"
		print poll_count
		print str(new_poll)
	except IntegrityError:	
		
		poll_failure_count += 1
		print "----excluded duplicate-----\n"
		print str(new_poll)
		print str(new_poll.start_date) + " - " + str(new_poll.end_date)
		db.session.rollback()

		

		
	if app.debug:
		if poll_iteration > 400:
			print 'Debug Run Complete'
			break	
		



print "COMPLETE"
print "new polls:"
print poll_count
print "excluded polls:"
print poll_failure_count

print ""

total_poll_count = PoliticalPollQuestion.query.count()



