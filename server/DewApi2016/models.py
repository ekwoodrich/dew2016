from flask.ext.sqlalchemy import SQLAlchemy
import uuid
from flask import Flask
import hashlib
from sqlalchemy.sql.expression import ClauseElement
import pickle
from sqlalchemy.exc import IntegrityError
import pprint
from datetime import datetime
import json
from flask.ext.superadmin import Admin, model


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/dew2016.db'
app.secret_key = 'Add your secret key'


db = SQLAlchemy(app)


politician_polls = db.Table('politician_polls', 
    	db.Column('political_poll_id', db.Integer, db.ForeignKey('political_poll.id')),
	db.Column('politician_id', db.Integer, db.ForeignKey('politician.id'))
)

class Politician(db.Model):
	
	__tablename__ = 'politician'

	id = db.Column(db.Integer, primary_key=True)

	first_name = db.Column(db.String(120))
	last_name = db.Column(db.String(120))
	slug = db.Column(db.String(120))
	slug_human = db.Column(db.String(120))
	party = db.Column(db.String(20))
	
	seeking_office = db.Column(db.String(120))	
	
	summary_items = db.relationship('CandidateSummary', backref = 'politician')
	
	poll_items = db.relationship('PollItem', backref='politician', lazy = 'dynamic')			
	polls = db.relationship('PoliticalPoll', secondary = politician_polls, backref = 'politician', lazy = 'dynamic')
	
	def update(self):
		self.slug = str(self.first_name).lower() + "_" + str(self.last_name).lower()
		self.slug_human = str(self.first_name) + " " + str(self.last_name)
	def __str__(self):
		if not self.slug_human:
			self.slug_human = str(self.first_name) + " " + str(self.last_name)
		if not self.slug:
			self.slug = str(self.first_name).lower() + "_" + str(self.last_name).lower()
		return self.slug_human

class OpinionSummary(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'))


	snapshot_date = db.Column(db.DateTime)

def party_initial(party_name):
	if party_name.lowrer() == 'gop':
		return '(R)'
	if part_name.lower() == 'dem':
		return '(D)'
	else:
		return '(I)'


class CandidateSummary(db.Model):
	__tablename__ = 'candidate_summary'
	
	id = db.Column(db.Integer, primary_key=True)
	created_datetime = db.Column(db.DateTime)
	party = db.Column(db.String(20))	
	
	politician_name = db.Column(db.String(255))
	election = db.Column(db.String(255))
	
	politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'))
	
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))	

	snapshot_blob = db.Column(db.Text)
	snapshot_json = db.Column(db.Text)
	
	
	def __init__(self, party, region, politician_name, snapshot_blob, snapshot_json, election_year = 2016, election = 'president'):
		if party:
			self.party = party
		self.region = region
		self.snapshot_blob = snapshot_blob
		self.snapshot_json = snapshot_json
		self.created_datetime = datetime.now()
		self.election = election
		self.politician_name = politician_name
		self.party = party
		
		self.politician = Politician.query.filter_by(slug_human=politician_name).first()


	def output_snapshot(self):
		return pickle.dumps(self.snapshot_blob)
	def __str__(self):
		return self.politician_name + " " + party_initial(self.party) + " - " + str(self.created_datetime)

