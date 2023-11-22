from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import Length, InputRequired

class LoginForm(FlaskForm):
	username = StringField('Username',
							validators=[InputRequired(), Length(max=16)])
	password = PasswordField('Password',
							validators=[InputRequired(), Length(min=8)])
	submit = SubmitField('Log In')


