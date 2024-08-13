import requests
import os

def status0_route(data):
    host = os.getenv('ROUTES_MICROSERVICE_ADDRESS')
    port = os.getenv('ROUTES_MICROSERVICE_PORT')
    r = requests.post('http://' + host + ':' + port + '/routes/status0', json=data)
    
    return True if r.status_code == 201 else False


def finalize_route(plate, route):
    data = {"plate": plate, "destination": route["Destination"], "origin": route["Origin"], "time_stamp": route["Time Stamp"]}
    host = os.getenv('ROUTES_MICROSERVICE_ADDRESS')
    port = os.getenv('ROUTES_MICROSERVICE_PORT')
    r = requests.post('http://' + host + ':' + port + '/routes/finalize', json=data)
    
    return True if r.status_code == 201 else False
