import os

class Config:
	SECRET_KEY = os.urandom(24)
	OUTPUT_DIR = os.path.abspath('botnet/output')
	SQLALCHEMY_DATABASE_URI = 'sqlite:///database.db'
	SQLALCHEMY_TRACK_MODIFICATIONS = False