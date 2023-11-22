# Import the dependencies
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
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

#################################################
# Flask Setup
#################################################

app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# homepage route to show all available routes
@app.route("/")
def welcome():
    return (
        "All Available Routes:<br>"
        "/api/v1.0/precipitation<br>"
        "/api/v1.0/stations<br>"
        "/api/v1.0/tobs<br>"
        "/api/v1.0/start<br>"
        "/api/v1.0/start/end<br/>"
    )

# precipitation route to show one years worth of precipitation data
@app.route("/api/v1.0/precipitation")
def precipitation():
    session =Session(engine)

    # finding one years worth of precipitaion values
    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)
    prcp_date = session.query(measurement.date, measurement.prcp).\
        filter(measurement.date >= query_date).all()

    session.close()

    # using for loop to pull data from query variable to append from dictionary to list
    precip_list = []
    for date,prcp in prcp_date:
        precip_dict = {}
        precip_dict["date"] = date
        precip_dict["prcp"] = prcp
        precip_list.append(precip_dict)

    return jsonify(precip_list)

@app.route("/api/v1.0/stations")
def stations():
    session =Session(engine)

    # adding station id's and names to station_name
    station_name = session.query(station.station,station.name).all()

    session.close()

    # using for loop to pull data from query variable to append from dictionary to list
    station_list = []
    for station,name in station_name:
        station_dict = {}
        station_dict["station"] = station
        station_dict["name"] = name
        station_list.append(station_dict)


    return jsonify(station_list)


@app.route("/api/v1.0/tobs")
def tobs():
    session = Session(engine)

    # finding most active station and loading into a variable
    most_active = session.query(measurement.station,func.count(measurement.station)).\
        group_by(measurement.station).order_by(func.count(measurement.station).desc()).first()
    
    #calculating one year from latest point in data
    query_date = dt.date(2017,8,23) - dt.timedelta(days = 365)

    #finding one years worth of most active stations temperatures
    station_date = session.query(measurement.date, measurement.tobs, measurement.station).\
        filter(measurement.station == most_active[0]).filter(measurement.date >= query_date).all()
    
    session.close()

    # using for loop to pull data from query variable to append from dictionary to list
    temp_list = []
    for date,tobs,station in station_date:
        temp_dict = {}
        temp_dict["date"] = date
        temp_dict["tobs"] = tobs
        temp_dict["station"] = station
        temp_list.append(temp_dict)

    return jsonify(temp_list)


@app.route("/api/v1.0/<start>")
def start(start):
    session = Session(engine)

    # finding min max avg of user defined start date to end of data
    maxminavg = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
                                        filter(measurement.date >= start)

    session.close()

    # using for loop to pull data from query variable to append from dictionary to list
    start_list = []
    for min,avg,max in maxminavg:
        start_dict = {}
        start_dict['min'] = min
        start_dict['avg'] = avg
        start_dict['max'] = max
        start_list.append(start_dict)

    return jsonify(start_list)


@app.route("/api/v1.0/<start>/<end>")
def startend(start,end):
    session = Session(engine)

    #finding min max average of user defined timeframe
    maxminavg = session.query(func.min(measurement.tobs),func.max(measurement.tobs),func.avg(measurement.tobs)).\
                    filter(measurement.date >= start).filter(measurement.date <= end).all()

    session.close()

    # using for loop to pull data from query variable to append from dictionary to list
    startend_list = []
    for min,avg,max in maxminavg:
        startend_dict = {}
        startend_dict['min'] = min
        startend_dict['avg'] = avg
        startend_dict['max'] = max
        startend_list.append(startend_dict)
    
    return jsonify(startend_list)


if __name__ == '__main__':
    app.run(debug=True)
