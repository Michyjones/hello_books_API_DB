from flask import Blueprint, request, make_response, jsonify
from flask.views import MethodView
from functools import wraps
import jwt
import re

from app.models import User, db


user = Blueprint('user', __name__, url_prefix='/api/v2/auth')
SECRET_KEY = 'thismyprojectmichyjones'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'x-access-token'in request.headers:
            token = request.headers['x-access-token']
        if not token:
            return jsonify({"message": "Token is Missing!!!"})
        try:
            data = jwt.decode(token, SECRET_KEY)
            current_user = User.query.filter_by(email=data['email']).first()
        except:
            return jsonify({"message": "Invalid Token!!"})
        return f(current_user, *args, **kwargs)

    return decorated


class UserRegister(MethodView):

    def post(self):
        """ This method create a new user"""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')
        valid_email = re.match(
            "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            email.strip())

        if valid_email is None:
            return make_response(jsonify(
                {'error': 'Please enter valid Email!'}), 400)

        if password is None:
            return make_response(jsonify({'error': 'Enter password'}), 400)

        if (role != 'user') and (role != 'admin'):
            return make_response(jsonify(
                {'error': 'Role can only be user or admin'}), 400)

        if len(password) < 8:

            return make_response(jsonify(
                {'message': 'password should be more than 8 character'}), 400)

        person = User.query.filter_by(email=email).first()

        if person:
            return make_response(jsonify({
                "error": "User already exist"
            }))
        new_user = User(email=email, password=password, role=role)
        db.session.add(new_user)
        db.session.commit()
        return make_response(jsonify({
            "message": "user_created successfully"
        }), 201)


user.add_url_rule(
    '/register', view_func=UserRegister.as_view(
        'register'), methods=['POST'])
