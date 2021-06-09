########################################################################################
######################          Import packages      ###################################
########################################################################################
from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from __init__ import create_app, db
from flask import Flask
from flask_login import LoginManager
from flask_wtf import FlaskForm

from models import User, Location, Visit

app = Flask(__name__)

# you can set key as config
app.config['GOOGLEMAPS_KEY'] = "AIzaSyAxQMjBO89Q733ScJuMi0o0rr3ZhMpfokE"

# Initialize the extension

########################################################################################
# our main blueprint
main = Blueprint('main', __name__)


@main.route('/')  # home page that return 'index'
def index():
    return render_template('index.html')


@main.route('/example')  # home page that return an example google maps page
def maps():
    return render_template('example.html')


@main.route('/admin')  # admin page
def admin():
    return render_template('admin.html')


@main.route('/edituser')  # edit user page
def edituser():
    return render_template('edituser.html')


@main.route('/editlocation')  # edit location page
def editlocation():
    locationList = Location.query.all()
    return render_template('editlocation.html', locationList=locationList)


@main.route('/user')  # regular user page
def user():
    return render_template('user.html')


@main.route('/visitinfo')  # regular visit page
def visitinfo():
    locationList = Location.query.all()
    return render_template('visitinfo.html', locationList=locationList)


@main.route('/report')  # regular report page
def report():
    return render_template('report.html')


@main.route('/profile')  # profile page that return 'profile'
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


@main.route('/modify_user', methods=['POST'])
def modify_user():
    username = request.form.get('username')
    selected = request.form.getlist('infectionStatus')
    infection_status = bool(selected)

    user = User.query.filter_by(username=username).first()
    if not user:
        flash('User was not found, could not modify.')
        return redirect(url_for('main.edituser'))
    if infection_status:
        user.infected = 1
    else:
        user.infected = 0
    db.session.commit()
    flash('User\'s infection status has been modified!')
    return redirect(url_for('main.edituser'))


@main.route('/modify_location', methods=['POST'])
def modify_location():
    location_id = request.form.get('locations')
    infection_percentage = request.form.get('percentage')
    location = Location.query.filter_by(id=location_id).first()
    location.probability = infection_percentage
    db.session.commit()
    return redirect(url_for('main.editlocation'))


@main.route('/create_visit', methods=['POST'])
def create_visit():
    locationInput = request.form.get('locations')
    dateInput = request.form.get('dateChoice')
    timeInput = request.form.get('timeChoice')

    # date = datetime.strptime(dateInput, '%Y-%m-%d')
    # time = datetime.strptime(timeInput, '%H:%M')
    timestamp = dateInput + " " + timeInput
    new_visit = Visit(userID=current_user.id, locationID=locationInput, timestamp=timestamp)
    print(new_visit)
    db.session.add(new_visit)
    db.session.commit()

    return redirect(url_for('main.visitinfo'))


app = create_app()  # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    db.create_all(app=create_app())  # create the SQLite databaseScipts
    app.run(debug=True)  # run the flask app on debug mode