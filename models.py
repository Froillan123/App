from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    first_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)
    birthday = db.Column(db.Date)
    marital_status = db.Column(db.String, nullable=True)
    address = db.Column(db.String, nullable=True)
    contact_info = db.Column(db.String, nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'
