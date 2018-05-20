from flask.views import MethodView
from flask import Blueprint, request, make_response, jsonify, g, url_for
from urllib.parse import urljoin

from app.models import Book, User, db, Borrow
from app.users.views import token_required


books = {}
borrow = {}
book = Blueprint('book', __name__, url_prefix='/api/v2')


class Books(MethodView):
    @token_required
    def get(self):
        """This method retrieves allbooks """
        page = request.args.get('page')
        limit = request.args.get('limit')

        if page and limit:
            books = Book.query.order_by(Book.bookid).paginate(page=int(page),
                                                              per_page=int(
                                                                  limit),
                                                              error_out=False)

            all_books, next_url, prev_url = [], None, None

            if books:
                for book in books.items:
                    all_books.append({
                        "bookid": book.bookid,
                        "book_name": book.book_name,
                        "category": book.category,
                        "availabilty": book.availabilty
                    })

                if books.has_next:
                    next_url = urljoin("http://localhost:5000/",
                                       "/v2/books"), url_for(
                        "book.books",
                        page=books.next_num,
                        limit=books.per_page)

                if books.has_prev:
                    prev_url = (urljoin("http://localhost:5000/",
                                        "/v2/books"), url_for(
                        "book.books",
                        page=books.prev_num,
                        limit=books.per_page))

                if all_books:
                    page_details = {
                        "start": books.page,
                        "limit": limit,
                        "next_page": next_url,
                        "prev_page": prev_url,
                        "books": all_books
                    }
                    return make_response(jsonify(page_details), 200)
                else:
                    return make_response(jsonify({"error":
                                                  "You have no book on this page"}), 404)

        else:
            return make_response(jsonify({"error":
                                          "Indicate page number and page limit"}), 404)

    @token_required
    def post(self):
        """This method add a book"""
        if g.user.role == "admin":
            data = request.get_json()
            bookid = data.get('bookid')
            book_name = data.get('book_name')
            category = data.get('category')

            current_user = User.query.filter_by(role='admin')
            if current_user:
                if bookid == '':
                    return make_response(jsonify(
                        {"error": "Enter Book id"}), 400)

                if book_name == '':
                    return make_response(jsonify(
                        {"error": "Enter Book name"}), 400)
                if category == '':
                    return make_response(jsonify(
                        {"error": "Enter Category"}), 400)
                book = Book.query.filter_by(bookid=bookid).first()

                if book:
                    return make_response(jsonify(
                        {'message': 'Book  already exist'}), 409)

                book = Book(bookid=bookid, book_name=book_name,
                            category=category)
                db.session.add(book)
                db.session.commit()
                return make_response(jsonify(
                    {"message": "Book Added successfully"
                     }), 201)
        else:
            return make_response(jsonify({"Message":
                                          "You are not Authorized !!!"}), 401)


class GetBook(MethodView):
    @token_required
    def get(self, bookid):
        """ This method gets a single book"""
        book = Book.query.filter_by(bookid=bookid).first()
        if book:
            one_book = []
            one_book.append({
                "bookid": book.bookid,
                "book_name": book.book_name,
                "category": book.category,
                "availabilty": book.availabilty
            })
            return make_response(jsonify(one_book), 200)

        else:
            return make_response(jsonify({
                "Error": "No book with that id"}), 400)


class EditBook(MethodView):
    @token_required
    def put(self, bookid):
        """ This Method edits book"""
        if g.user.role == "admin":
            data = request.get_json()
            book_name = data.get('book_name')
            category = data.get('category')

            book = Book.query.filter_by(bookid=bookid).first()

            if book:

                book.book_name = book_name
                book.category = category
                book.availabilty = True
                db.session.add(book)
                db.session.commit()
                return make_response(jsonify(
                    {"message": "Edit successfully"
                     }), 201)
            else:
                return make_response(jsonify("No book with that id"), 404)
        else:
            return make_response(jsonify({"Message":
                                          "You are not Authorized !!!"}), 401)


