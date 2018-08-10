import os


class BaseConfig(object):
    DEBUG = False
    TESTING = False


    SECURITY_PASSWORD_SALT = 'poiuytrewq987654321'
    MAIL_SERVER = 'smtp.googlemail.com'
    MAIL_PORT = 465
    MAIL_USE_TLS = False
    MAIL_USE_SSL = True
    MAIL_USERNAME = os.environ.get('Username')
    MAIL_DEFAULT_SENDER = os.environ.get('Email')
    MAIL_PASSWORD = os.environ.get('Password')

class DevelopmentConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL')


class TestingConfig(BaseConfig):
    DEBUG = False
    TESTING = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:password@localhost:5432/tests'


class StagingConfig(BaseConfig):
    DEBUG = True


class ProductionConfig(BaseConfig):
    DEBUG = False
    TESTING = False


app_config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'staging': StagingConfig,
    'production': ProductionConfig
}

