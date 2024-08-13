import json
from math import sin, cos, radians, acos
import requests
import sys
import threading
import time
import random
import paho.mqtt.client as mqtt
import os
import datetime
import subprocess


def setup() -> None:
    global current_speed
    global dc_time
    global deceleration

    global current_ldr

    global current_obstacle_distance
    global obstacle_detected

    global current_steering

    global current_position

    global pending_routes

    global vehicle_control_commands
    global current_route_detailed_steps

    global google_maps_api_key

    global current_leds
    global turn_left
    global turn_right
    global brake_high_luminosity
    global brake_low_luminosity
    global high_luminosity
    global low_luminosity
    global leds_stop

    global STATE_TOPIC
    global PLATE_REQUEST_TOPIC
    global CONFIG_TOPIC
    global TELEMETRY_TOPIC

    global vehicle_plate

    global event_message

    # MQTT.
    STATE_TOPIC = 'fic/vehicles/' + get_host_name() + '/state'
    PLATE_REQUEST_TOPIC = 'fic/vehicles/' + get_host_name() + '/request_plate'
    CONFIG_TOPIC = 'fic/vehicles/' + get_host_name() + '/config'
    TELEMETRY_TOPIC = 'fic/vehicles/' + get_host_name() + '/telemetry'

    vehicle_plate = ''

    event_message = ''

    # Google Maps API Key.
    google_maps_api_key = 'GOOGLE_MAPS_API_KEY_GOES_HERE'

    current_position = "Not Available"

    # Detección de obstáculos.
    obstacle_detected = False

    current_speed = 0
    dc_time = 0
    deceleration = False

    pending_routes = []

    # LDR.
    current_ldr = 1000

    # Sensor de ultrasonidos.
    current_obstacle_distance = 0.0

    # Servo.
    current_steering = 90.0

    # Leds.
    turn_left = [{"Color": "Yellow", "Intensity": 100, "Blinking": 1},
                 {"Color": "White", "Intensity": 50, "Blinking": 0},
                 {"Color": "Yellow", "Intensity": 100, "Blinking": 1},
                 {"Color": "Red", "Intensity": 0, "Blinking": 0}]

    turn_right = [{"Color": "White", "Intensity": 50, "Blinking": 0},
                  {"Color": "Yellow", "Intensity": 100, "Blinking": 1},
                  {"Color": "White", "Intensity": 0, "Blinking": 0},
                  {"Color": "Yellow", "Intensity": 100, "Blinking": 1}]

    brake_high_luminosity = [{"Color": "White", "Intensity": 50, "Blinking": 0},
                             {"Color": "White", "Intensity": 50, "Blinking": 0},
                             {"Color": "Red", "Intensity": 50, "Blinking": 0},
                             {"Color": "Red", "Intensity": 50, "Blinking": 0}]

    brake_low_luminosity = [{"Color": "White", "Intensity": 100, "Blinking": 0},
                            {"Color": "White", "Intensity": 100, "Blinking": 0},
                            {"Color": "Red", "Intensity": 100, "Blinking": 0}, 
                            {"Color": "Red", "Intensity": 100, "Blinking": 0}]

    high_luminosity = [{"Color": "White", "Intensity": 50, "Blinking": 0},
                       {"Color": "White", "Intensity": 50, "Blinking": 0},
                       {"Color": "Red", "Intensity": 0, "Blinking": 0},
                       {"Color": "Red", "Intensity": 0, "Blinking": 0}]

    low_luminosity = [{"Color": "White", "Intensity": 100, "Blinking": 0},
                      {"Color": "White", "Intensity": 100, "Blinking": 0},
                      {"Color": "Red", "Intensity": 50, "Blinking": 0},
                      {"Color": "Red", "Intensity": 50, "Blinking": 0}]

    leds_stop = [{"Color": "White", "Intensity": 0, "Blinking": 0},
                 {"Color": "White", "Intensity": 0, "Blinking": 0},
                 {"Color": "Red", "Intensity": 0, "Blinking": 0},
                 {"Color": "Red", "Intensity": 0, "Blinking": 0}]

    current_leds = leds_stop