class ElectionSummary(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	snapshot_date = db.Column(db.DateTime)
	created_datetime = db.Column(db.DateTime)
	party = db.Column(db.String(20))	

	election = db.Column(db.String(255))
	election_year = db.Column(db.Integer, default = 2016)
	
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))	

	snapshot_blob = db.Column(db.Text)
	snapshot_json = db.Column(db.Text)

	def __init__(self, party, region, snapshot_date, session, election_year = 2016, election = 'president'):
		if party:
			self.party = party
		self.region = region
		self.snapshot_date = datetime.today().date()
		self.created_datetime = datetime.now()
		self.election = election
		self.process_snapshot(session = session)
		
	def process_snapshot(self, session, json_format = False):
		if not json_format:
			print 'Processing poll average snapshot'
		
		if self.party:
			poll_item_list = PollItem.query.filter_by(poll_class = 'horse_race', party = self.party)
		else:
			poll_item_list = PollItem.query.filter_by(poll_class = 'horse_race')
		snapshot =	[]	
		poll_snapshot = {}
		politician_list = []
	
		for poll_item in poll_item_list:
			if poll_item.choice not in politician_list:
				politician_list.append((poll_item.choice, poll_item.office))
		
		
	
		for politician in politician_list:
			running_avg_cutoff = 10
		
			print 'Processing ' + politician[0]	

			poll_snapshot[str(politician[0])] = {}		
			
			politician_snapshot = {}			
		
		
		
			politician_snapshot = {'politician':politician[0],'running_average_count' : 0, 'running_average_sum' : 0, 'average_sum' : 0, 'average_count' : 0, 'office' : politician[1]}
		
			candidate_poll_list = PollItem.query.filter_by(region = self.region, choice = politician[0], poll_class = 'horse_race', office = politician[1])
			
			#calculate running mean
			for item in candidate_poll_list:
				politician_snapshot['running_average_count'] += 1
				politician_snapshot['running_average_sum'] += item.value
				if politician_snapshot['running_average_count'] == running_avg_cutoff:
					break
			#calculate unweighted mean
			for item in candidate_poll_list:
				politician_snapshot['average_count'] += 1
				politician_snapshot['average_sum'] += item.value
							
			politician_snapshot['average'] = float(politician_snapshot['average_sum']+.001)/float(politician_snapshot['average_count']+.001)	
			politician_snapshot['running_average'] = float(politician_snapshot['running_average_sum']+.001)/float(politician_snapshot['running_average_count']+.001)	
			
			if json_format:
				politician_snapshot['snapshot_date'] = self.snapshot_date.isoformat()
				politician_snapshot['created_time'] = self.created_datetime.time().isoformat()
			else:
				politician_snapshot['snapshot_date'] = self.snapshot_date
				politician_snapshot['created_time'] = self.created_datetime.time()
			if politician_snapshot['average_count'] > 10:
				if politician_snapshot['politician'] == 'Mitt Romney':
					break
				if politician_snapshot['politician'] == 'Andrew Cuomo':
					break
				if politician_snapshot['politician'] == 'Elizabeth Warren':
					break
				if politician_snapshot not in snapshot:
					snapshot.append(politician_snapshot)
					if json_format:
						new_candidate_summary = CandidateSummary(party = self.party, region = self.region, politician_name = politician[0], snapshot_blob = pickle.dumps(politician_snapshot), snapshot_json = json.dumps(politician_snapshot))
						session.add(new_candidate_summary)
		session.commit()
		sorted_snapshot = sorted(snapshot, key=lambda k: k['running_average'])
		sorted_snapshot.reverse()
		
		if json_format:	
			self.snapshot_json = json.dumps(sorted_snapshot)
		else:
			self.snapshot_blob = pickle.dumps(sorted_snapshot)
			self.process_snapshot(session = session, json_format = True)

	def output_snapshot(self):
			return pickle.loads(self.snapshot_blob)
	def __str__(self):
		return self.party + " - " + str(self.created_datetime)

poll_pollsters = db.Table('poll_pollsters', 
	db.Column('political_poll_id', db.Integer, db.ForeignKey('political_poll.id')),
	db.Column('pollster_id', db.Integer, db.ForeignKey('political_pollster.id'))
)	

