from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from pytz import timezone


ist = timezone('Asia/Kolkata')
db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    userid = db.Column(db.String(30), nullable=False, unique=True)
    email = db.Column(db.String(30), nullable=False, unique=True)
    password = db.Column(db.String(30), nullable=False)
    theme = db.Column(db.String(10), default="light")
    is_verified = db.Column(db.Boolean, nullable=False, default=False)
    books = db.relationship('Record', backref='user', lazy=True)


class Record(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=True)
    isbn = db.Column(db.String(20), nullable=True)
    genre = db.Column(db.String(50), nullable=True)
    description = db.Column(db.Text, nullable=True)
    cover_image = db.Column(db.String(200), nullable=True)  # this will have 'path' to uploaded image
    rating = db.Column(db.Float, nullable=True)
    reading_started = db.Column(db.DateTime(timezone=True), nullable=True, default=lambda: datetime.now(ist))
    reading_finished = db.Column(db.DateTime(timezone=True), nullable=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

