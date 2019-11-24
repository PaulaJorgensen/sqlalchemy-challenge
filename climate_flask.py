import datetime as dt
import numpy as np

import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func

from flask import Flask, jsonify

engine = create_engine("sqlite:///Resources/hawaii.sqlite") 
Base = automap_base()
Base.prepare(engine, reflect=True)
Measurement = Base.classes.measurement
Station = Base.classes.station
session = Session(engine)

app = Flask(__name__)

@app.route("/")
def Welcome():
    return (
        f"Data Range is from 8/23/2016 thru 8/23/2017.<br><br>"
        f"Available Routes: <br>"
        f"/api/v1.0/precipitation<br/>"
        f"Returns percipitation data for the data range.<br><br>"
        f"/api/v1.0/stations<br/>"
        f"Returns data on all the weather stations in Hawaii. <br><br>"
        f"/api/v1.0/tobs<br/>"
        f"Returns temperature data for the most active weather station (USC00519281).<br><br>"
        f"/api/v1.0/<date>date<br/>"
        f"Returns an Average, Max, and Min temperature for a given start date. <br><br>"
        f"/api/v1.0/<startdate>startdate/<enddate>enddate<br/>"
        f"Returns an Average, Max, and Min temperatures for a given date range."
    )
      
@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)
    curr_year=dt.date(2017, 8, 23)
    prev_year = curr_year - dt.timedelta(days=365)
    
    prcp=session.query(Measurement.date, func.sum(Measurement.prcp)).\
        filter(Measurement.prcp != None).filter(Measurement.date>=prev_year).\
            group_by(Measurement.date).all()
    session.close()

    prcp_data = []
    for d,p in prcp:
        prcp_dict = {}
        prcp_dict["date"] = d
        prcp_dict["prcp"] = p
        prcp_data.append(prcp_dict)
    return jsonify(prcp_data)
    
@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    """Return a list of stations."""
    results = session.query(Station.station, Station.name, Station.elevation, Station.latitude, Station.longitude).all()
    
    session.close()
    
    station_list = []
    for result in results:
        row = {}
        row['station'] = result[0]
        row['name'] = result[1]
        row['elevation'] = result[2]
        row['latitude'] = result[3]
        row['longitude'] = result[4]
        station_list.append(row)
    return jsonify(station_list)

@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    curr_year=dt.date(2017, 8, 23)
    prev_year = curr_year - dt.timedelta(days=365)
    
    temps = session.query(Measurement.tobs).\
    filter(Measurement.station == 'USC00519281').\
    filter(Measurement.date >= prev_year).all()

    session.close()
    
    temp_list = list(np.ravel(temps))
    return jsonify(temp_list)

@app.route("/api/v1.0/<date>")
def date(date):
    session = Session(engine)

    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=date).all()

    session.close()
    
    date_temp=list(np.ravel(results))

    t_min=date_temp[0]
    t_avg=date_temp[1]
    t_max=date_temp[2]
    t_dict = {'Minimum Temperature': t_min, 'Average Temperature': t_avg, 'Maximum Temperature': t_max}
    return jsonify(t_dict)

@app.route("/api/v1.0/<startdate>/<enddate>")
def start_end_date(startdate,enddate):
    session=Session(engine)
    print(startdate)

    results=session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
        filter(Measurement.date>=startdate).\
        filter(Measurement.date<=enddate).all()

    session.close()
    print(jsonify(results))
    date_temp=list(np.ravel(results))

    t_min=date_temp[0]
    t_avg=date_temp[1]
    t_max=date_temp[2]
    t_dict = {'Minimum Temperature': t_min, 'Average Temperature': t_avg, 'Maximum Temperature': t_max}
    return jsonify(t_dict)

if __name__ == '__main__':
    app.run(debug=True)
