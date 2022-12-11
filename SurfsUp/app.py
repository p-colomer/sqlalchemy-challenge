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

engine = create_engine("sqlite:///./Resources/hawaii.sqlite", echo=False)

#reflect the database into our classes
Base = automap_base()
Base.prepare(engine, reflect = True)
Measurement = Base.classes.measurement
Station = Base.classes.station

session = Session(engine)

latest_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
end_date = session.query(Measurement.date).order_by(Measurement.date).first()

session.close()

# Convertin strings to dates 
start_date_dt = dt.datetime.strptime(latest_date[0], '%Y-%m-%d').date()
start_dt_last_yr = start_date_dt - dt.timedelta(days=365)
date_last_yr = start_dt_last_yr.strftime('%Y-%m-%d')



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

# create precipitation route of last 12 months of precipitation data
@app.route("/api/v1.0/precipitation")
def precip():

    session = Session(engine)

    recent_prcp = session.query((Measurement.date), Measurement.prcp).filter(Measurement.date > '2016-08-22').filter(Measurement.date <= '2017-08-23').order_by(Measurement.date).all()

    session.close()
    # convert results to a dictionary with date as key and prcp as value
    prcp_dict = dict(recent_prcp)

    
    return jsonify(prcp_dict)


# create station route of a list of the stations in the dataset
@app.route("/api/v1.0/stations")
def stations():

    session = Session(engine)

    stations = session.query(Station.name, Station.station).all()

    session.close()

    # convert results to a dict
    stations_dict = dict(stations)

    
    return jsonify(stations_dict)


# create tobs route of temp observations for most active station over last 12 months
@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)

    tobs_station = session.query((Measurement.date), Measurement.tobs)\
    .filter(Measurement.date > '2016-08-23')\
    .filter(Measurement.date <= '2017-08-23')\
    .filter(Measurement.station == "USC00519281")\
    .order_by(Measurement.date).all()

    session.close()

    # convert results to dict
    tobs_dict = dict(tobs_station)
    
    return jsonify(tobs_dict)


# create start and start/end route
# min, average, and max temps for a given date range
@app.route("/api/v1.0/<start>")
@app.route("/api/v1.0/<start>/<end>")
def start_date(start, end=None):

    session = Session(engine)

    if start > latest_date[0] or (end !=None and end < end_date[0]):
        return ("Invalid Input Dates")
    else:
        if end:
            temp_calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).filter(Measurement.date <= end).all()
        else:
            temp_calc = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
                filter(Measurement.date >= start).all()

    session.close()

    temp_data = []
    for min, avg, max in temp_calc:
        temp_dict = {}
        temp_dict["Minimum Temperature"] = min
        temp_dict["Maximum Temperature"] = max
        temp_dict["Average Temperature"] = avg
        
    temp_dict["Start Date"] = start
    if end:
        temp_dict["End Date"] = end
    else:
        temp_dict["End Date"] = latest_date[0]
    temp_data.append(temp_dict)

    
    return jsonify(temp_data)


if __name__ == "__main__":
    app.run(debug=True)