from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import app_config


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)
# app = Flask(__name__)
# app.config.from_object(app_config[config_name])
# app.config['SECURITY_RECOVERABLE'] = True
# db.init_app(app)
    from app.users.views import user
    app.register_blueprint(user)

    from app.books.views import book
    app.register_blueprint(book)

    return app
