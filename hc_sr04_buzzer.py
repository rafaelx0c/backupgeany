import RPi.GPIO as GPIO
import time
import mysql.connector

# GPIO Mode (BOARD / BCM)
GPIO.setmode(GPIO.BCM)

# Set GPIO Pins
GPIO_TRIGGER = 23
GPIO_ECHO = 24
BUZZER = 18

# Set GPIO direction (IN / OUT)
GPIO.setup(GPIO_TRIGGER, GPIO.OUT)
GPIO.setup(GPIO_ECHO, GPIO.IN)  # Corrected line
GPIO.setup(BUZZER, GPIO.OUT)

# Database connection
db = mysql.connector.connect(
    host="localhost",      # Use "raspi" or "localhost" depending on the hostname
    user="admin",          # Replace with your phpMyAdmin username
    password="1234",       # Replace with your phpMyAdmin password
    database="DistanceMeasurements"  # The name of your database
)

cursor = db.cursor()

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)

    # Set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()

    # Save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()

    # Time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # Multiply with the sonic speed (34300 cm/s) and divide by 2 (round trip)
    distance = (TimeElapsed * 34300) / 2  # Fixed the speed to 34300 cm/s

    return distance

def buzzer_on():
    GPIO.output(BUZZER, True)

def buzzer_off():
    GPIO.output(BUZZER, False)

def insert_measurement(distance):
    # Insert distance measurement into the database
    measured_at = time.strftime('%Y-%m-%d %H:%M:%S')  # Get current time
    cursor.execute("INSERT INTO measurements (distance, measured_at) VALUES (%s, %s)", (distance, measured_at))
    db.commit()

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print(f"Measured Distance = {dist:.2f} cm")

            # Insert data into the database
            insert_measurement(dist)

            if dist > 12:  # If distance is greater than 12 cm
                buzzer_on()
            else:
                buzzer_off()

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        cursor.close()
        db.close()
