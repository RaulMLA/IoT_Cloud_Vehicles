import os
from flask import Flask, request
from flask_cors import CORS
import vehicles_db_manager

app = Flask(__name__)
CORS(app)

@app.route('/vehicles/register/', methods=['POST'])
def register_vehicle():
    params = request.get_json()
    plate = vehicles_db_manager.register_new_vehicle(params)
    
    if plate:
        return {"Plate": plate}, 201
    else:
        return {"result": "error inserting a new vehicle"}, 500


@app.route('/vehicles/retrieve/', methods=['GET'])
def retrieve_vehicles():
    vehicles = vehicles_db_manager.get_active_vehicles()
    
    if vehicles:
        return {"Vehicles": vehicles}, 201
    else:
        return {"result": "error retrieving vehicles"}, 500



if __name__ == '__main__':
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    
    app.run(host=HOST, port=PORT)
