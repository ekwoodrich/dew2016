from models import db, Region, PoliticalPoll, Pollster, PollItem, Politician, ElectionSummary, PoliticalSurvey
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
	reg = Region(national = False, name = name, abv = abv)
	db.session.add(reg)
	#print reg

app.debug = False


reg = Region(national = True, name = "United States", abv = "US")
db.session.add(reg)

db.session.commit()
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
		new_poll = PoliticalPoll()
		
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
			new_pollster = get_or_create(db.session, Pollster, name = pollster['name'], party = pollster['party'])[0]	
			new_poll.pollster_list.append(new_pollster)
		
		
		
		new_poll.poll_sponsor = get_or_create(db.session, Pollster, name= poll['pollster_info']['sponsor_name'])[0]
		

		new_poll.sponsor_name = poll['pollster_info']['sponsor_name']
		
		new_poll.set_dewid()
		
		new_survey_query = get_or_create(db.session, PoliticalSurvey,source_id = poll['poll_info']['poll_source_id'])
		
		if new_survey_query[1]:
			new_survey_source_id  = new_survey_query[0].id
			new_survey_item = new_survey_query[0]
			new_survey_item.region = Region.query.filter_by(abv=poll['poll_info']['poll_region']).first()	
			new_survey_item.poll_date = poll['poll_info']['poll_date']['poll_end_date']
			new_survey_item.uuid = str(poll['poll_info']['survey_uuid'])
			new_survey_item.start_date = poll['poll_info']['poll_date']['poll_start_date']
			new_survey_item.end_date = poll['poll_info']['poll_date']['poll_end_date']
			new_survey_item.added_date = datetime.now()
			new_survey_item.pollster_list = new_poll.pollster_list
			new_survey_item.poll_sponsor = new_poll.poll_sponsor
			new_survey_item.sponsor_name = poll['pollster_info']['sponsor_name']

			new_survey_item.source = poll['poll_info']['poll_source']
			new_survey_item.source_id = poll['poll_info']['poll_source_id']	
			new_survey_item.source_uri = poll['poll_info']['poll_source_uri']
			new_survey_item.set_dewid()
			
			db.session.add(new_survey_item)
			db.session.commit()

			print 'New Survey Added'
			print new_survey_item.poll_sponsor

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
		db.session.rollback()

		

		
	if app.debug:
		if poll_iteration > 80:
			print 'Debug Run Complete'
			break	
		



print "COMPLETE"
print "new polls:"
print poll_count
print "excluded polls:"
print poll_failure_count

print ""

total_poll_count = PoliticalPoll.query.count()

new_snapshot = generate_presidential_snapshot(db.session, reg)


print "============GOP Presidential Snapshot========="
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(new_snapshot['average_gop_list'])
print ""
print "============DEM Presidential Snapshot========="
pp = pprint.PrettyPrinter(indent=4)
pp.pprint(new_snapshot['average_dem_list'])



