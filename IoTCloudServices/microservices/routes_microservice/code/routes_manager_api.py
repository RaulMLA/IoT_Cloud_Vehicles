import os
from flask import Flask, request
from flask_cors import CORS
import routes_db_manager

app = Flask(__name__)
CORS(app)

@app.route('/routes/assign/', methods=['POST'])
def assign_route():
    params = request.get_json()

    result = routes_db_manager.assign_new_route(params)
    
    if result:
        params["time_stamp"] = result[1]
        if routes_db_manager.send_route(params):
            return {"result": "Route assigned"}, 201
        else:
            return {"result": "Error sending the route"}, 500
    else:
        return {"result": "Error assigning a new route"}, 500


@app.route('/routes/retrieve/', methods=['GET'])
def retrieve_routes():
    params = request.get_json()

    result = routes_db_manager.get_routes_assigned_to_vehicle(params)

    if result["Error Message"] is None:
        return {"result": result["Result"]}, 201
    else:
        return {"result": result["Error Message"]}, 500
    

@app.route('/routes/finalize/', methods=['POST'])
def finalize_route():
    params = request.get_json()

    result = routes_db_manager.finalize_route(params)

    if result:
        return {"result": "Route finalized"}, 201
    else:
        return {"result": "Error finalizing the route"}, 500


@app.route('/routes/status0/', methods=['POST'])
def status0_route():
    params = request.get_json()

    result = routes_db_manager.set_status_0_vehicle(params)

    if result:
        return {"result": "Set status 0 completed"}, 201
    else:
        return {"result": "Error setting status 0"}, 500



if __name__ == '__main__':
    HOST = os.getenv('HOST')
    PORT = os.getenv('PORT')
    
    app.run(host=HOST, port=PORT)
