########################################################################################
######################          Import packages      ###################################
########################################################################################
from datetime import datetime

from flask import Blueprint, render_template, flash, redirect, url_for, request, session
from flask_login import login_required, current_user
#from matplotlib import pyplot as plt

from __init__ import create_app, db
from flask import Flask
# import matplotlib.pyplot as plt
import networkx as nx
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
    # generate_report()
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


# Creates a new visit.
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


@main.route('/generate_report', methods=['POST'])
def generate_report():
    infectedUser = ""
    G = nx.Graph()
    lastVisit = Visit.query.filter_by(userID=current_user.id).order_by(Visit.id.desc()).first()
    date = datetime.strptime(lastVisit.timestamp[:-6], '%Y-%m-%d')
    list = Visit.query.filter(Visit.timestamp.contains(str(date.date()))).all()
    for x in range(len(list)):
        # print(list[x].username, " is going to ", list[x].location)
        currentUser = User.query.filter_by(id=list[x].userID).first()
        if currentUser.infected == 1:
            infectedUser = currentUser.username
        for y in range(x + 1, len(list)):
            innerUser = User.query.filter_by(id=list[y].userID).first()
            if innerUser.username and currentUser.username:
                if (list[x].locationID == list[y].locationID) and (
                        G.get_edge_data(innerUser.username, innerUser.username, default=0) == 0):
                    G.add_edge(currentUser.username, innerUser.username,
                               weight=(Location.query.filter_by(id=list[x].locationID)).probability)
                elif (Location.query.filter_by(id=list[x].locationID).first()).probability < \
                        (G[currentUser.username][innerUser.username]["weight"]):
                    G[currentUser.username][innerUser.username]["weight"] = \
                        (Location.query.filter_by(id=list[x].locationID)).probability

    print("The infected user is ", infectedUser)

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

    # nodes
    nx.draw_networkx_nodes(G, pos, node_size=700)

    # edges
    nx.draw_networkx_edges(G, pos, edgelist=elarge, width=4)
    nx.draw_networkx_edges(
        G, pos, edgelist=esmall, width=4, alpha=0.5, edge_color="b", style="dashed"
    )

    # labels
    nx.draw_networkx_labels(G, pos, font_size=20, font_family="sans-serif")
    labels = nx.get_edge_attributes(G, "weight")
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)

    from matplotlib import pyplot as plt
    plt.axis("off")
    plt.savefig("path.png")
    plt.show()

    return redirect(url_for('main.report'))


app = create_app()  # we initialize our flask app using the __init__.py function
if __name__ == '__main__':
    db.create_all(app=create_app())  # create the SQLite databaseScipts
    app.run(debug=True)  # run the flask app on debug mode
