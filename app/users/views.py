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
        token = request.headers.get("Authorization")
        if not token:
            return jsonify({"Message": "Token is Missing!!!"}, 401)
        blacklist_token = BlacklistedToken.query.filter_by(
            token=token.split()[1], valid=False).first()
        if blacklist_token:
            return make_response(jsonify({"Message": "You are already"
                                          " logged out!!!"}), 400)
        try:
            data = jwt.decode(token[7:], SECRET_KEY)
            current_user = User.query.filter_by(email=data['email']).first()
            g.user = current_user
        except:
            return make_response(jsonify({"Message": "Invalid Token!!"}), 401)

        return f(current_user, **kwargs)
            
    return decorated


def send_mail(recipient, password):
    """
    This method is used to send an email while resetting the password
    """
    sender = os.getenv('EMAIL')
    pwd = os.getenv('PASSWORD')
    message = """Your new password is %s""" % password
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
        first_name = data.get('first_name')
        last_name = data.get('last_name')
        address = data.get('address')
        email = data.get('email')
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        valid_email = re.match(
            "(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)",
            email.strip())
        if first_name.strip() == "":
            return make_response(jsonify(
                {"Message": "Please enter your first name"}), 400)

        if last_name.strip() == "":
            return make_response(jsonify(
                {"Message": "Please enter your last name"}), 400)
        if address.strip() == "":
            return make_response(jsonify(
                {"Message": "Please enter your address"}), 400)

        if valid_email is None:
            return make_response(jsonify(
                {'Error': 'Please enter valid Email!'}), 400)

        if confirm_password.strip() == "":
            return make_response(jsonify({'Error': 'Please confirm your'
                                          ' password'}), 400)

        if len(password.strip()) < 8:

            return make_response(jsonify(
                {'Message': 'Password should be more than 8 character'}), 400)

        person = User.query.filter_by(email=email).first()

        if person:
            return make_response(jsonify({
                "Error": "User already exist"
            }), 409)
        if password == confirm_password:
            new_user = User(first_name=first_name, last_name=last_name,
                            address=address, email=email.strip(),
                            password=password)
            new_user.save()
            return make_response(jsonify({
                "Message": "User created successfully"
            }), 201)
        else:
            return make_response(jsonify({"Error":
                                          "Password mismatch!!!"}), 401)

    @token_required
    def put(self):
        """ This method upgrade and downgrade a user """
        if g.user.IsAdmin is True:
            data = request.get_json()
            email = data.get('email')

            person = User.query.filter_by(email=email).first()
            if person:
                # upgrade user to admin
                if person.IsAdmin is False:
                    person.IsAdmin = True
                    person.save()
                    return make_response(jsonify({"Message":
                                                  "User upgraded to admin"}),
                                         200)

                # downgrade admin to user
                if person.IsAdmin is True:
                    person.IsAdmin = False
                    person.save()
                    return make_response(jsonify({"Message":
                                                  "admin downgraded to user"}),
                                         200)
            else:
                return make_response(jsonify({"Error":
                                              "User not found!!"}), 404)

        else:
            return make_response(jsonify({"Message":
                                          "You are not Authorized !!!"}), 401)


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
                                          "Message":
                                          "User login successfully",
                                          "IsAdmin": person.IsAdmin,
                                          "Email": person.email}), 200)
        else:
            return make_response(jsonify({"Error":
                                          "Invalid credentials"}), 401)


class LogoutUser(MethodView):
    @token_required
    def post(self):
        """Logs out the user and add token to blacklist"""
        header = request.headers['Authorization']
        blacklists = BlacklistedToken.query.filter_by(
            token=header.split()[1]).first()
        if blacklists and blacklists.valid is True:
            blacklisted = BlacklistedToken(
                token=header.split()[1], valid=False)
            db.session.add(blacklisted)
            db.session.commit()
            return make_response(jsonify({'Message': 'You are logged out'}), 200)
        return make_response(jsonify({'Message': "Your session has "
                                      "expired !!"}), 400)


class ChangePassword(MethodView):
    @token_required
    def post(self):
        """ This Method resets password """
        data = request.get_json()
        old_password = data.get('old_password')
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
                                          "Password Changed successfully"}),
                                 200)

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
            return make_response(jsonify({"Error": "Please enter "
                                          "your email address"}), 400)

        if not User.exists(email=email):
            return make_response(jsonify({"Error": "Email not found!"}), 400)

        password = str(uuid.uuid4())[:8]

        person = User.query.filter_by(email=email).first()
        alert = send_mail(email, password)

        if not alert:
            return make_response(jsonify({"Error": "Password was not reset."
                                          " Please try resetting it "
                                          "again later"}), 500)
        person.password = generate_password_hash(
            password, method='sha256')

        person.save()
        return make_response(jsonify({"Message": "A link has been sent to your"
                                      " email with the instructions"}), 200)


user.add_url_rule(
    '/register', view_func=UserRegister.as_view(
        'register'), methods=['POST', 'PUT'])

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
