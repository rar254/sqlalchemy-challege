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
    for name, frequency in active_station:
        station_dict = {}
        station_dict['Station'] = name
        station_dict['Frequency'] = frequency
        station.append(station_dict)

    return jsonify(active_station)

@app.route("/api/v1.0/tobs")
def tobs():
     # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query
    USC00519281_tobs = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date >= '2016-08-23',Measurement.station == "USC00519281").\
        group_by(Measurement.date).\
        order_by(Measurement.date).all()

    # Closing the session
    session.close()

    # Empty list to add the dictionary values to.
    tob = []
    for date, temp in USC00519281_tobs:
        station_tobs_dict ={}
        station_tobs_dict['Date'] = date
        station_tobs_dict['Temperature'] = temp
        tob.append(station_tobs_dict)

    # jsonify the results
    return jsonify(tob)

@app.route("/api/v1.0/<start>")
def temp(start):
     # # Create our session (link) from Python to the DB
    session = Session(engine)

    # Session Query
    temperature = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start).all()

    # Closing the session
    session.close()

    # Empty list to add the dictionary values to.
    temperature_list = []
    for min,max,avg in temperature:
        temperature_dict = {}
        temperature_dict['Min'] = min
        temperature_dict['Max'] = max
        temperature_dict['Average'] = avg
        temperature_list.append(temperature_dict)

    # UserError message    
    if temperature_list[0]['Min'] is None:
        return "Oops. Something went wrong. Is your date in the YYYY-MM-DD format?<br/>" \
            "Please try again"

    # jsonify the results
    return jsonify(temperature_list)

@app.route("/api/v1.0/<start>/<end>")
def temps(start, end):

     # # Create our session (link) from Python to the DB
    session = Session(engine)

    #Query
    temperature_range = session.query(func.min(Measurement.tobs),func.max(Measurement.tobs),func.avg(Measurement.tobs)).\
        filter(Measurement.date >= start,Measurement.date <= end).all()

    # Closing the session
    session.close()

    # Empty list to add the dictionary values to.
    temp_range_list = []
    for min,max,avg in temperature_range:
        temp_range_dict = {}
        temp_range_dict['Min'] = min
        temp_range_dict['Max'] = max
        temp_range_dict['Average'] = avg
        temp_range_list.append(temp_range_dict)

    # Error message
    if temp_range_list[0]['Min'] is None:
        return "Oops. Something went wrong. Is your date in the YYYY-MM-DD format?<br/>" \
            "Please try again"

    # jsonify the results
    return jsonify(temp_range_list)    

#Add Debugger to run the app
if __name__ == '__main__':
    app.run(debug=True)
