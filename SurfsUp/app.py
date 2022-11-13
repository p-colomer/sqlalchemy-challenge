import datetime as dt
import numpy as np
import pandas as pd

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from sqlalchemy.sql import exists  

from flask import Flask, jsonify


#create the engine

engine = create_engine("sqlite:///Resources/hawaii.sqlite", echo=False)

#reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

#define the app
app = Flask(__name__)

#step 5: define the routes
@app.route("/")
def welcome():
    return(
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start (enter as YYYY-MM-DD)<br/>"
        f"/api/v1.0/start/end (enter as YYYY-MM-DD/YYYY-MM-DD)"
    )

@# create precipitation route of last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precip():

    recent_prcp = session.query(str(Measurement.date), Measurement.prcp)\
    .filter(Measurement.date > '2016-08-22')\
    .filter(Measurement.date <= '2017-08-23')\
    .order_by(Measurement.date).all()

    # convert results to a dictionary with date as key and prcp as value
    prcp_dict = dict(recent_prcp)

    # return json list of dictionary
    return jsonify(prcp_dict)


# create station route of a list of the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():

    stations = session.query(Station.name, Station.station).all()

    # convert results to a dict
    stations_dict = dict(stations)

    # return json list of dict (I decided to do a dict instead of a list here to show both the station name and the station number)
    return jsonify(stations_dict)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():

    tobs_station = session.query(str(Measurement.date), Measurement.tobs)\
    .filter(Measurement.date > '2016-08-23')\
    .filter(Measurement.date <= '2017-08-23')\
    .filter(Measurement.station == "USC00519281")\
    .order_by(Measurement.date).all()

    # convert results to dict(I decided to to a dict here instead of a list in order to show the dates along with the temperature for each date)
    tobs_dict = dict(tobs_station)

    # return json list of dict
    return jsonify(tobs_dict)


# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):

    q = session.query(str(func.min(Measurement.tobs)), str(func.max(Measurement.tobs)), str(func.round(func.avg(Measurement.tobs))))

    if start:
        q = q.filter(Measurement.date >= start)

    if end:
        q = q.filter(Measurement.date <= end)

    # convert results into a dictionary (I opted for a dictionary instead of a list here so that it was clear with labels which temp was the min, the max, and the average)

    results = q.all()[0]

    keys = ["Min Temp", "Max Temp", "Avg Temp"]

    temp_dict = {keys[i]: results[i] for i in range(len(keys))}

    return jsonify(temp_dict)


if __name__ == "__main__":
    app.run(debug=True)