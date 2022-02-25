import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt

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
    print("Server received request for Home page...")
    return (
    f"Welcome to the Hawaii Climate API!<br/>"
    f"Available paths:<br/>"
    f"/api/v1.0/precipitation<br/>"
    f"/api/v1.0/stations<br/>"
    f"/api/v1.0/tobs<br/>"
    f"/api/v1.0/<tstart><br/>"
    f"/api/v1.0/<tstart>/<tend><br/>"
    ) 

@app.route("/api/v1.0/precipitation")
def precipitation():
    print("Server received request for Precipitation...")

    session = Session(engine)

    results = session.query(Measurement.date, Measurement.prcp).all()

    session.close()

    all_prcp = []
    for date, prcp in results:
        prcp_dict = {}
        prcp_dict["date"] = date
        prcp_dict["prcp"] = prcp
        all_prcp.append(prcp_dict)

    return jsonify(all_prcp)

@app.route("/api/v1.0/stations")
def stations():
    print("Server received request for Stations...")

    session = Session(engine)

    results = session.query(Station.station, Station.name).all()

    session.close()

    all_stations = list(np.ravel(results))
    
    return jsonify(all_stations)

@app.route("/api/v1.0/tobs")
def tobs():
    print("Server received request for Observed Tempertures")

    session = Session(engine)

    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)

    results = session.query(Measurement.tobs).\
    filter(Measurement.date >= query_date).\
    filter(Measurement.station == 'USC00519281').all()

    session.close()

    tobs_year = list(np.ravel(results))
    
    return jsonify(tobs_year)

# @app.route("/api/v1.0/<tstart>")
# def tstart(tstart= None):
# Just thought I'd keep the fact that you can set parameter to none, sorry Zayna not me
# realizing what I was doing wrong after you helped get to a solution with what I had...

@app.route("/api/v1.0/<tstart>")
def inputstart(tstart):
    print("Server received Start Date request for TMIN, TMAX, & TAVG")

    session = Session(engine)

    user_start = dt.datetime.strptime(tstart,"%Y-%m-%d")
    datediff = user_start - dt.timedelta(days=365)
    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= datediff).all()

    session.close()

    t_values = list(np.ravel(results))

    return jsonify(t_values)

@app.route("/api/v1.0/<tstart>/<tend>")
def inputstartend(tstart, tend):
    print("Server received Start and End Date request for TMIN, TMAX, & TAVG")

    session = Session(engine)

    user_start = dt.datetime.strptime(tstart,"%Y-%m-%d")
    user_end = dt.datetime.strptime(tend,"%Y-%m-%d")

    results = session.query(func.min(Measurement.tobs), func.max(Measurement.tobs), func.avg(Measurement.tobs)).\
    filter(Measurement.date >= user_start).\
    filter(Measurement.date <= user_end).all()
    
    session.close()

    t_startend_values = list(np.ravel(results))

    return jsonify(t_startend_values)
 
if __name__ == "__main__":
    app.run(debug=True)