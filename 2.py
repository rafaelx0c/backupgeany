import RPi.GPIO as GPIO
import time
import mysql.connector
from mysql.connector import Error
from datetime import datetime

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins for sensors and buzzer
GPIO_TRIGGER_1 = 23
GPIO_ECHO_1 = 24
GPIO_TRIGGER_2 = 14
GPIO_ECHO_2 = 15
BUZZER = 18

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER_1, GPIO.OUT)
GPIO.setup(GPIO_ECHO_1, GPIO.IN)
GPIO.setup(GPIO_TRIGGER_2, GPIO.OUT)
GPIO.setup(GPIO_ECHO_2, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# Connect to MySQL database
def connect_to_database():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='1234',
            database='sensor_data'
        )
        if connection.is_connected():
            print("Connected to MySQL database")
        return connection
    except Error as e:
        print(f"Error: {e}")
        return None

# Insert data into the MySQL database
def insert_distance_data(connection, dist1, dist2):
    try:
        cursor = connection.cursor()
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        print(f"Inserting data: Sensor1: {dist1}, Sensor2: {dist2}")
        sql_query = """INSERT INTO distance_readings (sensor1_distance, sensor2_distance, recorded_at)
                       VALUES (%s, %s, %s)"""
        cursor.execute(sql_query, (dist1, dist2, current_time))
        connection.commit()
        print("Data inserted successfully")
    except Error as e:
        print(f"Failed to insert data into MySQL table: {e}")

# Function to measure pulse duration
def measure_pulse(GPIO_ECHO, level):
    start_time = time.time()
    while GPIO.input(GPIO_ECHO) != level:
        if time.time() - start_time > 0.1:  # Timeout after 100ms
            return None
    return time.time()

# Function to measure distance
def distance(GPIO_TRIGGER, GPIO_ECHO):
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)  # Trigger pulse of 10 microseconds
    GPIO.output(GPIO_TRIGGER, False)

    start_time = measure_pulse(GPIO_ECHO, True)
    if start_time is None:
        return None
    
    stop_time = measure_pulse(GPIO_ECHO, False)
    if stop_time is None:
        return None

    pulse_duration = stop_time - start_time
    dist = pulse_duration * 17150  # Use the formula for distance calculation

    # Apply valid distance limits (2 cm to 400 cm)
    if dist > 400:
        dist = 400
    elif dist < 2:
        dist = 2

    # Round distance to one decimal place
    dist = round(dist, 1)
    
    return dist

def buzzer_on():
    GPIO.output(BUZZER, True)

def buzzer_off():
    GPIO.output(BUZZER, False)

if __name__ == '__main__':
    try:
        db_connection = connect_to_database()
        if db_connection is None:
            raise Exception("Failed to connect to the database.")

        while True:
            dist1 = distance(GPIO_TRIGGER_1, GPIO_ECHO_1)
            if dist1 is not None:
                print(f"Sensor 1 Measured Distance = {dist1:.2f} cm")
            else:
                print("Sensor 1 measurement error")

            dist2 = distance(GPIO_TRIGGER_2, GPIO_ECHO_2)
            if dist2 is not None:
                print(f"Sensor 2 Measured Distance = {dist2:.2f} cm")
            else:
                print("Sensor 2 measurement error")

            if dist1 is not None and dist2 is not None:
                insert_distance_data(db_connection, dist1, dist2)

            if dist1 is not None and (dist1 > 12 or dist2 > 12):
                buzzer_on()
            else:
                buzzer_off()

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()

    finally:
        if db_connection.is_connected():
            db_connection.close()
            print("MySQL connection is closed")
