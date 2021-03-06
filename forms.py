from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField
from wtforms.validators import InputRequired, email_validator, Email


class RegisterForm(FlaskForm):
    """Form for registering a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])
    email = StringField("Email", validators=[InputRequired(), Email()])
    first_name = StringField("First Name", validators=[InputRequired()])
    last_name = StringField("Last Name", validators=[InputRequired()])


class LoginForm(FlaskForm):
    """Form for logging in a user."""

    username = StringField("Username", validators=[InputRequired()])
    password = PasswordField("Password", validators=[InputRequired()])

class CSRFProtectForm(FlaskForm):
    """Form just for CSRF Protection"""

class NewOrEditNoteForm(FlaskForm):
    """Form for adding a new note"""
    title= StringField("Title", validators=[InputRequired()])
    content = TextAreaField("Content", validators=[InputRequired()])