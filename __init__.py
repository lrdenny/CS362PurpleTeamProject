# CS 362 Purple Team Project @ Eastern Oregon University
# ---
# This project was developed for the CS 362 (Spring 2021) course at Eastern Oregon University
# by "Purple Team" to simulate a basic web application that can work with a database to track
# the "spread" of COVID-19 in the city of La Grande, OR. This is accomplished using the Flask
# web framework, as well as sqlite and SQLAlchemy for the database.
# ---
# Members:
#  - Richard Duck
#  - Lawson Denny
#  - Michael Hefley
#  - Syler Rimbach

# --- IMPORTS ---
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager


# Associates Database w/ SQLAlchemy
db = SQLAlchemy()


# --- create_app ---
# Description: This function creates the initial aspects of the application, and is needed for all other code to run.
def create_app():

    # Instantiates the Web Application
    app = Flask(__name__)

    # Recommend but Unused
    app.config['SECRET_KEY'] = 'secret-key-goes-here'

    # Database Location
    app.config[
        'SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'

    # Recommended SQLAlchemy Setting
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Instantiates the database for future use.
    db.init_app(app)

    # Initializes and begins to work with the Flask LoginManager utility.
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    # Accesses User 'Table'
    from models import User

    # --- load_user ---
    # Description: Restores the user if their login was saved.
    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Sets up the authentication blueprint.
    from auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # Sets up the blueprint for the general portions of the app.
    from main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    return app
