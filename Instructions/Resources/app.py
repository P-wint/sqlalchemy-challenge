import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta

from flask import Flask, jsonify

# Database setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new one
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

print(Base.classes.keys())

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station

# session link from python
session = Session(engine)

# Flask Setup
app = Flask(__name__)

# Find the most recent date in the data set.
##latest_date = (session.query(Measurement.date). order_by(Measurement.date.desc()).first())
##latest_date = list(np.ravel(latest_date))[0]

# Define what to do when a user hits the index route
@app.route("/")
def welcome():
    return (
            f"Welcome to Surf's Up! Hawaii climate API!<br/> "
            f"Available Routes:<br/>"
            f"/api/v1.0/precipitation<br/>"
            f"/api/v1.0/stations<br/>"  
            f"/api/v1.0/temperature/>"
            f"/api/v1.0/tobs</br>"   
            )

# /api/v1.0/precipitation
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Query for the dates and precipitation from the last year"""
    # Calculate the date for one year ago from last date in db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date
    precipitation = session.query(Measurement.date, Measurement.prcp)
    filter(Measurement.date >= prev_year).all()
    
    # Dict with date as the key and 
    precip = {date: prcp for date, prcp in precipitation}    
    return jsonify(precip)

    # Return a JSON list of stations from the dataset.
@app.route("/api/v1.0/stations")
def stations():
    """A list of stations"""
    results = session.query(Station.station).all()
    stations = list(np.ravel(results))
    return jsonify (stations=stations)
    
@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the dates and temperature observations from a year from the last data point."""
    # Calculate the date for one year ago from last date in db
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for tobs.
    results = session.query(Measurement.tobs).\
        filter(Measurement.station == 'USC00519281').\
        filter(Measurement.date>= prev_year).all()

    temps = list(np.ravel(results))

    # Return the results
    return jsonify(temps=temps)
    
# When given the start only, calculate TMIN, TAVG, and TMAX for all dates greater than and equal to the start date.
@app.route("/api/v1.0/<start>")
def start_date(start):
    list = []
    session = Session(engine)
    temperature = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).group_by(Measurement.date).all()

    session.close()
    for data in temperature:
        dict = {}
        dict['Date'] = data[0]
        dict['Tmin'] = data[1]
        dict['Tavg'] = round(data[2],2)
        dict['Tmax'] = data[3]
        list.append(dict)

    #Return a JSON list
    return jsonify(list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start, end):
    session = Session(engine)

    # Return a JSON list of the minimum temperature, the average temperature, and the max temperature for a given start or start-end range.
    # When given the start and the end date,  the TMIN, TAVG, and TMAX for dates between the start and end date inclusive.
    list = []
    session = Session(engine)
    temperature = session.query(Measurement.date,func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                  filter(Measurement.date >= start).filter(Measurement.date <= end).group_by(Measurement.date).all()

    session.close()
    for data in temperature:
        dict = {}
        dict['Date'] = data[0]
        dict['Tmin'] = data[1]
        dict['Tavg'] = round(data[2],2)
        dict['Tmax'] = data[3]
        list.append(dict)

    # Return a JSON list
    return jsonify(list)  

# return a JSON list of the minimum , the average, and the max temperature for a given start or start-end range
   
if __name__ == "__main__":
    app.run(debug=True)
