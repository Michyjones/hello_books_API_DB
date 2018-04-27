from flask.views import MethodView
from flask import Blueprint, make_response, jsonify

from app.models import Book
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


book.add_url_rule(
    '/books', view_func=Books.as_view(
        'books'), methods=['GET'])
