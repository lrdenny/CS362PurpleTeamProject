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
# ---
# Built Upon: https://medium.com/analytics-vidhya/creating-login-page-on-flask-9d20738d9f42
# Resource Created By: User "Elfao" From Medium

# --- IMPORTS ---
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db

# Blueprint Object (Used for Authentication)
auth = Blueprint('auth', __name__)


# --- login ---
# Description: This functions 'attempts' to login a user. If it succeeds, they may interact with the app. Otherwise,
#              they must either sign up or try their login again.
@auth.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('login.html')

    else:
        # Retrieves information from the login page.
        username = request.form.get('username')
        password = request.form.get('password')

        # Decides if the user's session login should be saved.
        remember = True if request.form.get('remember') else False

        # Finds if the user exists in the database.
        user = User.query.filter_by(username=username).first()

        if not user:  # If user does not exist...
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        if user.password.startswith('pbkdf2'):  # If user exists...
            if not check_password_hash(user.password, password):
                flash('Please check your login details and try again.')
                return redirect(url_for('auth.login'))
        elif user.password != password: # If user exists (again)...
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login'))

        # Logs the user in, deciding if they should be remembered.
        login_user(user, remember=remember)

        # If user is an admin...
        if user.admin == 1:
            return redirect(url_for('main.admin'))  # Goes to admin menu page.
        else:
            return redirect(url_for('main.profile'))  # Goes to user menu page.


# --- signup ---
# Description: This function signs up a user, creating a new entry for them in the system,
#              and then allowing them to login.
@auth.route('/signup', methods=['GET', 'POST'])
def signup():

    if request.method == 'GET':
        return render_template('signup.html')

    else:
        # Retrieves information from the sign up page.
        username = request.form.get('username')
        password = request.form.get('password')

        # Finds if the user exists in the database.
        user = User.query.filter_by(username=username).first()

        if user:  # If user exists...
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))

        # Else user doesn't exists...
        # - Creates a new user and adds them to the database.
        new_user = User(username=username, password=generate_password_hash(password))
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('auth.login'))  # Goes to login page.


# --- logout ---
# Description: This function logs out the current user, and returns back to the login page.
@auth.route('/logout')
@login_required
def logout():

    logout_user()
    return redirect(url_for('main.index'))
