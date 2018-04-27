from flask.views import MethodView
from flask import Blueprint, request, make_response, jsonify, g

from app.models import Book, User, db
from app.users.views import token_required


books = {}
book = Blueprint('book', __name__, url_prefix='/api/v2')


class Books(MethodView):
    @token_required
    def get(self):
        """This method retrieves allbooks """
        books = Book.query.all()
        all_books = []
        for book in books:
            all_books.append({
                "bookid": book.bookid,
                "book_name": book.book_name,
                "category": book.category,
                "availabilty": book.availabilty
            })
        return make_response(jsonify(all_books), 200)

    @token_required
    def post(self):
        """This method add a book"""
        if g.user.role == "admin":
            data = request.get_json()
            bookid = data.get('bookid')
            book_name = data.get('book_name')
            category = data.get('category')
            availabilty = data.get('availabilty')

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
                            category=category, availabilty=availabilty)
                db.session.add(book)
                db.session.commit()
                return make_response(jsonify(
                    {"message": "Book Added successfully"
                     }), 201)
            else:
                return jsonify('go')
        else:
            return make_response(jsonify({"Message":
                                          "You are not Authorized !!!"}), 401)


book.add_url_rule(
    '/books', view_func=Books.as_view(
        'books'), methods=['GET', 'POST'])

