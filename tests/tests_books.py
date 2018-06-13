import unittest
import json
from app import create_app
from app.models import db, User


class Userbooks(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        with self.app.app_context():

            # db.drop_all()
            db.create_all()
            admin = User(email="admin@gmail.com",
                         password="qwerty12345", IsAdmin=True)
            admin.save()
        user = {"email": "admin@gmail.com", "password": "qwerty12345"}
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

    def test_create_book(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_update_a_book(self):
        book = {"serialno": "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)

        book = {"book_name": "flask", "category": "software"}
        response = self.client.put(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 201)

    def test_update_unexisting_book(self):
        book = {"serialno": "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)

        book = {"book_name": "flask", "category": "software"}
        response = self.client.put(
            "/api/v2/books/5", data=json.dumps(book), headers=self.headers)

        self.assertEqual(response.status_code, 404)

    def test_delete_a_book(self):
        book = {"serialno": "002", "book_name":
                "Introduction to programming",
                "category": "Engineering"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.delete(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_delete_unexisting_book(self):
        book = {"serialno": "002", "book_name":
                "Introduction to programming",
                "category": "Engineering"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.delete(
            "/api/v2/books/4", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 404)

    def test_get_a_book(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books/1", data=json.dumps(books), headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_all_book(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books", data=json.dumps(books), headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_get_book_with_invalid_id(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=books,
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books/9", data=books, headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_borrow_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        r = self.client.post("/api/v2/books", data=json.dumps(book),
                             headers=self.headers)
        print(r.data)
        response = self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        print(response.data)
        self.assertEqual(response.status_code, 200)

    def test_return_a_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        response = self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_return_unborrowed_book(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/3", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_get_borrowed_book(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/users/books", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_borrow_borrowed_book(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)

        self.assertEqual(response.status_code, 400)

    def test_borrow_unexisting_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=book,
                         headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/6", data=book,
            headers=self.headers)
        self.assertEqual(response.status_code, 400)

    def test_borrowed_history(self):
        book = {"serialno": "002", "bookname": "Introduction to programming",
                "serialno": "004", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/users/books", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
