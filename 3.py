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
GPIO.setup(GPIO_ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

# Database connection
db = mysql.connector.connect(
    host="localhost",
    user="admin",
    password="1234",
    database="DistanceMeasurements"
)

cursor = db.cursor()

def distance():
    # Set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)

    # Wait for Echo start
    while GPIO.input(GPIO_ECHO) == 0:
        pulse_start = time.time()

    # Wait for Echo end
    while GPIO.input(GPIO_ECHO) == 1:
        pulse_end = time.time()

    # Calculate pulse duration
    pulse_duration = pulse_end - pulse_start

    # Calculate distance in cm
    distance = pulse_duration * 17150
    
    if distance > 400:
        distance = 400
    elif distance < 2:
        distance = 2

    return distance

def buzzer_on():
    GPIO.output(BUZZER, True)

def buzzer_off():
    GPIO.output(BUZZER, False)

def insert_measurement(distance):
    measured_at = time.strftime('%Y-%m-%d %H:%M:%S')
    cursor.execute("INSERT INTO measurements (distance, measured_at) VALUES (%s, %s)", (distance, measured_at))
    db.commit()

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print(f"Measured Distance = {dist:.2f} cm")

            # Insert data into the database
            insert_measurement(dist)

            if dist > 12:
                buzzer_on()
            else:
                buzzer_off()

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
        cursor.close()
        db.close()