def led_controller() -> None:
    global current_leds

    while True:
        # Giro a izquierda.
        if current_steering > 100 and not obstacle_detected:
            current_leds = turn_left
        # Giro a derecha.
        elif current_steering < 80 and not obstacle_detected:
            current_leds = turn_right
        else:
            if current_ldr > 2000:
                # Frenado con luz baja.
                if deceleration and dc_time > 0:
                    current_leds = brake_low_luminosity
                # Luz baja.
                else:
                    current_leds = low_luminosity
            else:
                # Frenado con luz alta.
                if deceleration and dc_time > 0:
                    current_leds = brake_high_luminosity
                # Luz alta.
                else:
                    current_leds = high_luminosity


def execute_command(command: dict, step: dict) -> None:
    global current_speed
    global dc_time
    global current_steering
    global current_position

    global deceleration

    deceleration = True if command['Speed'] < current_speed else False

    current_steering = command['SteeringAngle']
    current_speed = command['Speed']
    dc_time = command['Time']
    time.sleep(dc_time * 3600)
    current_position = step['Destination']


def routes_loader(my_route: dict) -> None:
    global pending_routes

    pending_routes.append(json.loads(my_route))


def vehicle_controller() -> None:
    global vehicle_control_commands
    global event_message

    while True:
        while len(pending_routes) > 0:
            event_message = ''
            routes = pending_routes[0]
            routes_manager(routes['Origin'], routes['Destination'])
            while len(vehicle_control_commands) > 0:
                if not obstacle_detected:
                    command = vehicle_control_commands[0]
                    detailed_step = current_route_detailed_steps[0]

                    execute_command(command, detailed_step)

                    '''
                    print('\n' + '-' * 70)
                    print(f'Comando:\n{command}')
                    print(f'\nEntorno:\nLuz: {current_ldr}, Obstáculo: {obstacle_detected}, Distancia obstáculo: {current_obstacle_distance}')
                    print(f'\nLuces:\n{current_leds[0]}\n{current_leds[1]}\n{current_leds[2]}\n{current_leds[3]}')
                    print('-' * 70 + '\n')
                    '''

                    del vehicle_control_commands[0]
                    del current_route_detailed_steps[0]
                else:
                    '''
                    print('\n' + '-' * 70)
                    print(f'El vehículo ha detectado un obstáculo a {current_obstacle_distance} metros y se encuentra detenido.')
                    print(f'\nLuces:\n{current_leds[0]}\n{current_leds[1]}\n{current_leds[2]}\n{current_leds[3]}')
                    print('-' * 70 + '\n')
                    '''
                    time.sleep(1)
            
            route_completed = pending_routes[0]
            del pending_routes[0]
            
            json_response = json.dumps({"Plate": vehicle_plate, "Event": "Route Completed", "Timestamp": str(datetime.datetime.now()), "Route": route_completed})
            client.publish(STATE_TOPIC, payload=json_response, qos=1, retain=False)

            if len(pending_routes) == 0:
                event_message = 'Routes Completed'
                time.sleep(10)

        vehicle_stop()


def environment_simulator() -> None:
    global current_ldr
    global obstacle_detected
    global current_obstacle_distance
    global deceleration

    while True:
        if current_ldr > 0:
            current_ldr += random.uniform(-300, 300)
        else:
            current_ldr = random.uniform(0, 3000)

        if current_obstacle_distance > 0:
            current_obstacle_distance += random.uniform(-5, 5)
        else:
            current_obstacle_distance = random.uniform(0, 10)

        obstacle_detected = True if current_obstacle_distance < 10 else False
        
        if obstacle_detected:
            deceleration = True

        time.sleep(1)


