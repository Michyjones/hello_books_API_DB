from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from functools import wraps
import jwt
import re
import datetime

from app.models import User, db, generate_password_hash, BlacklistedToken

user = Blueprint('user', __name__, url_prefix='/api/v2/auth')
SECRET_KEY = 'thismyprojectmichyjones'


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'token'in request.headers:
            token = request.headers['token']
        if not token:
            return jsonify({"Message": "Token is Missing!!!"})
        try:
            data = jwt.decode(token, SECRET_KEY)
            current_user = User.query.filter_by(email=data['email']).first()
            g.user = current_user
        except:
            return jsonify({"Message": "Invalid Token!!"})

        return f(current_user, **kwargs)

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


class UserLogin(MethodView):
    def post(self):
        """ This method logs in an existing user"""
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')

        person = User.query.filter_by(email=email).first()

        if person and person.verify_password(password):
            token = jwt.encode({"email": person.email,
                                "exp": datetime.datetime.utcnow(
                                ) + datetime.timedelta(minutes=30)},
                               SECRET_KEY)
            return make_response(jsonify({"token": token.decode('UTF-8'),
                                          "message":
                                          "User login successfully"}), 200)
        else:
            return make_response(jsonify({"error":
                                          "Invalid credentials"}), 401)


class ResetPassword(MethodView):
    @token_required
    def post(self):
        """ This Method resets password """
        data = request.get_json()
        old_password = data.get('password')
        new_password = data.get('new_password')
        if not old_password:
            return make_response(jsonify({"Error":
                                          'Please enter your Current '
                                          'password'}), 400)
        if len(new_password) < 8:
            return make_response(jsonify({"Error":
                                          'Password must be more than 8'
                                          'characters'
                                          }), 400)

        person = User.query.filter_by(email=g.user).first()
        if person and person.verify_password(old_password):
            person.password = generate_password_hash(new_password, method='sha256')
            db.session.add(person)
            db.session.commit()
            return make_response(jsonify({"Message":
                                          "Password reset successfully"}), 201)

        else:
            return make_response(jsonify({"error": "Old password mismatch"}))


user.add_url_rule(
    '/register', view_func=UserRegister.as_view(
        'register'), methods=['POST'])

user.add_url_rule(
    '/login', view_func=UserLogin.as_view(
        'login'), methods=['POST'])

user.add_url_rule(
    '/reset-password', view_func=ResetPassword.as_view(
        'reset-password'), methods=['POST'])
