import numpy as np
import datetime as dt
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from dateutil.relativedelta import relativedelta
from flask import Flask, jsonify

#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///resources/hawaii.sqlite")

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
def root():
    """List all available api routes."""
    return (
        f"Available Routes:<br/>"
        f"/precipitation<br/>"
        f"/stations<br/>"
        f"/tobs<br/>"
        f"/&lt;start&gt;<br/>"
        f"/&lt;start&gt;/&lt;end&gt;<br/>"
    )

@app.route("/precipitation")

def precipitation():
    session = Session(engine)
 
    # Year ago date from jupyter notebook
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    max_date1 = dt.datetime.strptime(max_date, '%Y-%m-%d')
    latest_twelve = max_date1 - relativedelta(years=1)

    # All of the data retrieved same as jupyter notebook
    results = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date>=latest_twelve.date()).filter(Measurement.date<=max_date1.date()).order_by(Measurement.date).all()

    session.close()

    precip = []
    for date, prcp in results:
        pre_dict = {}
        pre_dict["date"] = date
        pre_dict["prcp"] = prcp
        precip.append(pre_dict)

    return jsonify(precip)


@app.route("/stations")
def stations():   
    #Returns all the stations as JSON

    session = Session(engine)

    #all stations
    stations = session.query(Measurement.station).group_by(Measurement.station).all()

    session.close()

    all_stations = list(np.ravel(stations))

    return jsonify(all_stations)


@app.route("/tobs")
def tobs(): 
		#Query the dates and temperature observations of the most active station for the last year of data.
    #Return a JSON list of temperature observations (TOBS) for the previous year.

    session = Session(engine)

    # Year ago date from jupyter notebook
    max_date = session.query(Measurement.date).order_by(Measurement.date.desc()).first()
    max_date = max_date[0]

    max_date1 = dt.datetime.strptime(max_date, '%Y-%m-%d')
    latest_twelve = max_date1 - relativedelta(years=1)

    sta_results = session.query(Measurement.date, Measurement.tobs).filter(Measurement.date>=latest_twelve.date()).filter(Measurement.date<=max_date1.date()).filter(Measurement.station == "USC00519281").order_by(Measurement.date).all()

    session.close()

    tobs_all = []
    for date, tobs in sta_results:
        tobs_dict = {
            "date" : date,
            "tobs" : tobs
        }
        tobs_all.append(tobs_dict)

    return jsonify(tobs_all)


@app.route("/start/<start_dt>")
#tmp_low = session.query(func.min(Measurement.tobs)).filter(Measurement.station == 'USC00519281').all()
#tmp_low = tmp_low[0][0]

#tmp_high = session.query(func.max(Measurement.tobs)).filter(Measurement.station == 'USC00519281').all()
#tmp_high = tmp_high[0][0]

#tmp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.station == 'USC00519281').all()
#tmp_avg = tmp_avg[0][0]
def start(start_dt):
    session = Session(engine)
    start_dt = dt.datetime.strptime(start_dt, '%Y-%m-%d')

    tmp_low = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).all()
    tmp_low = tmp_low[0][0]
    tmp_high = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).all()
    tmp_high = tmp_high[0][0]
    tmp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).all()
    tmp_avg = round(tmp_avg[0][0], 1)
    
    session.close()

    all_temps = {
        "Min Temp" : tmp_low,
        "Max Temp" : tmp_high,
        "Avg Temp" : tmp_avg
    }    
    return jsonify(all_temps)

@app.route("/<start_dt>/<end_dt>")
def start_end_date(start_dt, end_dt):

    session = Session(engine)
    start_dt = dt.datetime.strptime(start_dt, '%Y-%m-%d')
    end_dt = dt.datetime.strptime(end_dt, '%Y-%m-%d')

    tmp_low = session.query(func.min(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).filter(Measurement.date<=end_dt.date()).all()
    tmp_low = tmp_low[0][0]
    tmp_high = session.query(func.max(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).filter(Measurement.date<=end_dt.date()).all()
    tmp_high = tmp_high[0][0]
    tmp_avg = session.query(func.avg(Measurement.tobs)).filter(Measurement.date>=start_dt.date()).filter(Measurement.date<=end_dt.date()).all()
    tmp_avg = round(tmp_avg[0][0], 1)
    
    session.close()

    all_temps = {
        "Min Temp" : tmp_low,
        "Max Temp" : tmp_high,
        "Avg Temp" : tmp_avg
    }    
    return jsonify(all_temps)



if __name__ == '__main__':
    app.run(debug=True)
    