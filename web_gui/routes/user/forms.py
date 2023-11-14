import json
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, EqualTo, ValidationError, InputRequired

from botnet.models import User


class RegistrationForm(FlaskForm):
	username = StringField('Username',
							validators=[InputRequired(), Length(max=16)])
	password = PasswordField('Password',
							validators=[InputRequired(), Length(min=8)])
	confirm_password = PasswordField('Confirm Password',
							validators=[InputRequired(), Length(min=8), EqualTo('password')])
	submit = SubmitField('Sign Up')

	def validate_username(self, username):
		if User.query.filter_by(username=username.data).first():
			raise ValidationError("That username is taken. Please choose a different one.")


class LoginForm(FlaskForm):
	username = StringField('Username',
							validators=[InputRequired(), Length(max=16)])
	password = PasswordField('Password',
							validators=[InputRequired(), Length(min=8)])
	submit = SubmitField('Log In')
 

class ResetPasswordForm(FlaskForm):
	password = PasswordField('New Password',
							validators=[InputRequired(), Length(min=8)])
	confirm_password = PasswordField('Confirm New Password',
							validators=[InputRequired(), Length(min=8), EqualTo('password')])
	submit = SubmitField('Reset Password')

