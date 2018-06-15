import unittest
import json
from app import create_app
from app.models import db


class UserAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        with self.app.app_context():

            db.create_all()

        user = {"email": "mbuguamike@gmail.com", "password": "qwerty12345"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.token = json.loads(response.data.decode())['token']
        self.headers = {'Content-Type': 'application/json', 'Authorization':
                        'Bearer {}'.format(self.token)
                        }

    def test_register_with_null_email(self):
        user = {"email": None, "password": "password"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_register_with_null_password(self):
        user = {"email": "michyjones@gmail.com", "password": None}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please enter your password")

    def test_register_password_is_less_than_8_character(self):
        user = {"email": "michyjones@gmail.com", "password": "rwyeue"}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Password should be more than 8 character")

    def test_register_user(self):
        user = {"email": "michyjone@gmail.com", "password": "qwerty12345",
                "role": "user"}

        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 201)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "User created successfully")

    def test_register_user_exists(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty12345"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 409)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "User already exist")

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
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "User login successfully")

    def test_login_with_invalid_credentials(self):
        user = {"email": "nevermind@gmail.com",
                "password": "qwerty122345"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        user = {"email": "admin@gmail.com", "password": "asdfghsg"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Invalid credentials")

    def test_login_with_null_email(self):
        user = {"email": None, "password": "password1234"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)

    def test_login_with_null_password(self):
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
        output = json.loads(response.data)
        self.assertEqual(output['Msg'],
                         "You are logged out")

    def test_logout_when_tokenexpired(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty122345"}
        self.client.post(
            "/api/v2/auth/logout", data=json.dumps(user), headers=self.headers)
        response = self.client.post(
            "/api/v2/auth/logout", data=json.dumps(user),
            content_type="application/json", headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are already logged out!!!")

    def test_change_password(self):
        user = {"email": "mbuguamike@gmail.com",
                "password": "qwerty12345", "new_password": "password12345"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Password Changed successfully")

    def test_change_password_without_oldpass(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "password": "", "new_password": "1234567qwerty"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please enter your Current password")

    def test_change_password_with_incorrect_oldpass(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "password": "asdfghrty", "new_password": "1234567qwerty"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['error'],
                         "Old password mismatch")

    def test_change_password_with_less_than_8_characters(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "password": "qwerty12345", "new_password": "123"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Password must be more than 8characters")

    def test_reset_password_without_email(self):
        user = {"email": None}
        response = self.client.post(
            "/api/v2/auth/reset-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please enter your email address")

    def test_reset_password_with_non_email(self):
        user = {"email": "worldcupishere@gmail.com"}
        response = self.client.post(
            "/api/v2/auth/reset-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Email not found!")

    def test_reset_password(self):
        user = {"email": "mbuguamike@gmail.com"}
        response = self.client.post(
            "/api/v2/auth/reset-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "A link has been sent to your email with "
                         "the instructions")

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
