import datetime as dt
from dateutil.relativedelta import relativedelta
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
meas=Base.classes.measurement
station=Base.classes.station

#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")
def welcome():
    """List all available api routes."""
    return (
	f"Welcome to the Climate app:<br/>"
        f"Available Routes:<br/><br/><br/>"
        f"/api/v1.0/precipitation<br/>Returns a JSON list of precipitation data of all stations<br/><br/>"
        f"/api/v1.0/stations<br/>Returns a JSON list of all stations<br/><br/>"
	f"/api/v1.0/tobs<br/>Returns dates and temperature observations of the most active station for the last year of data.<br/><br/>"
	f"/api/v1.0/start_date<br/>Returns calculate Temp MIN, Temp AVG, and Temp MAX for all dates greater than and equal to the start date.<br/><br/>"
	f"/api/v1.0/start_date/end_date<br/>Returns given the start and the end date, calculate the Temp MIN, Temp AVG, and Temp MAX for dates between the start and end date inclusive."
	
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Convert the query results to a dictionary using date as the key and prcp as the value."""
    # Query all passengers
    results = session.query(meas.date, meas.prcp).all()

    session.close()

     # Convert to a dictionary
    all_temps = []
    for date, prcp in results:
        temps_dict = {}
        temps_dict["date"] = date
        temps_dict["prcp"] = prcp
        all_temps.append(temps_dict)

    return jsonify(all_temps)


@app.route("/api/v1.0/stations")
def stations():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    """Return a JSON list of stations from the dataset"""
    # Query all stations
    results = session.query(meas.station).group_by(meas.station).all()
    session.close()

    # Convert to a dictionary
    all_stations = []
    for station in results:
        stations_dict = {}
        stations_dict["Station"] = station
        all_stations.append(stations_dict)

    return jsonify(all_stations)


@app.route("/api/v1.0/tobs")
def tobs():
    # Create our session (link) from Python to the DB
    session = Session(engine)

    # Query the dates and temperature observations of the most active station for the last year of data.
    results = session.query(meas.station, meas.date, meas.tobs).filter(meas.date.between('2016-08-23', '2017-08-23')).filter(meas.station=='USC00519281')
    session.close()

    # Convert to a dictionary
    top_station_temp = []
    for station, date, tobs in results:
        station_temp_dict = {}
        station_temp_dict["station"] = station
        station_temp_dict["date"] = date
        station_temp_dict["tobs"] = tobs
        top_station_temp.append(station_temp_dict)

    return jsonify(top_station_temp)

@app.route("/api/v1.0/<date>")
def start_date(date):
    # Create our session (link) from Python to the DB
    session = Session(engine)
    
    #When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
    results = session.query(func.min(meas.tobs), func.avg(meas.tobs), func.max(meas.tobs)).filter(meas.date >= date).all()

    # Convert to a dictionary
    statics_start_day = []
    for min, avg, max in results:
        statics_dict = {}
        statics_dict["Temp Min"] = min
        statics_dict["Temp Avg"] = avg
        statics_dict["Temp Max"] = max
        statics_start_day.append(statics_dict)

    return jsonify(statics_start_day)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    # Create our session (link) from Python to the DB
    session = Session(engine)

    #When given the start and the end date, calculate the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    results = session.query(func.min(meas.tobs), func.avg(meas.tobs), func.max(meas.tobs)).filter(meas.date >= start).filter(meas.date <= end).all()
    
    # Convert to a dictionary
    statics_start_end_day = []
    for min, avg, max in results:
        statics_dict = {}
        statics_dict["Temp Min"] = min
        statics_dict["Temp Avg"] = avg
        statics_dict["Temp Max"] = max
        statics_start_end_day.append(statics_dict)


    return jsonify(statics_start_end_day)


if __name__ == '__main__':
    app.run(debug=True)