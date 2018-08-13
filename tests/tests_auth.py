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

        self.user = {"first_name": "jones", "last_name": "michy",
                     "address": "123 Nairobi",
                     "email": "mike.gitau92@gmail.com",
                     "password": "qwerty12345",
                     "confirm_password": "qwerty12345"}
        self.response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(self.user),
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(self.user),
            content_type="application/json")
        self.token = json.loads(response.data.decode())['token']
        self.headers = {'Content-Type': 'application/json', 'Authorization':
                        'Bearer {}'.format(self.token)
                        }

    # This tests registering a user without an email address
    def test_register_with_null_email(self):
        user = {"first_name": "jones", "last_name": "michy",
                "address": "123 Nairobi", "email": None,
                "password": "qwerty12345", "confirm_password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # This tests registering a user with password less than 8 character
    def test_register_password_is_less_than_8_character(self):
        user = {"first_name": "jones", "last_name": "michy",
                "address": "123 Nairobi", "email": "mike.gitau92@gmail.com",
                "password": "qwerty1", "confirm_password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Password should be more than 8 character")

    # This tests registering a user without the first name
    def test_register_with_null_first_name(self):
        user = {"first_name": "", "last_name": "michy",
                "address": "123 Nai", "email": "mike.gitau92@gmail.com",
                "password": "qwerty1", "confirm_password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Please enter your first name")

    # This tests registering a user without the last name
    def test_register_with_null_last_name(self):
        user = {"first_name": "jones", "last_name": "",
                "address": "123 Nai", "email": "mike.gitau92@gmail.com",
                "password": "qwerty1", "confirm_password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Please enter your last name")

    # This tests registering a user without the address
    def test_register_with_null_address(self):
        user = {"first_name": "jones", "last_name": "michy",
                "address": "", "email": "mike.gitau92@gmail.com",
                "password": "qwerty1", "confirm_password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Please enter your address")

    # This tests registering a user without confirming the password
    def test_register_with_null_confirm_password(self):
        user = {"first_name": "jones", "last_name": "michy",
                "address": "123 Nai", "email": "mike.gitau92@gmail.com",
                "password": "qwerty1", "confirm_password": ""}
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please confirm your password")

    # This tests successful registration of a user in the library
    def test_register_user(self):
        self.assertEqual(self.response.status_code, 201)
        output = json.loads(self.response.data)
        self.assertEqual(output['Message'],
                         "User created successfully")

    # This tests registering already existing user in the library
    def test_register_user_exists(self):
        response = self.client.post(
            "/api/v2/auth/register", data=json.dumps(self.user),
            content_type="application/json")

        self.assertEqual(response.status_code, 409)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "User already exist")

    # This tests logging in with valid email or password
    def test_login_user(self):
        user = {"email": "mike.gitau92@gmail.com", "password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")

        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "User login successfully")

    # This tests logging in with invalid email or password
    def test_login_with_invalid_credentials(self):
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(self.user),
            content_type="application/json")
        user = {"email": "admin@gmail.com", "password": "asdfghsg"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Invalid credentials")

    # This tests logging in without the email
    def test_login_with_null_email(self):
        user = {"email": None, "password": "password1234"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 401)

    # This tests logging in without the password
    def test_login_with_null_password(self):
        user = {"email": "michyjones@gmail.com", "password": None,
                "role": "user"}
        response = self.client.post(
            "/api/v2/auth/login", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    # This tests logging out from the library application
    def test_logout(self):
        user = {"email": "michyjones@gmail.com", "password": "qwerty122345"}
        response = self.client.post(
            "/api/v2/auth/logout", data=user, headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are logged out")

    # This tests logging out when the token expires
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

    # This tests changing password withcorect details
    def test_change_password(self):
        user = {"email": "mbuguamike@gmail.com",
                "old_password": "qwerty12345", "new_password": "password12345",
                "confirm_password": "password12345"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Password Changed successfully")

    # This tests changing password without the current password
    def test_change_password_without_oldpass(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "old_password": "", "new_password": "1234567",
                 "confirm_password": "1234567"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please enter your Current password")

    # This tests changing password with mismatch old password
    def test_change_password_with_incorrect_oldpass(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "old_password": "qwerty12345789",
                 "new_password": "1234567qwerty",
                 "confirm_password": "1234567qwerty"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Old password mismatch")

    # This tests changing password with mismatch new and confirm password
    def test_change_password_with_incorrect_confirm_password(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "old_password": "qwerty12345",
                 "new_password": "1234567qwerty",
                 "confirm_password": "1234567gfhj"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Password mismatch")

    # This tests trying to change password with less than required length
    def test_change_password_with_less_than_8_characters(self):
        user1 = {"email": "mbuguamike@gmail.com",
                 "old_password": "qwerty12345", "new_password": "123",
                 "confirm_password": "123"}
        response = self.client.post(
            "/api/v2/auth/change-password", data=json.dumps(user1),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Password must be more than 8 characters")

    # This tests trying to reset password without an email
    def test_reset_password_without_email(self):
        user = {"email": None}
        response = self.client.post(
            "/api/v2/auth/reset-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Please enter your email address")

    # This tests trying to reset password if you are unregistered user
    def test_reset_password_with_non_email(self):
        user = {"email": "worldcupishere@gmail.com"}
        response = self.client.post(
            "/api/v2/auth/reset-password", data=json.dumps(user),
            content_type="application/json")
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "Email not found!")

    # # This tests reset password by sending password to the mail
    # def test_reset_password(self):
    #     user = {"email": "mike.gitau92@gmail.com"}
    #     response = self.client.post(
    #         "/api/v2/auth/reset-password", data=json.dumps(user),
    #         content_type="application/json")
    #     self.assertEqual(response.status_code, 200)
    #     output = json.loads(response.data)
    #     self.assertEqual(output['Message'],
    #                      "A link has been sent to your email with "
    #                      "the instructions")

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
