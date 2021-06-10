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
from datetime import datetime
from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
from __init__ import create_app, db
from flask import Flask
import networkx as nx

from models import User, Location, Visit

app = Flask(__name__)

main = Blueprint('main', __name__)


# ---------------------------------
# Following functions simply direct
# to their respective webpage, with
# some having additional functionality
# noted below.
# ---------------------------------

@main.route('/')
def index():
    return render_template('index.html')


@main.route('/example')
def maps():
    return render_template('example.html')


@main.route('/admin')
def admin():
    return render_template('admin.html')


@main.route('/edituser')
def edituser():
    return render_template('edituser.html')


@main.route('/editlocation')
def editlocation():
    # Queries the Location table to populate a dropdown menu.
    locationList = Location.query.all()
    return render_template('editlocation.html', locationList=locationList)


@main.route('/user')
def user():
    return render_template('user.html')


@main.route('/visitinfo')
def visitinfo():
    # Queries the Location table to populate a dropdown menu.
    locationList = Location.query.all()
    return render_template('visitinfo.html', locationList=locationList)


@main.route('/report')
def report():
    return render_template('report.html')


@main.route('/profile')
@login_required
def profile():
    return render_template('profile.html', name=current_user.username)


# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------
# ---------------------------------


# --- modify_user ---
# Description: The following function sets a desired user to be either
#              infected with COVID-19, or not.
@main.route('/modify_user', methods=['POST'])
def modify_user():
    # Acquires information from HTML page.
    username = request.form.get('username')
    selected = request.form.getlist('infectionStatus')
    infection_status = bool(selected)

    # Checks if the user exists.
    user = User.query.filter_by(username=username).first()
    if not user:  # User doesn't exist...
        flash('User was not found, could not modify.')
        return redirect(url_for('main.edituser'))
    if infection_status:  # User is infected...
        user.infected = 1
    else:  # Use is not infected...
        user.infected = 0

    db.session.commit()
    flash('User\'s infection status has been modified!')
    return redirect(url_for('main.edituser'))


# --- modify_location ---
# Description: The following function sets a desired location's probability
#              of COVID-19 infection to a certain value.
@main.route('/modify_location', methods=['POST'])
def modify_location():
    # Gets information from HTML page.
    location_id = request.form.get('locations')
    infection_percentage = request.form.get('percentage')

    # Gets the desired location to modify.
    location = Location.query.filter_by(id=location_id).first()
    # Sets the infection probability of a location.
    location.probability = infection_percentage

    db.session.commit()
    return redirect(url_for('main.editlocation'))


# --- create_visit ---
# Description: The following function creates a new visit based on information
#              that the user provides.
@main.route('/create_visit', methods=['POST'])
def create_visit():
    # Gets information from HTML page.
    locationInput = request.form.get('locations')
    dateInput = request.form.get('dateChoice')
    timeInput = request.form.get('timeChoice')

    # Creates a timestamp of when the user visited.
    timestamp = dateInput + " " + timeInput

    # Creates a new visit based on the user's input.
    new_visit = Visit(userID=current_user.id, locationID=locationInput, timestamp=timestamp)
    db.session.add(new_visit)
    db.session.commit()

    return redirect(url_for('main.visitinfo'))


# --- generate_report ---
# --- NOT IMPLEMENTED ---
# Description: The following function generates a new report based on
#              a visit by a user, and shows their likelihood of infection.
@main.route('/generate_report', methods=['POST'])
def generate_report():
    # Used to hold the infected user's name.
    infectedUser = ""
    # Graph used for output.
    G = nx.Graph()

    # Gets the last visit of the current_user.
    lastVisit = Visit.query.filter_by(userID=current_user.id).order_by(Visit.id.desc()).first()

    # Sets the date of the desired visit.
    date = datetime.strptime(lastVisit.timestamp[:-6], '%Y-%m-%d')

    # Acquires a list of visits on a certain day.
    list = Visit.query.filter(Visit.timestamp.contains(str(date.date()))).all()

    # Iterates through visits, users, and locations.
    for x in range(len(list)):
        # print(list[x].username, " is going to ", list[x].location)
        currentUser = User.query.filter_by(id=list[x].userID).first()
        if currentUser.infected == 1:
            infectedUser = currentUser.username
        for y in range(x + 1, len(list)):
            innerUser = User.query.filter_by(id=list[y].userID).first()
            if innerUser.username != currentUser.username:
                print(innerUser.username)
                print(currentUser.username)
                if (list[x].locationID == list[y].locationID) and (
                        G.get_edge_data(innerUser.username, innerUser.username, default=0) == 0):
                    G.add_edge(currentUser.username, innerUser.username,
                               weight=(Location.query.filter_by(id=list[x].locationID)).probability)
                elif (Location.query.filter_by(id=list[x].locationID).first()).probability < \
                        (G[currentUser.username][innerUser.username]["weight"]):
                    G[currentUser.username][innerUser.username]["weight"] = \
                        (Location.query.filter_by(id=list[x].locationID)).probability
            else:
                continue

    print("The infected user is ", infectedUser)

    # Iterates through visits, users, and locations.
    for i in range(len(list)):
        currentUser = User.query.filter_by(id=list[x].userID).first()
        if list[i].username != infectedUser:
            shortest_path = nx.dijkstra_path(G, currentUser.username, infectedUser)
            infectionProb = 1.0

            for x in range(len(shortest_path) - 1):
                infectionProb *= (G[shortest_path[x]][shortest_path[x + 1]]["weight"]) / 100.0

            print(currentUser.username, " has an infection probability of ", round(infectionProb, 4) * 100, "%")

        else:
            print("The infected user has no shortest path")

    elarge = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] > .5]
    esmall = [(u, v) for (u, v, d) in G.edges(data=True) if d["weight"] <= .5]

    pos = nx.spring_layout(G)  # positions for all nodes

    # Nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # Edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=4)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=4, alpha=0.5, edge_color="b", style="dashed"
    )

    # Labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    # Outputs Graph
    from matplotlib import pyplot as plt
    plt.axis("off")
    plt.savefig("path.png")
    plt.show()

    return redirect(url_for('main.report'))


# Creates the application and starts it.
app = create_app()
if __name__ == '__main__':
    db.create_all(app=create_app())
    app.run(debug=True)
