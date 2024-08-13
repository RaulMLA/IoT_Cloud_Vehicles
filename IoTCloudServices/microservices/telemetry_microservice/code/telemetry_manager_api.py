import os
from flask import Flask, request
from flask_cors import CORS
import telemetry_db_manager

app = Flask(__name__)
CORS(app)

@app.route('/telemetry/register/', methods=['POST'])
def register_telemetry():
    params = request.get_json()
    result = telemetry_db_manager.register_new_telemetry(params['telemetry'])

    if result:
        return {"result": "Telemetry registered"}, 201
    else:
        return {"result": "Error registering telemetries "}, 500


@app.route('/telemetry/vehicle/detailed_info/', methods=['GET'])
def detailed_info():
    params = request.get_json()
    result = telemetry_db_manager.get_vehicle_detailed_info(params)

    if result["Error Message"] is None:
        return result, 201
    else:
        return result, 500


@app.route('/telemetry/vehicle/positions/', methods=['GET'])
def vehicle_positions():
    result = telemetry_db_manager.get_vehicles_last_position()

    if result["Error Message"] is None:
        return result, 201
    else:
        return result, 500



if __name__ == '__main__':
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    
    app.run(host=HOST, port=PORT)
