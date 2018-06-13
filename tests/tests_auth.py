import unittest
import json
from app import create_app
from app.models import db


class UserAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        with self.app.app_context():

            db.drop_all()
            db.create_all()

        user = {"email": "mbuguamike@gmail.com", "password": "qwerty12345",
                "role": "admin"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.token = json.loads(response.data.decode())['token']
        self.headers = {'Content-Type': 'application/json',
                        'token': self.token}

    def test_register_user_email_isnot_null(self):
        user = {"email": None, "password": "password",
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_register_user_password_isnot_null(self):
        user = {"email": "michyjones@gmail.com", "password": None,
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_register_user_role_can_only_be_admin_or_user(self):
        user = {"email": "admin@gmail.com", "password": "qwerty123",
                "role": "manager"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_register_password_more_than_8_character(self):
        user = {"email": "michyjones@gmail.com", "password": "rwyeue",
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")

        self.assertEqual(response.status_code, 400)

    def test_register_user_exist(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty12345",
                "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_register_user(self):
        user = {"email": "michyjone@gmail.com", "password": "qwerty12345",
                "role": "user"}

        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 201)

    def test_login_user(self):

        user = {"email": "peterjohn@gmail.com",
                "password": "qwerty12345", "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        user = {"email": "peterjohn@gmail.com", "password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_login_user_invalid_credentials(self):
        user = {"email": "nevermind@gmail.com",
                "password": "qwerty122345", "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        user = {"email": "admin@gmail.com", "password": "asdfghsg"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_login_user_email_is_not_null(self):
        user = {"email": None, "password": "password",
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/login", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_login_user_password_is_not_null(self):
        user = {"email": "michyjones@gmail.com", "password": None,
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/login", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_logout(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty122345"}
        response = self.client.post(
            "/api/v2/auth/logout", data=user, headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_logout_when_tokenexpired(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty122345"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_change_password(self):
        user = {"email": "michyjones@gmail.com",
                "password": "qwerty122345", "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        user = {"email": "michyjones@gmail.com", "password": "newpass12345"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_change_password_without_oldpass(self):
        user = {"email": "michyjones5@gmail.com",
                "password": "qwerty122345"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        user2 = {"email": "michyjones5@gmail.com",
                 "password": "", "new_password": "1234567qwerty"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user2),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
