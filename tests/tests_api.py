import unittest
import run
from app import create_app
from app.models import db


class UserAuthentication(unittest.TestCase):

    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = run.app.test_client()
        with self.app.app_context():
            db.drop_all()
            db.create_all()

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
        print(response.data)
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
        user = {"email": "michyjones@gmail.com", "password": "password",
                "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")

        self.assertEqual(response.status_code, 409)

    def test_register_user(self):
        user = {"email": "michyjone@gmail.com", "password": "qwerty12345",
                "role": "user"}

        response = self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")

        self.assertEqual(response.status_code, 201)

    def test_login_user(self):

        user = {"email": "michyjones@gmail.com",
                "password": "password", "role": "user"}
        self.client.post(
            "/api/v1/auth/register", data=user,
            content_type="application/json")
        user = {"email": "michyjones@gmail.com", "password": "password"}
        response = self.client.post(
            "/api/v2/auth/login", data=user,
            content_type="application/json")

        self.assertEqual(response.status_code, 200)

    def test_login_user_invalid_credentials(self):
        user = {"email": "michy@gmail.com",
                "password": "password", "role": "user"}
        self.client.post(
            "/api/v2/auth/register", data=user,
            content_type="application/json")
        user = {"email": "admin@gmail.com", "password": "asdfghsg"}
        response = self.client.post(
            "/api/v2/auth/login", data=user,
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
            "/api/v1/auth/login", data=user,
            content_type="application/json")
        self.assertEqual(response.status_code, 400)

    def test_admin_create_book(self):
        book = {"bookid": "007", "book_name": "Introductionto flask",
                "category": "Engineering"}
        response = self.client.post(
            "/api/v2/books", data=book, content_type="application/json")
        print(response.data)
        self.assertEqual(response.status_code, 201)

    def test_admin_updates_a_book(self):
        book = {"bookid": "004", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=book, content_type="application/json")
        book = {"book_name": "flask", "category": "software"}
        response = self.client.put(
            "/api/v2/books/004", data=book, content_type="application/json")
        print(response.data)

        self.assertEqual(response.status_code, 201)

    def test_admin_delete_a_book(self):
        book = {"bookid": "002", "book_name":
                "Introduction to programming",
                "category": "Engineering"}
        self.client.post("/api/v1/books", data=book,
                         content_type="application/json")
        response = self.client.delete(
            "/api/v2/books/002", data=book, content_type="application/json")
        print(response.data)
        self.assertEqual(response.status_code, 204)

    def test_can_get_all_books(self):
        books = {"bookid": "001", "bookname": "Introductionto bootstrap",
                 "bookid": "002", "bookname": "Introduction to programming",
                 "bookid": "003", "bookname": "Introduction to javascript",
                 "bookid": "004", "bookname": "Introduction to flask",
                 "bookid": "005", "bookname": "Web development"}
        response = self.client.get(
            "/api/v2/books", data=books, content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_user_can_borrow_book(self):
        book = {"bookid": "004", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v1/books", data=book,
                         content_type="application/json")
        response = self.client.post(
            "/api/v2/users/books/004", data=book,
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def test_user_can_get_a_book(self):
        book = {"bookid": "002", "bookname": "Introduction to programming"}
        response = self.client.get(
            "/api/v2/books/<bookid>", data=book,
            content_type="application/json")
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        self.client = None