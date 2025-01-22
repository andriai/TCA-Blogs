from flask_login import UserMixin
from ext import db, login_manager
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()  # Initialize Bcrypt


class Blog(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())
    comments = db.relationship('Comment', backref='blog', cascade="all, delete")  # Fix backref

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


class Comment(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    content = db.Column(db.String())
    blog_id = db.Column(db.Integer(), db.ForeignKey('blog.id', ondelete='CASCADE'), nullable=False)  # Ensure cascade delete
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='comments')

    def __init__(self, content, blog_id, user_id):
        self.content = content
        self.blog_id = blog_id
        self.user_id = user_id


class Like(db.Model):
    id = db.Column(db.Integer(), primary_key=True)
    blog_id = db.Column(db.Integer(), db.ForeignKey('blog.id', ondelete='CASCADE'))
    user_id = db.Column(db.Integer(), db.ForeignKey('user.id', ondelete='CASCADE'))
    blog = db.relationship('Blog', backref=db.backref('likes', lazy=True))
    user = db.relationship('User', backref=db.backref('likes', lazy=True))

    def __init__(self, user_id, blog_id):
        self.user_id = user_id
        self.blog_id = blog_id


class User(db.Model, UserMixin):
    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String, unique=True, nullable=False)
    username = db.Column(db.String, nullable=False)
    birth_date = db.Column(db.Integer, nullable=True)
    password_hash = db.Column(db.String, nullable=False)
    role = db.Column(db.String, default="user")

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
