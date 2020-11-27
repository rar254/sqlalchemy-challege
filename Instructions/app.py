#Import dependancies
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
climate_path = "Resources/hawaii.sqlite"

engine = create_engine(f'sqlite:///{climate_path}')

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def home():
    """Homepage: List all available api routes."""
    return (
        f"Welcome! Here are the available api routes!<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end<br/>"
    )

@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of last 12M precipitation data"""
    # Query all precipitation data
    prcp_val = session.query(Measurement.date, func.avg(Measurement.prcp)).\
        filter(Measurement.date >= '2016-08-23').\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Close the session
    session.close()

    # Empty list to add the dictionary values to.
    prcp = []
    
    for date, average in prcp_val:
        prcp_dict = {}
        prcp_dict['Date'] = date
        prcp_dict['Average Precipitation'] = average
        prcp.append(prcp_dict)
    
    # jsonify the results
    return jsonify(prcp)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a list of stations"""
    # Query all passengers
    active_station = session.query(Station.station, func.count(Measurement.station)).filter(Station.station == Measurement.station).\
        group_by(Station.station).\
        order_by(func.count(Measurement.station).desc()).all()

    session.close()

    # Empty list to add the dictionary values to.
    station = []
    for name in active_station:
        station_dict = {}
        station_dict['Name'] = name
        station.append(station_dict)

    return jsonify(active_station)

#Add Debugger to run the app
if __name__ == '__main__':
    app.run(debug=True)