def get_detailed_steps(steps):
    detailed_steps = []

    for step in steps:
        # Determinar la velocidad en escala de 100.
        step_speed = (step["distance"]["value"] / 1000) / (step["duration"]["value"] / 3600)

        # Determinar la distancia del paso.
        step_distance = step["distance"]["value"]

        # Determinar el tiempo del paso.
        step_time = step["duration"]["value"]

        # Determinar la maniobra que se tiene que ejecutar con el volante.
        try:
            step_maneuver = step["maneuver"]
        except:
            step_maneuver = "Straight"

        # Determinar los waypoints que se corresponden con ese paso.
        substeps = decode_polyline(step["polyline"]["points"])

        for index in range(len(substeps) - 1):
            p1 = {"latitude": substeps[index][0], "longitude": substeps[index][1]}
            p2 = {"latitude": substeps[index + 1][0], "longitude": substeps[index + 1][1]}
            points_distance = distance(p1, p2)
            if points_distance > 0.001:
                sub_step_duration = points_distance / step_speed
                new_detailed_step = {"Origin": p1, "Destination": p2, "Speed": step_speed,
                                        "Time": sub_step_duration, "Distance": points_distance,
                                        "Maneuver": step_maneuver}
                detailed_steps.append(new_detailed_step)

    return detailed_steps


def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''

    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']:
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index += 1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates

def distance(p1, p2):
    p1Latitude = p1["latitude"]
    p1Longitude = p1["longitude"]
    p2Latitude = p2["latitude"]
    p2Longitude = p2["longitude"]

    earth_radius = {"km": 6371.0087714, "mile": 3959}
    result = earth_radius["km"] * acos(cos((radians(p1Latitude))) * cos(radians(p2Latitude))* cos(radians(p2Longitude) - radians(p1Longitude)) + sin(radians(p1Latitude)) * sin(radians(p2Latitude)))

    return result


def get_commands(current_route_detailed_steps):
    global vehicle_control_commands
    steeringAngle: float = 90.0

    vehicle_control_commands = []
    index = 0

    for detailed_step in current_route_detailed_steps:
        index += 1

        maneuver = detailed_step["Maneuver"].replace(" ", "").replace("-", "").replace("_", "").upper()

        # print("Generando el comando {} para el paso {}".format(index, detailed_step))
        if (maneuver == "STRAIGHT" or maneuver == "RAMPLEFT" or maneuver == "RAMPRIGHT" or maneuver == "MERGE" or maneuver == "MANEUVERUNSPECIFIED"):
            steeringAngle = 90.0
        if maneuver == "TURNLEFT":
            steeringAngle = 45.0
        if maneuver == "UTURNLEFT":
            steeringAngle = 0.0
        if maneuver == "TURNSHARPLEFT":
            steeringAngle = 15.0
        if maneuver == "TURNSLIGHTLEFT":
            steeringAngle = 60.0
        if maneuver == "TURNRIGHT":
            steeringAngle = 135.0
        if maneuver == "UTURNRIGHT":
            steeringAngle = 180.0
        if maneuver == "TURN_SHARPRIGHT":
            steeringAngle = 105.0
        if maneuver == "TURN_SLIGHTRIGHT":
            steeringAngle = 150.0
        if maneuver == "ROUNDABOUTLEFT":
            steeringAngle = 45.0
        if maneuver == "ROUNDABOUTRIGHT":
            steeringAngle = 135.0

        new_command = {"SteeringAngle": steeringAngle, "Speed": detailed_step["Speed"], "Time": detailed_step["Time"]}
        vehicle_control_commands.append(new_command)


def routes_manager(origin_address="Toronto", destination_address="Montreal"):
    global current_route_detailed_steps

    print(f'Asignando ruta desde {origin_address} hasta {destination_address}.')
    url = "https://maps.googleapis.com/maps/api/directions/json?origin=" + origin_address + "&destination=" + destination_address + "&key=" + google_maps_api_key

    payload = {}
    headers = {}
    response = requests.request("GET", url, headers=headers, data=payload)
    current_route = response.text
    print(f'La ruta ha sido asignada correctamente.')

    steps = response.json()["routes"][0]["legs"][0]["steps"]
    current_route_detailed_steps = get_detailed_steps(steps)
    get_commands(current_route_detailed_steps)
    print('He acabado de asignar los comandos al vehículo.')


def vehicle_stop():
    global vehicle_control_commands
    global current_route_detailed_steps
    global current_steering
    global current_speed
    global current_leds
    global current_ldr
    global current_obstacle_distance

    vehicle_control_commands = []
    current_route_detailed_steps = []
    current_steering = 90.0
    current_speed = 0.0

    current_leds = leds_stop
    current_ldr = 0.0
    current_obstacle_distance = 0.0


