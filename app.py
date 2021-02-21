# Set up
import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

# Database set up
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

Base = automap_base()
Base.prepare(engine, reflect=True)

# save variables
Measurement = Base.classes.measurement
Station = Base.classes.station

# create app
session = Session(engine)
app = Flask(__name__)

# To keep order in dictionary when passing jsonify function
app.config['JSON_SORT_KEYS'] = False


# homepage

@app.route("/")
def welcome():
    """List all available api routes."""
    return """
        <b>Available Routes:</b><br/>
        /api/v1.0/precipitation<br/>
        /api/v1.0/stations<br/>
        /api/v1.0/tobs<br/>
        /api/v1.0/YYYY-MM-DD<br/>
        /api/v1.0/YYYY-MM-DD/YYYY-MM-DD<br/>
        """


# precipitation route

@ app.route("/api/v1.0/precipitation")
def precipitation():
    # Query precipitation data
    results = session.query(Measurement.date, Measurement.prcp).all()

    # Create a dictionary from the row data and return

    precipitation = []
    for date, prcp in results: 
        precip_dict = {}
        precip_dict["Date"] = date
        precip_dict["Precipitation"] = prcp
        precipitation.append(precip_dict)

    return jsonify(precipitation)


# Stations route

@app.route("/api/v1.0/stations")  
def stations():

    """Return a list of all stations"""
    #Query station table 
    results = session.query(Station.station, Station.name).all()

    stations = []
    for station, name in results: 
        station_dict = {}
        station_dict["Station ID"] = station
        station_dict["Station Name"] = name
        stations.append(station_dict)

    return jsonify(stations)    


# TOBS route

#Query the dates and temperature observations 
#of the most active station for the last year of data.
#Return a JSON list of temperature observations (TOBS) 
#for the previous year.
@app.route("/api/v1.0/tobs")
def active_temps():

    """Return a list of the temp observations for the most active station of the last year"""
    # Calculate the date 1 year from last data point
    query_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()

    format_query_date = dt.date(2017, 8, 23) - dt.timedelta(days=365)


    # find the station with the highest number of temp observations
    most_temps = session.query(Measurement.station, func.count(Measurement.tobs))\
                                .group_by(Measurement.station)\
                                .order_by(func.count(Measurement.tobs).desc())\
                                .first()
    most_temps_id = most_temps[0]

    # query the last 12 months of temp observation data for this station
    results = session.query(Measurement.date, Measurement.tobs).\
                    filter(Measurement.date >= format_query_date).\
                    filter(Measurement.station == most_temps_id).\
                    order_by(Measurement.date).all()

    temps = []
    for station, tobs in results: 
        temps_dict = {}
        temps_dict["Station ID"] = most_temps_id
        temps_dict["Temperature"] = tobs
        temps.append(temps_dict)

    return jsonify(temps)

#Return a JSON list of the minimum temperature, the average temperature, 
#and the max temperature for a given start or start-end range.

#When given the start only, calculate TMIN, TAVG, and TMAX 
#for all dates greater than and equal to the start date.

#When given the start and the end date, calculate the TMIN, TAVG, and TMAX 
#for dates between the start and end date inclusive.

@app.route("/api/v1.0/<start>")
def date_temps(start):

    """Return a list of min, avg and max temp for a given start date"""

# query tmin, tavg and tmax for all dates greater than or equal to the start date
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).all()

    date_temps = []   
    for temp in results: 
        dt_dict = {}
        dt_dict["Min Temp"] = temps[1] 
        dt_dict["Avg Temp"] = temps[2]
        dt_dict["Max Temp"] = temps[3]   
        date_temps.append(dt_dict) 

    return jsonify(date_temps)            

@app.route("/api/v1.0/<start>/<end>")
def date_range_temps(start, end):
   

    """Return a list of min, avg, and max temp for a user defined start and end date"""

# query tmin, tavg, and tmax for dates between the start and end date
    results = session.query(Measurement.date, func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                    filter(Measurement.date >= start).\
                    filter(Measurement.date <= end).all()

    date_range_temps = []   
    for temp in results: 
        dt_range_dict = {}
        dt_range_dict["Min Temp"] = temps[1] 
        dt_range_dict["Avg Temp"] = temps[2]
        dt_range_dict["Max Temp"] = temps[3]   
        date_range_temps.append(dt_range_dict) 

    return jsonify(date_range_temps)       


# app.run statement
if __name__ == "__main__":
    app.run(debug=True)