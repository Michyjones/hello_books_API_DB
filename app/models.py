from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'

    def __init__(self, email, password, role):
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.role = role

    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20))
    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')

    def verify_password(self, password):
        return check_password_hash(self.password, password)


class Book(db.Model):
    __tablename__ = 'book'

    def __init__(self, bookid, book_name, category):
        self.bookid = bookid
        self.book_name = book_name
        self.category = category

    bookid = db.Column('bookid', db.Integer, primary_key=True)
    book_name = db.Column('book_name', db.String(100))
    category = db.Column('category', db.String(50))
    availabilty = db.Column(db.Boolean, default=True)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')


class Borrow(db.Model):

    __tablename__ = 'borrow'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.String, db.ForeignKey('user.email'))
    bookid = db.Column(db.Integer, db.ForeignKey('book.bookid'))
    date_borrowed = db.Column(
        db.DateTime, default=datetime.now, nullable=False)
    date_returned = db.Column(
        db.DateTime, onupdate=datetime.now, nullable=False)
    returned = db.Column(db.Boolean, default=False)



