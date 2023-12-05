# Flask-Authentication-System
This project demonstrates how to add authentication to a Flask app with Flask-Login. It allows users to log in and access protected pages, and displays information from the user's account on their profile page.
Project Structure

## The file structure of the project looks like this:

    Flask-Authentication-System
    └── project
        ├── __init__.py       # setup the app
        ├── auth.py           # the auth routes for the app
        ├── db.sqlite         # the database
        ├── main.py           # the non-auth routes for the app
        ├── models.py         # the user model
        └── templates
            ├── base.html     # contains common layout and links
            ├── index.html    # show the home page
            ├── login.html    # show the login form
            ├── profile.html  # show the profile page
            └── signup.html   # show the signup form

## Installation

### Clone the repository and navigate to the project directory:

    git clone https://github.com/JWebster-Colby/Flask-Authentication-System.git
    cd Flask-Authentication-System

### Create a virtual environment and activate it:

    python3 -m venv auth
    source auth/bin/activate

### Install the required packages:

    pip install flask flask-sqlalchemy flask-login
    or
    pip install -r requirements.txt

## Usage

Set the FLASK_APP and FLASK_DEBUG environment variables:

    export FLASK_APP=project
    export FLASK_DEBUG=1

Run the Flask application:

    flask run