import requests
import os


def register_vehicle(data):
    print('Registrando vehículo...')
    host = os.getenv('VEHICLES_MICROSERVICE_ADDRESS')
    port = os.getenv('VEHICLES_MICROSERVICE_PORT')
    
    r = requests.post('http://' + host + ':' + port + '/vehicles/register', json=data)
    
    return r.json() if r.status_code == 201 else {"Plate": "Not Available"}
