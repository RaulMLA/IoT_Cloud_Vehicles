import mysql.connector
import os

def register_new_telemetry(params):
    connect_database()

    sql = 'INSERT INTO vehicles_telemetry (vehicle_id, current_steering, current_speed, latitude, longitude, current_ldr, current_obstacle_distance, front_left_led_intensity, front_right_led_intensity, rear_left_led_intensity, rear_right_led_intensity, front_left_led_color, front_right_led_color, rear_left_led_color, rear_right_led_color, front_left_led_blinking, front_right_led_blinking, rear_left_led_blinking, rear_right_led_blinking, time_stamp) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);'
    values = (params["vehicle_id"],
              params["current_steering"],
              params["current_speed"],
              params["current_position"]["latitude"],
              params["current_position"]["longitude"],
              params["current_ldr"],
              params["current_obstacle_distance"],
              params["current_leds"][0]["Intensity"],
              params["current_leds"][1]["Intensity"],
              params["current_leds"][2]["Intensity"],
              params["current_leds"][3]["Intensity"],
              params["current_leds"][0]["Color"],
              params["current_leds"][1]["Color"],
              params["current_leds"][2]["Color"],
              params["current_leds"][3]["Color"],
              params["current_leds"][0]["Blinking"],
              params["current_leds"][1]["Blinking"],
              params["current_leds"][2]["Blinking"],
              params["current_leds"][3]["Blinking"],
              params["time_stamp"])
    
    
    try:
        with mydb.cursor() as mycursor:
            mycursor.execute(sql, values)
            mydb.commit()
            mydb.close()
            return True
    except:
        mydb.rollback()
        mydb.close()
        return False


def get_vehicle_detailed_info(params):
    connect_database()

    sql = 'SELECT vehicle_id, current_steering, current_speed, current_ldr, \
           current_obstacle_distance, front_left_led_intensity, \
           front_right_led_intensity, rear_left_led_intensity, \
           rear_right_led_intensity, front_left_led_color, \
           front_right_led_color, rear_left_led_color, rear_right_led_color, \
           front_left_led_blinking, front_right_led_blinking, \
           rear_left_led_blinking, rear_right_led_blinking, time_stamp FROM \
           vehicles_telemetry WHERE vehicle_id = %s ORDER BY time_stamp LIMIT 20'

    result = []

    my_cursor = mydb.cursor()
    my_cursor.execute(sql, (params["vehicle_id"],))
    my_result = my_cursor.fetchall()
    mydb.close()

    if len(my_result) == 0:
        return {"Error Message": "No data found for vehicle_id: " + params["vehicle_id"]}

    for vehicle_id, current_steering, current_speed, current_ldr, \
        current_obstacle_distance, front_left_led_intensity, \
        front_right_led_intensity, rear_left_led_intensity, \
        rear_right_led_intensity, front_left_led_color, front_right_led_color, \
        rear_left_led_color, rear_right_led_color, front_left_led_blinking, \
        front_right_led_blinking, rear_left_led_blinking, rear_right_led_blinking, \
        time_stamp in my_result:

        item = {"Vehicle_id": vehicle_id,
                "Current Steering": current_steering,
                "Current Speed": current_speed,
                "Current LDR": current_ldr,
                "Obstacle Distance":current_obstacle_distance,
                "Front Left Led Intensity": front_left_led_intensity,
                "Front Right Led Intensity": front_right_led_intensity,
                "Rear Left Led Intensity": rear_left_led_intensity,
                "Rear Right Led Intensity": rear_right_led_intensity,
                "Front Left Led Color": front_left_led_color, 
                "Front Right Led Color": front_right_led_color,
                "Rear Left Led Color": rear_left_led_color,
                "Rear Right Led Color": rear_right_led_color,
                "Front Left Led Blinking": front_left_led_blinking,
                "Front Right Led Blinking": front_right_led_blinking,
                "Rear Left Led Blinking": rear_left_led_blinking,
                "Rear Right Led Blinking": rear_right_led_blinking,
                "Time Stamp": time_stamp}
        
        result.append(item)
        
    return {"Error Message": None, "Result": result}



def get_vehicles_last_position():
    connect_database()

    sql = 'SELECT vehicles.vehicle_id, plate, latitude, longitude, time_stamp FROM \
           vehicles, vehicles_telemetry WHERE \
           vehicles.vehicle_id=vehicles_telemetry.vehicle_id AND status = 1 \
           AND time_stamp = (SELECT MAX(time_stamp) FROM vehicles_telemetry WHERE vehicles_telemetry.vehicle_id = vehicles.vehicle_id)'
    
    result = []

    my_cursor = mydb.cursor()
    my_cursor.execute(sql)
    my_result = my_cursor.fetchall()
    mydb.close()

    if len(my_result) == 0:
        return {"Error Message": "No data found"}

    for vehicle_id, plate, latitude, longitude, time_stamp in my_result:
        item = {"Vehicle_id": vehicle_id,
                "Plate": plate,
                "Latitude": latitude,
                "Longitude": longitude,
                "Time Stamp": time_stamp}
        
        result.append(item)
        
    return {"Error Message": None, "Result": result}



def connect_database():
    global mydb
    
    mydb = mysql.connector.connect(
        host=os.getenv('DBHOST'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPASSWORD'),
        database=os.getenv('DBDATABASE')
    )
    return mydb