survey_pollsters = db.Table('survey_pollsters', 
	db.Column('political_survey_id', db.Integer, db.ForeignKey('political_survey.id')),
	db.Column('pollster_id', db.Integer, db.ForeignKey('political_pollster.id'))
)
class PoliticalSurvey(db.Model):
	__tablename__ = 'political_survey'
	
	id = db.Column(db.Integer, primary_key=True)
	dewid = db.Column(db.String(255), unique = True)
	
	election_year = db.Column(db.Integer, default = 2016)
	
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))
	uuid = db.Column(db.String(255))
	
	pollster_list = db.relationship('Pollster', secondary = survey_pollsters, backref = db.backref('political_survey', lazy = 'dynamic'))

	sponsor_id = db.Column(db.Integer, db.ForeignKey('political_pollster.id'))
	sponsor_name = db.Column(db.String(255))
	
	polls = db.relationship('PoliticalPoll', backref='political_survey', lazy = 'dynamic')	

	
	partisan = db.Column(db.Boolean)
	party = db.String(10)


	source = db.Column(db.String(48))
	source_id = db.Column(db.Integer)
	source_uri = db.Column(db.String(256))

	
	def set_dewid(self):
		dewid = hashlib.md5()
		
		dewid.update(str(self.source_id))
		
		if not dewid.hexdigest()[0:6]:
			self.set_dewid()

		self.dewid = 'dewid-' + dewid.hexdigest()[0:6]
		
	def __str__(self):
		return (str(self.election_year) + " " + str(self.sponsor_name) + " " + str(self.region) + " " + "\n") 
		
class PoliticalPoll(db.Model):
	
	__tablename__ = 'political_poll'
	
	
	id = db.Column(db.Integer, primary_key=True)

	survey_uuid = db.Column(db.String(255))
	dewid = db.Column(db.String(255), unique = True)
	
	title = db.Column(db.String(255))
	
	election_year = db.Column(db.Integer, default = 2016)
	pollster_list = db.relationship('Pollster', secondary = poll_pollsters, backref = db.backref('political_poll', lazy = 'dynamic'))
	#pollster_list_json = db.Column(db.String(200))	
	sponsor_name = db.Column(db.String(80))
	sponsor_id = db.Column(db.Integer, db.ForeignKey('political_pollster.id'))
	survey_id = db.Column(db.Integer, db.ForeignKey('political_survey.id'))
	
	partisan = db.Column(db.Boolean)
	party = db.String(10)

	poll_class = db.Column(db.String(48))	
	
	screen = db.Column(db.String(48))
	method = db.Column(db.String(48))
	sample = db.Column(db.Integer)
	margin_of_error = db.Column(db.Float)
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))	
	

	added_date = db.Column(db.DateTime)
	start_date = db.Column(db.DateTime)
	end_date = db.Column(db.DateTime)

	office = db.Column(db.String(32))

	poll_items = db.relationship('PollItem', backref='political_poll', lazy = 'dynamic')	
		
	
	def set_dewid(self):
		dewid = hashlib.md5()
		
		poll_item_hash = ''
	
		for poll in self.poll_items:
			poll_item_hash += poll.choice
		dewid.update(poll_item_hash)
		dewid.update(self.title)
		dewid.update(str(self.sponsor_name))
		dewid.update(self.start_date.ctime())
		dewid.update(self.end_date.ctime())
		dewid.update(str(self.office))
		dewid.update(str(self.region_id))
		dewid.update(str(self.poll_class))
		dewid.update(str(self.party))
		dewid.update(str(self.sample))
		dewid.update(str(self.screen))
		dewid.update(str(self.method))
		dewid.update(str(self.margin_of_error))
		
		if not dewid.hexdigest()[0:6]:
			self.set_dewid()

		self.dewid = 'dewid-' + dewid.hexdigest()[0:6]
	
	def __str__(self):
		return (str(self.sponsor_name) + " " + self.title + " " + "\n" + self.dewid + "\n" + "[" + str(self.poll_class) + "]" + "\n") 
		

class PollItem(db.Model):
	
	__tablename__ = 'poll_item'

	id = db.Column(db.Integer, primary_key = True)

	politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'))
	political_poll_id = db.Column(db.Integer, db.ForeignKey('political_poll.id'))
	
	party = db.Column(db.String(20))
	value = db.Column(db.Float)
	
	office = db.Column(db.String(40))
	region_id = db.Column(db.Integer, db.ForeignKey('region.id'))	

	poll_class = db.Column(db.String(40))
	other = db.Column(db.Boolean, default = False)
	
	choice = db.Column(db.String(50))	

	poll_date_str = db.Column(db.String(80))
	poll_date = db.Column(db.DateTime)

	