class DeleteBook(MethodView):
    @token_required
    def delete(self, bookid):
        """This method delete book"""
        if g.user.role == "admin":

            book = Book.query.filter_by(bookid=bookid).first()
            if book:
                db.session.delete(book)
                db.session.commit()

                return make_response(jsonify({
                    "Message": "delete successful"}), 204)
            else:
                return make_response(jsonify({
                    "error": "Book does not exist."}), 404)
        else:
            return make_response(jsonify({"Message":
                                          "You are not Authorized !!!"}), 401)


class BorrowBook(MethodView):
    @token_required
    def get(self):
        """This method shows borrowed books history """
        # query borrowing history by returned is false
        returned = request.args.get('returned')
        if returned:
            borrows = Borrow.query.filter_by(
                returned=False, user_email=g.user.email)
            print(borrows)
            borrowed = []
            for borrow_book in borrows:
                borrowed.append({
                    "id": borrow_book.id,
                    "user_email": borrow_book.user_email,
                    "bookid": borrow_book.bookid,
                    "date_borrowed": borrow_book.date_borrowed,
                    "date_returned": borrow_book.date_returned,
                    "returned": borrow_book.returned
                })
            return make_response(jsonify(borrowed), 200)

        # get borrowing history with pages and limit
        borrows = Borrow.query.filter_by(user_email=g.user.email)
        borrowed = []
        for borrow_book in borrows:
            borrowed.append({
                "id": borrow_book.id,
                "user_email": borrow_book.user_email,
                "bookid": borrow_book.bookid,
                "date_borrowed": borrow_book.date_borrowed,
                "date_returned": borrow_book.date_returned,
                "returned": borrow_book.returned
            })
        return make_response(jsonify(borrowed), 200)

    @token_required
    def post(self, bookid):
        """ This method borrows a single book"""
        book = Book.query.filter_by(bookid=bookid).first()
        if book:
            if book.availabilty is True:
                borrow_book = Borrow(
                    user_email=g.user.email, bookid=bookid, returned=False)
                book.availabilty = False
                db.session.add(borrow_book)
                db.session.commit()
                return make_response(jsonify({"Message": "You have borrowed "
                                              "a book with id {}".format(bookid
                                                                         )}), 200)

            else:
                return make_response(jsonify({"Message":
                                              "The book is not available at "
                                              "the moment"}), 400)
        else:
            return make_response(jsonify({"Message": "No book with that id"}), 400)


class ReturnBook(MethodView):
    @token_required
    def put(self, bookid):
        """ This method Returns a single book"""
        book = Book.query.filter_by(bookid=bookid).first()
        return_book = Borrow.query.filter_by(bookid=book.bookid).first()

        if book:
            if book.availabilty is False and \
                    return_book.user_email == g.user.email:
                book.availabilty = True
                return_book.returned = True
                db.session.add(return_book)
                db.session.commit()
                return make_response(jsonify({"Message": "You have Returned "
                                              "a book with id {}".format(bookid
                                                                         )}), 200)

            else:
                return make_response(jsonify({"Message": "You have Not "
                                              "borrowed book with that id"}), 400)
        else:
            return make_response(jsonify({"Message": "No book with that id"}), 400)


book.add_url_rule(
    '/books', view_func=Books.as_view(
        'books'), methods=['GET', 'POST'])

book.add_url_rule(
    '/books/<bookid>', view_func=GetBook.as_view(
        'getbook'), methods=['GET'])

book.add_url_rule(
    '/books/<bookid>', view_func=EditBook.as_view(
        'editbook'), methods=['PUT'])

book.add_url_rule(
    '/books/<bookid>', view_func=DeleteBook.as_view(
        'deletebook'), methods=['DELETE'])

book.add_url_rule(
    '/users/books', view_func=BorrowBook.as_view(
        'borrowhistory'), methods=['GET'])

book.add_url_rule(
    '/users/books/<bookid>', view_func=BorrowBook.as_view(
        'borrowbook'), methods=['POST'])

book.add_url_rule(
    '/users/books/<bookid>', view_func=ReturnBook.as_view(
        'returnbook'), methods=['PUT'])
