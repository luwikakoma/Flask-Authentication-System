from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, FileField, SelectField, PasswordField, SubmitField
from wtforms import  SelectMultipleField, widgets
from wtforms.validators import InputRequired, Email, Length, DataRequired
from .models import UserRole
from flask import request

class MultiCheckboxField(SelectMultipleField):
    widget = widgets.ListWidget(prefix_label=False)
    option_widget = widgets.CheckboxInput()

csrf = CSRFProtect()

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    #remember = BooleanField('Remember Me')

class RegisterForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=80)])

class CreateUserForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    password = StringField('Password', validators=[InputRequired(), Length(min=8, max=80)])
    roles = MultiCheckboxField('Roles', coerce=int)

    def __init__(self, *args, **kwargs):
        super(CreateUserForm, self).__init__(*args, **kwargs)
        self.roles.choices = [(role.id, role.name) for role in UserRole.query.all()]

    def validate(self, extra_validators=None):
        initial_validation = super(CreateUserForm, self).validate()

        if not initial_validation:
            return False

        # Convert the list of role IDs into a list of Roles
        roles = UserRole.query.filter(UserRole.id.in_(self.roles.data)).all()

        if not roles:
            self.roles.errors.append('Invalid role selections.')
            return False

        return True

class ProfileEditForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Email(), Length(max=50)])
    name = StringField('Name', validators=[InputRequired(), Length(max=50)])
    current_password = PasswordField('Current Password')
    password = PasswordField('New Password (Leave blank to keep current password)')
    
    submit = SubmitField('Update')

class UploadFileForm(FlaskForm):
    file = FileField('Select file', validators=[DataRequired()])
    submit = SubmitField('Upload')

class CreateFolderForm(FlaskForm):
    foldername = StringField('Folder Name', validators=[DataRequired()])
    submit = SubmitField('Create Folder')

class DeleteFileForm(FlaskForm):
    choose = SelectField('Select file to delete', validators=[DataRequired()])
    submit = SubmitField('Delete')