class Pollster(db.Model):
	__tablename__ = 'political_pollster'
	
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(120))
	party = db.Column(db.String(20))
	
	sponsor = db.relationship('PoliticalPoll', backref='poll_sponsor')	
	
	def __str__(self):
		return self.name	
	
class Region(db.Model):
	
	__tablename__ = 'region'

	id = db.Column(db.Integer, primary_key=True)
	national = db.Column(db.Boolean, default = False)
	name = db.Column(db.String(48))
	abv = db.Column(db.String(3))
		
	poll_items = db.relationship('PollItem', backref = 'region')
	polls = db.relationship('PoliticalPoll', backref = 'region')
	poll_survey_list = db.relationship('PoliticalSurvey', backref = 'region')
	election_summaries = db.relationship('ElectionSummary', backref = 'region')
	candidate_summaries = db.relationship('CandidateSummary', backref = 'region')

	def __str__(self):
		if self.national:
			return "National"
		else:
			return self.name
def get_or_create(session, model, defaults={}, **kwargs):
        query = session.query(model).filter_by(**kwargs)

        instance = query.first()

        if instance:
            return instance, False
        else:
            #session.begin(nested=True)
            try:
                params = dict((k, v) for k, v in kwargs.iteritems() if not isinstance(v, ClauseElement))
                params.update(defaults)
                instance = model(**params)

                session.add(instance)
                #session.commit()

                return instance, True
            except IntegrityError as e:
                #session.rollback()
                instance = query.one()

                return instance, False
def generate_presidential_snapshot(session, region, force_new = False):
	if not region:
		summary_region = Region.query.filter_by(abv='US').first()
	else:
		summary_region = region

	average_gop_list = None
	average_dem_list = None

	gop_new_summary = ElectionSummary(session = session, region = summary_region, election = 'president', party = 'gop', snapshot_date = datetime.today().date())
	dem_new_summary = ElectionSummary(session = session, region = summary_region, election = 'president', party = 'dem', snapshot_date = datetime.today().date())
	
	session.add(gop_new_summary)
	session.add(dem_new_summary) 
	
	session.commit()
	
	average_gop_list = gop_new_summary.output_snapshot()
	average_dem_list = dem_new_summary.output_snapshot()
	

	
	return {'average_gop_list' : average_gop_list,  'average_dem_list' : average_dem_list}




class PollUpdateReport(db.Model):
	__tablename__ = 'poll_update_report'

	id = db.Column(db.Integer, primary_key=True)
	update_time = db.Column(db.DateTime)
	
	poll_update_success = db.Column(db.Boolean)
	poll_summary_success = db.Column(db.Boolean)
	
	total_poll_count = db.Column(db.Integer)
	new_poll_count = db.Column(db.Integer)
	excluded_poll_count = db.Column(db.Integer)
	
	def __init__(self):
		self.success = False
		self.update_time = datetime.now()
	def update_complete(self, total_poll_count, new_poll_count, excluded_poll_count):
		self.poll_update_success = True
		self.total_poll_count = total_poll_count
		self.new_poll_count = new_poll_count
		self.excluded_poll_count = excluded_poll_count
		
	def summary_complete(self):
		self.poll_summary_success = True
		
	
admin = Admin(app, 'Simple Models')

# Add views
admin.register(CandidateSummary, session=db.session)
admin.register(PoliticalSurvey, session=db.session)
admin.register(ElectionSummary, session=db.session)
admin.register(PoliticalPoll, session=db.session)
admin.register(PollItem, session=db.session)
admin.register(Politician, session=db.session)
admin.register(Pollster, session=db.session)

db.create_all()