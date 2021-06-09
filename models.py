from flask_login import UserMixin
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from __init__ import db


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    key = db.Column(db.String(100))
    infected = db.Column(db.Integer, default=0)
    admin = db.Column(db.Integer, default=0)


class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)
    probability = db.Column(db.Integer, default=0)


class Visit(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    userID = db.Column(db.Integer, ForeignKey('user.id'))
    locationID = db.Column(db.Integer, ForeignKey('location.id'))
    timestamp = db.Column(db.String(100)) # YYYY-MM-DD HH:MM
    user = relationship("User", foreign_keys=[userID])
    location = relationship("Location", foreign_keys=[locationID])
