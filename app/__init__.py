from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy
from config import app_config


db = SQLAlchemy()


def create_app(config_name):
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(app_config[config_name])
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    from app.users.views import user
    app.register_blueprint(user)

    from app.books.views import book
    app.register_blueprint(book)

    @app.errorhandler(404)
    def invalidendpoints(error=None):
        """Method for invalid endpoints."""
        message = {
            'message': 'The url entered is Invalid!!!',
            'URL': 'Not found : ' + request.url
        }
        return jsonify(message), 404

    @app.errorhandler(405)
    def notallowed(error=None):
        """Method for not allowed endpoints."""
        message = {
            'message': 'You are not Allowed to use the Method!!!',
            'URL': 'Not Allowed : ' + request.url}
        return jsonify(message), 405

    @app.errorhandler(400)
    def Badrequest(error=None):
        """Method for not allowed endpoints."""
        message = {
            "Error": "Please make sure you have entered "
            "correct information to proceed"}
        return jsonify(message), 400

    @app.errorhandler(500)
    def Internalservererror(error=None):
        """Method for not allowed endpoints."""
        message = {
            "Error": "Enter Valid information as requested!!"}
        return jsonify(message), 500

    return app
