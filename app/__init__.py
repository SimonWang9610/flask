'''
establish application factory methods
'''
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager
from flask_pagedown import PageDown

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()
pagedown = PageDown()
# initialise Login module
# set the endpoint at /auth
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)
    login_manager.init_app(app)
    pagedown.init_app(app)

    with app.app_context():
        # attach routes and custom error page here
        from .main import main as main_blueprint
        from .auth import auth as auth_blueprint
        from .api import api as api_blueprint

        app.register_blueprint(main_blueprint)
        app.register_blueprint(auth_blueprint, url_prefix='/auth')
        app.register_blueprint(api_blueprint, url_prefix='/api')
    return app
