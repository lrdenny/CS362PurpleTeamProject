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
from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from __init__ import db


# User Class - Represents User Table
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(1000))
    infected = db.Column(db.Integer, default=0)
    admin = db.Column(db.Integer, default=0)


# Location Class - Represents Location Table
class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    probability = db.Column(db.Integer, default=0)


# Visit Class - Represents Visit Table
class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, ForeignKey('user.id'))
    locationID = db.Column(db.Integer, ForeignKey('location.id'))
    timestamp = db.Column(db.String(100))  # YYYY-MM-DD HH:MM
    user = relationship("User", foreign_keys=[userID])
    location = relationship("Location", foreign_keys=[locationID])
