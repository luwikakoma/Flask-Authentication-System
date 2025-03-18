import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from flask_bcrypt import Bcrypt
from flask_migrate import Migrate

# Initialize extensions
db = SQLAlchemy()
bcrypt = Bcrypt()
csrf = CSRFProtect()
login_manager = LoginManager()

UPLOAD_FOLDER_ENV_VAR = 'UPLOAD_FOLDER'
DEFAULT_UPLOAD_FOLDER = 'C:\\Users\\user\\Desktop\\File Sharer Uploads'

def create_app():
    app = Flask(__name__)

    # App Configurations
    app.config['SECRET_KEY'] = 'secret-key-goes-here'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Configure upload folder
    upload_folder = os.environ.get(UPLOAD_FOLDER_ENV_VAR, DEFAULT_UPLOAD_FOLDER)
    os.makedirs(upload_folder, exist_ok=True)  # Ensure folder exists
    app.config['UPLOAD_FOLDER'] = upload_folder

    # Initialize extensions
    db.init_app(app)
    bcrypt.init_app(app)
    csrf.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'

    migrate = Migrate(app, db)  # Setup Flask-Migrate

    with app.app_context():
        from .models import User, UserRole
        from .auth import auth as auth_blueprint
        from .main import main as main_blueprint

        app.register_blueprint(auth_blueprint)
        app.register_blueprint(main_blueprint)

        db.create_all()

        # Create default roles if they don't exist
        if not UserRole.query.filter_by(name='admin').first():
            db.session.add(UserRole(name='admin'))
        if not UserRole.query.filter_by(name='user').first():
            db.session.add(UserRole(name='user'))

        db.session.commit()

        # User loader function for Flask-Login
        @login_manager.user_loader
        def load_user(user_id):
            return User.query.get(int(user_id))

    return app
