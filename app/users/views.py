from flask import Blueprint, request, make_response, jsonify
from app.models import User, db

from flask.views import MethodView


user = Blueprint('user', __name__, url_prefix='/api/v2/auth')


class UserRegister(MethodView):

    def post(self):
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        role = data.get('role')

        if email is None:
            return make_response(jsonify(
                {'error': 'Fill in the details'}), 400)

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
