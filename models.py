from flask_login import UserMixin

from ext import db, login_manager


class Blog(db.Model):

    id = db.Column(db.Integer(), primary_key=True)
    title = db.Column(db.String())
    content = db.Column(db.String())
    author = db.Column(db.String())

    def create(self):
        db.session.add(self)
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    @staticmethod
    def save():
        db.session.commit()


class User(db.Model, UserMixin):

    id = db.Column(db.Integer(), primary_key=True)
    email = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    birth_date = db.Column(db.Integer)
    password = db.Column(db.String)
    role = db.Column(db.String)

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
