from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'user'

    def __init__(self, first_name, last_name, address, email,
                 password, IsAdmin=False):
        self.first_name = first_name
        self.last_name = last_name
        self.address = address
        self.email = email
        self.password = generate_password_hash(password, method='sha256')
        self.IsAdmin = IsAdmin

    first_name = db.Column(db.String(30))
    last_name = db.Column(db.String(30))
    address = db.Column(db.String(30))
    email = db.Column(db.String(50), primary_key=True)
    password = db.Column(db.String(128))
    IsAdmin = db.Column(db.Boolean, default=False)
    borrows = db.relationship('Borrow', backref='user', lazy='dynamic')

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    @staticmethod
    def exists(email):
        """
        Used to check if the user exists in the database
        """
        person = User.query.filter_by(email=email).first()
        return True if person else False

    def save(self):
        """Save  to the database"""
        db.session.add(self)
        db.session.commit()


class Book(db.Model):
    __tablename__ = 'book'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    serial_no = db.Column(db.String(20))
    book_name = db.Column('book_name', db.String(100))
    category = db.Column('category', db.String(50))
    availabilty = db.Column(db.Boolean, default=True)
    borrows = db.relationship('Borrow', backref='book', lazy='dynamic')


class Borrow(db.Model):

    __tablename__ = 'borrow'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'))
    user_email = db.Column(db.String, db.ForeignKey('user.email'))
    date_borrowed = db.Column(
        db.DateTime, default=datetime.now, nullable=False)
    date_returned = db.Column(
        db.DateTime, onupdate=datetime.now, nullable=True)
    returned = db.Column(db.Boolean, default=False)


class BlacklistedToken(db.Model):
    """All blacklisted tokens"""
    __tablename__ = 'blacklist'

    id = db.Column(db.Integer, primary_key=True)
    token = db.Column(db.String(200), nullable=False)
    valid = db.Column(db.Boolean, default=True)

    def __init__(self, token, valid=True):
        self.token = token
        self.valid = valid

    def save(self):
        """Save  to the database"""
        db.session.add(self)
        db.session.commit()
