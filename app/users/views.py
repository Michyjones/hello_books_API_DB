from flask import Blueprint, request, make_response, jsonify, g
from flask.views import MethodView
from functools import wraps
from smtplib import SMTP, SMTPException
import jwt
import re
import os
import datetime
import uuid


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


def send_mail(recipient, password):
    print (password)
    """
    This method is used to send an email while resetting the password
    """
    sender = os.getenv('EMAIL')
    pwd = os.getenv('PASSWORD')
    print (sender)
    message = "Your new password is %s" % password
    try:
        server = SMTP("smtp.gmail.com", 587)
        server.ehlo()
        server.starttls()
        server.login(sender, pwd)
        server.sendmail(sender, recipient, message)
        server.close()
        return True

    except SMTPException:
        return False


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
        new_user.save()
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
            BlacklistedToken(token.decode('UTF-8')).save()
            return make_response(jsonify({"token": token.decode('UTF-8'),
                                          "message":
                                          "User login successfully"}), 200)
        else:
            return make_response(jsonify({"error":
                                          "Invalid credentials"}), 401)


class LogoutUser(MethodView):
    @token_required
    def post(self):
        """Logs out the user and add token to blacklist"""
        requests = request.headers['token']
        tokens = BlacklistedToken.query.filter_by(token=requests).first()
        if tokens and tokens.valid is True:
            tokens.valid = False
            tokens.save()
            return make_response(jsonify({'success': 'logged out'}), 200)
        return make_response(jsonify({'message': 'Your session has expired!'}),
                             401)


class ChangePassword(MethodView):
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
        person = User.query.filter_by(email=g.user.email).first()
        if person and person.verify_password(old_password):
            person.password = generate_password_hash(
                new_password, method='sha256')
            person.save()
            return make_response(jsonify({"Message":
                                          "Password reset successfully"}), 200)

        else:
            return make_response(jsonify({"error": "Old password mismatch"}),
                                 400)


class ResetPassword(MethodView):
    def post(self):
        """
        This method is used to reset user's password when forgotten.
        It sends an email with the new auto generated password
        """
        data = request.get_json()
        email = data.get('email')

        if not email:
            return make_response(jsonify({"error": "Please enter your email address"}), 400)

        if not User.exists(email=email):
            return make_response(jsonify({"error": 'Email not found!'}), 400)

        password = str(uuid.uuid4())[:8]

        person = User.query.filter_by(email=email).first()
        alert = send_mail(email, password)

        if not alert:
            return make_response(jsonify({"error": 'Password was not reset.'
                                          ' Please try resetting it again'}),
                                 500)
        person.password = generate_password_hash(
            password, method='sha256')

        person.save()
        return make_response(jsonify({"message": 'An email has been sent with '
                                      'instructions for ''your new password'}), 201)


user.add_url_rule(
    '/register', view_func=UserRegister.as_view(
        'register'), methods=['POST'])

user.add_url_rule(
    '/login', view_func=UserLogin.as_view(
        'login'), methods=['POST'])

user.add_url_rule(
    '/change-password', view_func=ChangePassword.as_view(
        'change-password'), methods=['POST'])

user.add_url_rule(
    '/logout', view_func=LogoutUser.as_view(
        'logout'), methods=['POST'])
user.add_url_rule(
    '/reset-password', view_func=ResetPassword.as_view(
        'reset-password'), methods=['POST'])
