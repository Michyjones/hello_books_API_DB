import unittest
import json
from app import create_app
from app.models import db, User


class Userbooks(unittest.TestCase):
    def setUp(self):
        self.app = create_app(config_name="testing")
        self.client = self.app.test_client()
        with self.app.app_context():

            db.create_all()
            admin = User(first_name="jones",
                         last_name="michy",
                         address="123nai",
                         email="admin@gmail.com",
                         password="qwerty12345",
                         IsAdmin=True)
            admin.save()
        # Login admin
        user = {"email": "admin@gmail.com", "password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(user),
            content_type="application/json")

        self.token = json.loads(response.data.decode())['token']
        self.headers = {'Content-Type': 'application/json', 'Authorization':
                        'Bearer {}'.format(self.token)
                        }

        # Login a normal user
        normal_user = {"first_name": "jones", "last_name": "michy",
                       "address": "123 Nairobi", "email": "mike.gitau92@gmail.com",
                       "password": "qwerty12345", "confirm_password": "qwerty12345"}
        self.client.post(
            "/api/v2/auth/register", data=json.dumps(normal_user),
            content_type="application/json")
        n_user = {"email": "mike.gitau92@gmail.com",
                  "password": "qwerty12345"}
        response = self.client.post(
            "/api/v2/auth/login", data=json.dumps(n_user),
            content_type="application/json")
        self.token_1 = json.loads(response.data.decode())['token']
        self.headers_1 = {'Content-Type': 'application/json', 'Authorization':
                          'Bearer {}'.format(self.token_1)
                          }

    def test_upgrade_user(self):
        user = {"email": "mike.gitau92@gmail.com"}
        response = self.client.put(
            "/api/v2/auth/register", data=json.dumps(user),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "User upgraded to admin")
        response = self.client.put(
            "/api/v2/auth/register", data=json.dumps(user),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "admin downgraded to user")

    def test_upgrade_and_downgrade_user_as_normal_user(self):
        user = {"email": "mike.gitau92@gmail.com"}
        response = self.client.put(
            "/api/v2/auth/register", data=json.dumps(user),
            headers=self.headers_1)
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are not Authorized !!!")

    # def test_downgrade_admin(self):
    #     user = {"email": "mike.gitau92@gmail.com"}
    #     response = self.client.put(
    #         "/api/v2/auth/register", data=json.dumps(user),
    #         headers=self.headers)
    #     self.assertEqual(response.status_code, 200)
    #     print(response.data)
    #     output = json.loads(response.data)
    #     self.assertEqual(output['Message'],
    #                      "admin downgraded to user")

    def test_create_book(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        output = json.loads(response.data)
        self.assertEqual(output['message'],
                         "Book Added successfully")

    def test_create_book_as_normal_user(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers_1)
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are not Authorized !!!")

    def test_create_book_without_book_name(self):
        book = {'serialno': "002", "book_name": "",
                "category": "Engineering"}
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['error'],
                         "Enter Book name")

    def test_create_book_without_category(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": ""}
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['error'],
                         "Enter Category")

    def test_create_an_existing_book(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        response = self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 409)
        output = json.loads(response.data)
        self.assertEqual(output['message'],
                         'Book  already exist')

    def test_update_a_book(self):
        book = {"serialno": "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)

        book = {"book_name": "flask", "category": "software"}
        response = self.client.put(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 201)
        output = json.loads(response.data)
        self.assertEqual(output['message'],
                         "Edit successfully")

    def test_update_book_as_normal_user(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        book = {"book_name": "flask", "category": "software"}
        response = self.client.put(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers_1)
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are not Authorized !!!")

    def test_update_non_existing_book(self):
        book = {"serialno": "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        response = self.client.put(
            "/api/v2/books/5", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "No book with that id")

    def test_delete_a_book(self):
        book = {"serialno": "002", "book_name":
                "Introduction to programming",
                "category": "Engineering"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.delete(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "delete successful")

    def test_delete_book_as_normal_user(self):
        book = {'serialno': "002", "book_name": "Introductionto flask",
                "category": "Engineering"}
        self.client.post(
            "/api/v2/books", data=json.dumps(book), headers=self.headers)
        response = self.client.delete(
            "/api/v2/books/1", data=json.dumps(book), headers=self.headers_1)
        self.assertEqual(response.status_code, 401)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You are not Authorized !!!")

    def test_delete_non_existing_book(self):
        book = {"serialno": "002", "book_name":
                "Introduction to programming",
                "category": "Engineering"}
        response = self.client.delete(
            "/api/v2/books/4", data=json.dumps(book), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['error'],
                         "Book does not exist.")

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

    def test_get_a_book_with_invalid_id(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books/e", data=json.dumps(books), headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Use a valid book Id")

    def test_book_pagination(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books?page=1", data=json.dumps(books),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def test_pagination_no_available_book_on_a_page(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"}
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books?page=2", data=json.dumps(books),
            headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['error'],
                         "You have no book on this page")

    def test_get_unavailable_book(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=books,
                         headers=self.headers)
        response = self.client.get(
            "/api/v2/books/9", data=books, headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['Error'],
                         "No book with that id")

    def test_borrow_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You have borrowed a book with id 1")

    def test_borrow_book_with_invalid_id(self):
        books = {"serialno": "002", "book_name":
                 "Introduction to programming",
                 "category": "Engineering"
                 }
        self.client.post("/api/v2/books", data=json.dumps(books),
                         headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/we", data=json.dumps(books),
            headers=self.headers)
        self.assertEqual(response.status_code, 404)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "Invalid book ID")

    def test_return_a_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        response = self.client.put(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "You have Returned a book with id 1")

    def test_return_non_existing_book(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        response = self.client.put(
            "/api/v2/users/books/3", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "No book with that id")

    def test_get_borrowed_book(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
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
        output = json.loads(response.data)
        self.assertEqual(output['Message'],
                         "The book is not available at the moment")

    def test_borrow_unexisting_book(self):
        book = {"serialno": "002", "bookname": "Introduction to flask",
                "category": "software"}
        self.client.post("/api/v2/books", data=book,
                         headers=self.headers)
        response = self.client.post(
            "/api/v2/users/books/6", data=book,
            headers=self.headers)
        self.assertEqual(response.status_code, 400)
        output = json.loads(response.data)
        self.assertEqual(output['Message'], "No book with that id")

    def test_borrowed_history_where_return_is_false(self):
        book = {"serialno": "002", "bookname": "Introduction to programming"}
        self.client.post("/api/v2/books", data=json.dumps(book),
                         headers=self.headers)
        self.client.post(
            "/api/v2/users/books/1", data=json.dumps(book),
            headers=self.headers)
        response = self.client.get(
            "/api/v2/users/books?return=false", data=json.dumps(book),
            headers=self.headers)
        self.assertEqual(response.status_code, 200)

    def tearDown(self):
        with self.app.app_context():
            db.drop_all()
