import datetime
import mysql.connector
import os

import requests


def assign_new_route(params):
    connect_database()

    sql = 'INSERT INTO routes (origin, destination, plate, time_stamp, done) VALUES (%s, %s, %s, %s, %s);'
    sql_2 = 'UPDATE vehicles SET status=1 WHERE plate=%s;'
    
    tuples = (params["origin"], params["destination"], params["plate"], str(datetime.datetime.now()), 0)

    try:
        with mydb.cursor() as mycursor:
            mycursor.execute(sql, tuples)
            mycursor.execute(sql_2, (params["plate"],))
            mydb.commit()
            mydb.close()
            return True, tuples[3]
    except:
        mydb.rollback()
        mydb.close()
        return False
    

def send_route(data):
    host = os.getenv('MESSAGE_ROUTER_ADDRESS')
    port = os.getenv('MESSAGE_ROUTER_PORT')
    r = requests.post('http://' + host + ':' + port + '/routes/send', json=data)

    return True if r.status_code == 201 else False


def finalize_route(params):
    connect_database()

    sql = 'UPDATE routes SET done=1 WHERE plate = %s AND time_stamp = %s;'
    params["time_stamp"] = params["time_stamp"][:-7]

    try:
        with mydb.cursor() as mycursor:
            mycursor.execute(sql, (params["plate"], params["time_stamp"]))
            mydb.commit()
            mydb.close()
            return True
    except:
        mydb.rollback()
        mydb.close()
        return False


def get_routes_assigned_to_vehicle(params):
    connect_database()

    sql = 'SELECT * FROM routes WHERE plate = %s'

    result = []

    my_cursor = mydb.cursor()
    my_cursor.execute(sql, (params["Plate"],))
    my_result = my_cursor.fetchall()

    if len(my_result) == 0:
        return {"Error Message": "No data found"}
    
    for id, origin, destination, plate, time_stamp, done in my_result:
        item = {"Origin": origin,
                "Destination": destination,
                "Plate": plate,
                "Time Stamp": time_stamp,
                "Done": done}
        
        result.append(item)

    mydb.close()

    return {"Error Message": None, "Result": result}


def set_status_0_vehicle(params):
    connect_database()

    sql = 'UPDATE vehicles SET status = 0 WHERE plate = %s;'

    try:
        with mydb.cursor() as mycursor:
            mycursor.execute(sql, (params["Plate"], ))
            mydb.commit()
            mydb.close()
            return True
    except:
        mydb.rollback()
        mydb.close()
        return False


def connect_database():
    global mydb
    
    mydb = mysql.connector.connect(
        host=os.getenv('DBHOST'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPASSWORD'),
        database=os.getenv('DBDATABASE')
    )
    return mydb
