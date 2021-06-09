########################################################################################
######################          Import packages      ###################################
########################################################################################
from flask import Blueprint, render_template, redirect, url_for, request, flash
from werkzeug.security import generate_password_hash, check_password_hash
from models import User
from flask_login import login_user, logout_user, login_required, current_user
from __init__ import db


auth = Blueprint('auth', __name__) # create a Blueprint object that we name 'auth'


@auth.route('/login', methods=['GET', 'POST']) # define login page path
def login(): # define login page fucntion
    if request.method=='GET': # if the request is a GET we return the login page
        return render_template('login.html')
    else: # if the request is POST the we check if the user exist and with te right password
        username = request.form.get('username')
        password = request.form.get('password')
        key = db.Column(db.String(100))
        admin = request.form.get('admin')
        infected = request.form.get('infected')
        remember = True if request.form.get('remember') else False
        user = User.query.filter_by(username=username).first()
        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the databaseScipts
        if not user:
            flash('Please sign up before!')
            return redirect(url_for('auth.signup'))
        elif not user.password == password:
            flash('Please check your login details and try again.')
            return redirect(url_for('auth.login')) # if the user doesn't exist or password is wrong, reload the page
        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        if (user.admin == 1):
            return redirect(url_for('main.admin'))
        else:
            return redirect(url_for('main.profile'))


@auth.route('/signup', methods=['GET', 'POST'])# we define the sign up path
def signup(): # define the sign up function
    if request.method=='GET': # If the request is GET we return the sign up page and forms
        return render_template('signup.html')
    else: # if the request is POST, then we check if the email doesn't already exist and then we save data
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first() # if this returns a user, then the email already exists in databaseScipts
        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return redirect(url_for('auth.signup'))
        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(username=username, password=password, key=password) #
        # add the new user to the databaseScipts
        db.session.add(new_user)
        db.session.commit()
        return redirect(url_for('auth.login'))

@auth.route('/logout') # define logout path
@login_required
def logout(): #define the logout function
    logout_user()
    return redirect(url_for('main.index'))
