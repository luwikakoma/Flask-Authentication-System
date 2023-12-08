from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, PasswordField, BooleanField
from wtforms import RadioField
from wtforms.validators import InputRequired, Email, Length
from .models import UserRole

csrf = CSRFProtect()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class CreateUserForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    password = StringField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    role = RadioField('Role', choices=[], coerce=str)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.role.choices = [(role.name, role.name) for role in UserRole.query.all()]