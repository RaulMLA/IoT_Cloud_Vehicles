import subprocess
from flask import Flask, request
from flask_cors import CORS
import json
import random
import threading
import paho.mqtt.client as mqtt
import os
import time

from telemetry_register_interface import register_telemetry
from vehicle_register_interface import register_vehicle
from routes_assign_interface import status0_route, finalize_route


def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
        .check_output(['bash', '-c', bashCommandName]) \
        .decode('utf-8')[0:-1]
    pid = str(os.getpid())
    host_with_pid = f"{host}-{pid}"
    return host_with_pid


def connect_to_mqtt():
    global client

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id='message_router')
    client.username_pw_set(username='admin', password='javascript')
    client.on_connect = on_connect
    client.on_message = on_message

    MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
    MQTT_PORT = int(os.getenv("MQTT_SERVER_PORT"))

    client.connect(MQTT_SERVER, MQTT_PORT, 60)

    print(f'Conectado al servidor MQTT en {MQTT_SERVER}:{MQTT_PORT}')

    client.loop_forever()
    
    
def on_connect(client, userdata, flags, rc, properties=None):
    STATE_TOPIC = 'fic/vehicles/+/state'
    REQUEST_PLATE_TOPIC = 'fic/vehicles/+/request_plate'
    TELEMETRY_TOPIC = 'fic/vehicles/+/telemetry'

    if rc == 0:
        client.subscribe(REQUEST_PLATE_TOPIC)
        client.subscribe(TELEMETRY_TOPIC)
        client.subscribe(STATE_TOPIC)
        
        print('Suscrito a los topics:')
        print(f' - {REQUEST_PLATE_TOPIC}')
        print(f' - {TELEMETRY_TOPIC}')
        print(f' - {STATE_TOPIC}')


def on_message(client, userdata, msg):
    #  Imprimir por pantalla el mensaje recibido desde el broker.
    #print(f'Mensaje recibido en el topic {msg.topic}: {msg.payload.decode()}')

    # Se comprueba el topic del mensaje que se ha recibido incluye request_plate.
    topic = msg.topic.split('/')
    if topic[-1] == 'request_plate':
        input_data = msg.payload.decode()
        request_data = {"vehicle_id":input_data}
        vehicle_plate = register_vehicle(request_data)
        client.publish("fic/vehicles/" + msg.payload.decode() + "/config", payload=json.dumps(vehicle_plate), qos=1, retain=False)

        print("Publicado", vehicle_plate, "en TOPIC", msg.topic)

    # Se comprueba el topic del mensaje que se ha recibido incluye telemetry.
    elif topic[-1] == 'telemetry':
        received_telemetry = json.loads(msg.payload.decode())
        while not register_telemetry(received_telemetry):
            print('Error al registrar la telemetría. Reintentando...')
            time.sleep(5)
                
    # Ruta completada.
    elif topic[-1] == 'state':
        vehicle_id = topic[2]
        message_payload = json.loads(msg.payload.decode())
        if message_payload['Event'] == 'Route Completed':
            finalize_route(message_payload['Plate'], message_payload['Route'])
            print(f'Vehículo {vehicle_id} ha completado la ruta.')
        elif message_payload['Event'] == 'Routes Completed':
            print(f'El vehículo {vehicle_id} ha completado todas las rutas.')
            status0_route({"Plate": message_payload['Plate']})



if __name__ == '__main__':
    try:
        mqtt_thread = threading.Thread(target=connect_to_mqtt, daemon=True)
        mqtt_thread.start()

        app = Flask(__name__)
        CORS(app)

        @app.route('/routes/send/', methods=['POST'])
        def send_route():
            try:
                params = request.get_json()
                route = {"Origin": params["origin"], "Destination": params["destination"], "Time Stamp": str(params["time_stamp"])}
                client.publish("fic/vehicles/" + params["plate"] + "/routes", payload=json.dumps(route), qos=1, retain=False)
                return {"Result": "Route successfully sent"}, 201
            except:
                return {"Result": "Internal Server Error"}, 500
        
        HOST = os.getenv('HOST')
        PORT = os.getenv('PORT')
        
        app.run(host=HOST, port=PORT)

        mqtt_thread.join()

    except Exception as e:
        print(e)
