from flask_wtf import FlaskForm
from wtforms.fields import StringField, SubmitField, TextAreaField, DateField, PasswordField
from wtforms.validators import DataRequired, length, Email, ValidationError

from models import User


class BlogForm(FlaskForm):
    title = StringField("Enter blog title", validators=[DataRequired(), length(max=40)])
    content = TextAreaField("Enter Blog", validators=[DataRequired()])

    post = SubmitField("Post")


class RegisterForm(FlaskForm):
    username = StringField("Enter your username", validators=[DataRequired(), length(min=3, max=50)])
    email = StringField('Enter your email', validators=[DataRequired(), Email()])
    birth_date = DateField("Enter your birt date")
    password = PasswordField("Enter your password", validators=[DataRequired(), length(min=8, max=32)])

    submit = SubmitField("Submit")

    def validate_email(self, field):
        email = field.data
        user = User.query.filter_by(email=email).first()
        if user:
            ValidationError("This email is already registered.", category="error")


class LoginForm(FlaskForm):
    username = StringField("Enter your username", validators=[DataRequired(), length(min=3, max=50)])
    email = StringField('Enter your email', validators=[DataRequired(), Email()])
    password = PasswordField("Enter your password", validators=[DataRequired(), length(min=8, max=32)])

    login = SubmitField("Submit")

    def validate(self, extra_validators=None):
        if not super().validate(extra_validators=extra_validators):
            return False

        # Check if user exists by username or email
        user_by_username = User.query.filter(User.username == self.username.data).first()
        user_by_email = User.query.filter(User.email == self.email.data).first()

        if not user_by_username and not user_by_email:
            self.username.errors.append("Invalid username.")
            self.email.errors.append("Invalid email.")
            return False

        user = user_by_username or user_by_email

        if user_by_username and not user_by_email:
            self.email.errors.append("Invalid email.")
        elif user_by_email and not user_by_username:
            self.username.errors.append("Invalid username.")

        if user.password != self.password.data:
            self.password.errors.append("Invalid password. Please try again.")
            return False

        return True
