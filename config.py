import os

# create absolute path for SQLite database
# PostgreSQL is also allowed in Development environment
basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hardToGuessString'

    SSL_REDIRECT = False
    # configure email server as gmail
    MAIL_SERVER = os.environ.get('MAIL_SERVER', 'smtp.googlemail.com')
    MAIL_PORT = int(os.environ.get('MAIL_PORT', '587'))
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS', 'true').lower() in ['true', 'on', '1']

    # set the confirm email address
    # a confirm link will be sent to the new register via the below email address
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME', 'simon9610.wang@gmail.com')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', 'itec5920w')
    ITEC_MAIL_SUBJECT_PREFIX = '[ITEC5920]'
    ITEC_MAIL_SENDER = 'ITEC Admin <no-reply@gmail.com>'

    # set FLASKY_ADMIN=<your_email> : set default Admin account for the blog on windows
    # if not set, the admin account will be 'dengpan1002.wang@gmail.com'
    # but you still have to register the admin account in the blog to activate it
    ITEC_ADMIN = os.environ.get('ITEC_ADMIN') or 'dengpan1002.wang@gmail.com'
    # configure database
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # set the number of content displayed in one page
    ITEC_POSTS_PER_PAGE = 5
    ITEC_FOLLOWERS_PER_PAGE = 10
    ITEC_COMMENTS_PER_PAGE = 5

    @staticmethod
    def init_app(app):
        pass

class DevelopmentConfig(Config):
    DEBUG = True

    # SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')

    # to use your local setting, postgresql_url must be 'postgresql://<user>:<password>@<host>:<port>/<database_name>'
    # before run the application, ensure <database_name> has been created in your machine
    # <port> is your PostgreSQL port
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'postgresql://postgres:961002@localhost:5432/data'

class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite://'

# configure for deploying the application as production
class ProductionConfig(Config):
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        # email errors to the administrators
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()

        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr= cls.ITEC_MAIL_SENDER,
            toaddrs=[cls.ITEC_ADMIN],
            subject=cls.ITEC_MAIL_SUBJECT_PREFIX + 'Application Error',
            credentials=credentials,
            secure=secure
        )
        # only server problems are going to be emailed once the application is deployed
        # other errors are logged to a file
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

# configure for deploying the application on Heroku
# some server errors will be sent to the admin account
class HerokuConfig(Config):

    SSL_REDIRECT = True if os.environ.get('DYNO') else False
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                             'sqlite:///' + os.path.join(basedir, 'data.sqlite')

    @classmethod
    def init_app(cls, app):
        ProductionConfig.init_app(app)

        import logging
        from logging import StreamHandler

        file_handler = StreamHandler()
        file_handler.setLevel(logging.INFO)
        app.logger.addHandler(file_handler)

        # handle reverse proxy server headers
        from werkzeug.contrib.fixers import ProxyFix
        app.wsgi_app = ProxyFix(app.wsgi_app)



config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig,
    'heroku': HerokuConfig
}

