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
        page = request.args.get('page', default=1, type=int)
        limit = request.args.get('limit', default=3, type=int)

        if page and limit:
            books = Book.query.order_by(Book.id).paginate(page=int(page),
                                                          per_page=int(
                limit),
                error_out=False)

            all_books, next_url, prev_url = [], None, None

            if books:
                for book in books.items:
                    all_books.append({
                        "id": book.id,
                        "serial_no": book.serial_no,
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

                                                  "You have no book on "
                                                  "this page"}), 404)

    @token_required
    def post(self):
        """This method add a book"""
        if g.user.IsAdmin is True:
            data = request.get_json()
            serial_no = data.get('serial_no')
            book_name = data.get('book_name')
            category = data.get('category')

            current_user = User.query.filter_by(IsAdmin='admin')
            if current_user:
                if serial_no == '':
                    return make_response(jsonify(
                        {"error": "Enter serial Number"}), 400)

                if book_name == '':
                    return make_response(jsonify(
                        {"error": "Enter Book name"}), 400)
                if category == '':
                    return make_response(jsonify(
                        {"error": "Enter Category"}), 400)
                book = Book.query.filter_by(serial_no=serial_no).first()

                if book:
                    return make_response(jsonify(
                        {'message': 'Book  already exist'}), 409)

                book = Book(serial_no=serial_no, book_name=book_name,
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
    def get(self, id):
        """ This method gets a single book"""
        try:
            id = int(id)
        except ValueError:
            return jsonify({"Message": "Use a valid books Id"})
        book = Book.query.filter_by(id=id).first()
        if book:
            one_book = []
            one_book.append({
                "id": book.id,
                "serial_no": book.serial_no,
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
    def put(self, id):
        """ This Method edits book"""
        if g.user.IsAdmin is True:
            data = request.get_json()
            serial_no = data.get('serial_no')
            book_name = data.get('book_name')
            category = data.get('category')

            book = Book.query.filter_by(id=id).first()

            if book:
                book.serial_no = serial_no
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
    def delete(self, id):
        """This method delete book"""
        if g.user.IsAdmin is True:
            book = Book.query.filter_by(id=id).first()
            if book:
                db.session.delete(book)
                db.session.commit()

                return make_response(jsonify({
                    "Message": "delete successful"}), 200)
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
            borrowed = []
            for borrow_book in borrows:
                borrowed.append({
                    # "id": borrow_book.id,
                    "user_email": borrow_book.user_email,
                    "book_id": borrow_book.book_id,
                    "date_borrowed": borrow_book.date_borrowed,
                    "date_returned": borrow_book.date_returned,
                    "returned": borrow_book.returned
                })
            return make_response(jsonify(borrowed), 200)

        # get borrowing history
        borrows = Borrow.query.filter_by(user_email=g.user.email)
        borrowed = []
        for borrow_book in borrows:
            borrowed.append({
                # "id": borrow_book.id,
                "user_email": borrow_book.user_email,
                "book_id": borrow_book.book_id,
                "date_borrowed": borrow_book.date_borrowed,
                "date_returned": borrow_book.date_returned,
                "returned": borrow_book.returned
            })
        return make_response(jsonify(borrowed), 200)

    @token_required
    def post(self, id):
        """ This method borrows a single book"""
        try:
            id = int(id)
        except ValueError:
            return jsonify({"Message": "Invalid book ID"})
        book = Book.query.filter_by(id=id).first()
        if book:
            if book.availabilty is True:
                borrow_book = Borrow(
                    user_email=g.user.email, book_id=id, returned=False)
                book.availabilty = False
                db.session.add(borrow_book)
                db.session.commit()
                return make_response(jsonify({"Message": "You have borrowed "
                                              "a book with id {}".format(id
                                                                         )}),
                                     200)

            else:
                return make_response(jsonify({"Message":
                                              "The book is not available at "
                                              "the moment"}), 400)
        else:
            return make_response(jsonify({"Message": "No book with that id"}),
                                 400)


class ReturnBook(MethodView):
    @token_required
    def put(self, id):
        """ This method Returns a single book"""
        try:
            id = int(id)
        except ValueError:
            return jsonify({"Message": "Invalid book ID"})
        book = Book.query.filter_by(id=id).first()
        return_book = Borrow.query.filter_by(book_id=id).first()

        if book:
            if book.availabilty is False and \
                    return_book.user_email == g.user.email:
                book.availabilty = True
                return_book.returned = True
                db.session.add(return_book)
                db.session.commit()
                return make_response(jsonify({"Message": "You have Returned "
                                              "a book with id {}".format(id
                                                                         )}),
                                     200)

            else:
                return make_response(jsonify({"Message": "You have Not "
                                              "borrowed book with that id"}),
                                     400)
        else:
            return make_response(jsonify({"Message": "No book with that id"}),
                                 400)


book.add_url_rule(
    '/books', view_func=Books.as_view(
        'books'), methods=['GET', 'POST'])

book.add_url_rule(
    '/books/<id>', view_func=GetBook.as_view(
        'getbook'), methods=['GET'])

book.add_url_rule(
    '/books/<id>', view_func=EditBook.as_view(
        'editbook'), methods=['PUT'])

book.add_url_rule(
    '/books/<id>', view_func=DeleteBook.as_view(
        'deletebook'), methods=['DELETE'])

book.add_url_rule(
    '/users/books', view_func=BorrowBook.as_view(
        'borrowhistory'), methods=['GET'])

book.add_url_rule(
    '/users/books/<id>', view_func=BorrowBook.as_view(
        'borrowbook'), methods=['POST'])

book.add_url_rule(
    '/users/books/<id>', view_func=ReturnBook.as_view(
        'returnbook'), methods=['PUT'])
