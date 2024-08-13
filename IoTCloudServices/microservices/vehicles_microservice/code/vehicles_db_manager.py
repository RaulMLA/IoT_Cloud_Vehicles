import mysql.connector
import os


def register_new_vehicle(params):
    connect_database()

    sql_1 = "SELECT plate FROM vehicles WHERE vehicle_id = %s ORDER BY plate ASC LIMIT 1;"
    sql_2 = "SELECT plate, is_assigned FROM available_plates WHERE is_assigned = 0 ORDER BY plate ASC LIMIT 1;"
    sql_3 = "INSERT INTO vehicles (vehicle_id, plate) VALUES (%s, %s);"
    sql_4 = "UPDATE available_plates SET is_assigned = 1 WHERE plate = %s;"
    plate = ""

    try:
        with mydb.cursor() as mycursor:
            mycursor.execute(sql_1, (params['vehicle_id'],))
            myresult = mycursor.fetchone()
            if myresult:
                plate = myresult[0]
            else:
                mycursor.execute(sql_2)
                myresult = mycursor.fetchone()
                if myresult:
                    plate = myresult[0]
                    mycursor.execute(sql_3, (params['vehicle_id'], plate))
                    mycursor.execute(sql_4, (plate,))
                    mydb.commit()
    except:
        mydb.rollback()
        plate = ""

    mydb.close()
    return plate


def get_active_vehicles():
    connect_database()
    
    sql = "SELECT plate FROM vehicles WHERE status = 1;"
    plates = []

    with mydb.cursor() as mycursor:
        mycursor.execute(sql)
        myresult = mycursor.fetchall()
        for plate in myresult:
            data = {"Plate": plate}
            plates.append(data)
            
    mydb.close()
    return plates


def connect_database():
    global mydb
    
    mydb = mysql.connector.connect(
        host=os.getenv('DBHOST'),
        user=os.getenv('DBUSER'),
        password=os.getenv('DBPASSWORD'),
        database=os.getenv('DBDATABASE')
    )

    return mydb
