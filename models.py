from flask import Flask
from flask import SQLALchemy
from config import app_config

app = Flask(__name__)
app.config.from_object(app_config['development'])
db = SQLALchemy(app)


class User(db.Model):
    __tablename__ = 'user'
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(128))
    role = db.Column(db.String(20))
    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')


class Book(db.Model):
    __tablename__ = 'book'
    id = db.Column('bookid', db.Integer, primary_key=True)
    book_name = db.Column('book_name', db.String(100))
    category = db.Column('category', db.String(50))
    availabilty = db.Column(db.Boolean, default=True)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')


class Borrow(db.Model):

    __tablename__ = 'borrow'

    id = db.Column(db.Integer, primary_key=True)
    user_email = db.Column(db.Integer, db.ForeignKey('user.email'))
    bookid = db.Column(db.Integer, db.ForeignKey('books.id'))
    returned = db.Column(db.Boolean, default=False)
