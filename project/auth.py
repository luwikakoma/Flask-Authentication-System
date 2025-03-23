from flask import Blueprint, render_template, redirect, url_for, request, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, UserRole
from . import db
from .forms import LoginForm, RegisterForm, CreateUserForm, ProfileEditForm
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()  # Initialize Flask-Bcrypt

auth = Blueprint('auth', __name__)

@auth.route('/')
def login():
    login_form = LoginForm() 
    return render_template('login.html', login_form = login_form)

@auth.route('/login', methods=['POST'])
def login_post():
    login_form = LoginForm()  

    if login_form.validate_on_submit():

        email = login_form.email.data  
        password = login_form.password.data  
        #remember = login_form.remember.data if login_form.remember.data else False  # Correct way to check remember

        user = User.query.filter_by(email=email).first()

        # Check if user exists and verify password
        if not user or not bcrypt.check_password_hash(user.password, password):
            flash('Please check login details and try again!')
            return redirect(url_for('auth.login'))

        # Log in the user
        login_user(user)
        return redirect(url_for('main.home'))

    # If the form is not valid, redirect back to login page
    flash('Invalid form data, please try again')
    return redirect(url_for('auth.login'))

@auth.route('/signup')
def signup():
    form = RegisterForm()
    return render_template('signup.html', form=form)

@auth.route('/signup', methods=['POST'])
def signup_post():
    form = RegisterForm()
    if form.validate_on_submit():
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        # Check if email already exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('User already exists!')
            return redirect(url_for('auth.signup'))

        # Hash password correctly
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Fetch the role 'user' from the database
        role = UserRole.query.filter_by(name='user').first()

        # Create a new user with the hashed password
        new_user = User(email=email, name=name, password=hashed_password, roles=[role])

        # Save user
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))


@auth.route('/create_user', methods=['POST'])
def create_user():
    form = CreateUserForm()
    if form.validate_on_submit():
        role_ids = form.roles.data
        roles = UserRole.query.filter(UserRole.id.in_(role_ids)).all()

        email = form.email.data
        name = form.name.data
        password = form.password.data

        # Check if email exists
        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists')
            return redirect(url_for('auth.create_user'))

        # Hash the password correctly
        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        # Create a new user
        new_user = User(email=email, name=name, password=hashed_password, roles=roles)

        db.session.add(new_user)
        db.session.commit()
        flash('User created successfully')
        return redirect(url_for('auth.create_user'))
    return render_template('create_user.html', form=form)


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = ProfileEditForm()
    
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.email = form.email.data
        
        db.session.commit()
        flash('Your profile has been updated.')
        return redirect(url_for('main.home'))
    
    elif request.method == 'GET':
        form.name.data = current_user.name
        form.email.data = current_user.email
    
    return render_template('edit_profile.html', form=form, current_user=current_user)

@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@auth.route('/forgot_password')
def forgot_password():
    return render_template('signup.html') #change to forgot password route later