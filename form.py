from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, DateField, PasswordField
from wtforms.validators import DataRequired, length, Email, ValidationError

from models import User
from ext import bcrypt


class BlogForm(FlaskForm):
    title = StringField("ბლოგის სათაური", validators=[DataRequired(), length(max=40)])
    content = TextAreaField("ბლოგი", validators=[DataRequired()])

    post = SubmitField("ატვირთვა")


class CommentForm(FlaskForm):
    content = TextAreaField("კომენტარი", validators=[DataRequired()])
    submit = SubmitField("ატვირთე კომენტარი")


class RegisterForm(FlaskForm):
    username = StringField("შეიყვანეთ სახელი", validators=[DataRequired(), length(min=3, max=50)])
    email = StringField('შეიყვანეთ ელ.ფოსტა', validators=[DataRequired(), Email()])
    birth_date = DateField("შეიყვანეთ დაბადების თარიღი")
    password = PasswordField("შეიყვანეთ პაროლი", validators=[DataRequired(), length(min=8, max=32)])

    submit = SubmitField("რეგისტრაცია")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            self.email.errors.append("ელ.ფოსტა გამოყენებულია.")


class LoginForm(FlaskForm):
    username = StringField("შეიყვანეთ სახელი", validators=[DataRequired(), length(min=3, max=50)])
    email = StringField('შეიყვანეთ ელ.ფოსტა', validators=[DataRequired(), Email()])
    password = PasswordField("შეიყვანეთ პაროლი", validators=[DataRequired(), length(min=8, max=32)])
    login = SubmitField("ავტორიზაცია")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        user_by_username = User.query.filter(User.username == self.username.data).first()
        user_by_email = User.query.filter(User.email == self.email.data).first()

        if not user_by_username and not user_by_email:
            self.username.errors.append("არასწორი სახელი.")
            self.email.errors.append("არასწორი ელ.ფოსტა.")
            return False

        user = user_by_username or user_by_email

        if user_by_username and not user_by_email:
            self.email.errors.append("არასწორი ელ.ფოსტა.")
        elif user_by_email and not user_by_username:
            self.username.errors.append("არასწორი სახელი.")

        if not user.check_password(self.password.data):
            self.password.errors.append("არასწორი პაროლი. ხელახლა სცადეთ.")
            return False

        return True