def getVehicleStatus() -> dict:
    vehicle_status = {"id": get_host_name(),
                      "vehicle_plate": vehicle_plate,
                      "telemetry": {"current_steering": float(current_steering),
                                    "current_speed": current_speed,
                                    "current_position": current_position,
                                    "current_leds": current_leds,
                                    "current_ldr": current_ldr,
                                    "current_obstacle_distance": current_obstacle_distance,
                                    "vehicle_id": get_host_name(),
                                    "time_stamp": str(datetime.datetime.now())}}
    return vehicle_status


def publish_telemetry(client):
    if vehicle_plate != '' and len(current_route_detailed_steps) > 0 and current_position != "Not Available":
        vehicle_status = getVehicleStatus()
        json_telemetry = json.dumps(vehicle_status)
        client.publish(TELEMETRY_TOPIC, payload=json_telemetry, qos=1, retain=False)


def get_host_name():
    bashCommandName = 'echo $HOSTNAME'
    host = subprocess \
        .check_output(['bash', '-c', bashCommandName]) \
        .decode('utf-8')[0:-1]
    pid = str(os.getpid())
    host_with_pid = f"{host}-{pid}"
    return host_with_pid


def on_connect(client, userdata, flags, rc, properties=None):
    if rc == 0:
        client.subscribe(CONFIG_TOPIC)
        print(f'Suscrito al topic {CONFIG_TOPIC}')
        client.publish(PLATE_REQUEST_TOPIC, payload=get_host_name(), qos=1, retain=False)
        


def on_message(client, userdata, msg):
    global vehicle_plate
    print(f'Mensaje recibido: {msg.payload.decode()} en el topic {msg.topic}')

    topic = msg.topic.split('/')
    if topic[-1] == 'config':
        config_received = msg.payload.decode()
        json_config_received = json.loads(config_received)
        if json_config_received['Plate'] != 'Not Available':
            vehicle_plate = json_config_received['Plate']
            ROUTES_TOPIC = 'fic/vehicles/' + vehicle_plate + '/routes'
            client.subscribe(ROUTES_TOPIC)
            print(f'Matrícula del vehículo: {vehicle_plate}')
    elif topic[-1] == 'routes':
        required_route = msg.payload.decode()
        routes_loader(required_route)


def on_disconnect(client, userdata, flags, rc, properties=None):
    connection_dict = {"Plate": vehicle_plate, "Event": "Off - Unregular Disconnection", "Timestamp": str(datetime.time())}
    print(connection_dict)
    connection_str = json.dumps(connection_dict)
    client.will_set(STATE_TOPIC, connection_str)


def mqtt_communications():
    global client
    global event_message

    print('Iniciando message_router...')

    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=get_host_name())
    client.username_pw_set(username='admin', password='javascript')
    client.on_connect = on_connect
    client.on_message = on_message
    client.on_disconnect = on_disconnect

    MQTT_SERVER = os.getenv("MQTT_SERVER_ADDRESS")
    MQTT_PORT = int(os.getenv("MQTT_SERVER_PORT"))

    client.connect(MQTT_SERVER, MQTT_PORT, 60)

    print(f'Conectado al servidor MQTT en {MQTT_SERVER}:{MQTT_PORT}')

    client.loop_start()

    while True:
        publish_telemetry(client)

        if event_message != '':
            route_completed_dir = {"Plate": vehicle_plate, "Event": event_message, "Timestamp": str(datetime.datetime.now())}
            print(route_completed_dir)
            client.publish(STATE_TOPIC, payload=json.dumps(route_completed_dir), qos=1, retain=False)
            event_message = ''

        time.sleep(10)



if __name__ == '__main__':
    try:
        setup()
        t1 = threading.Thread(target=mqtt_communications, daemon=True)
        t1.start()
        t2 = threading.Thread(target=environment_simulator, daemon=True)
        t2.start()
        t3 = threading.Thread(target=vehicle_controller, daemon=True)
        t3.start()
        t4 = threading.Thread(target=led_controller, daemon=True)
        t4.start()
        t1.join()
        t2.join()
        t3.join()
        t4.join()
    except Exception as e:
        print(e)
        vehicle_stop()
        client.loop_stop()
