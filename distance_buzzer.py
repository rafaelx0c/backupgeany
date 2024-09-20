import RPi.GPIO as GPIO
import time
import json
from flask import Flask, jsonify

app = Flask(__name__)

# GPIO setup
GPIO.setmode(GPIO.BCM)
TRIG = 23
ECHO = 24
BUZZER = 22
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)

def get_distance():
    GPIO.output(TRIG, False)
    time.sleep(2)
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)
    pulse_start = time.time()
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    pulse_end = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)
    return distance

@app.route('/update')
def update():
    distance = get_distance()
    if distance >= 12:
        GPIO.output(BUZZER, True)
    else:
        GPIO.output(BUZZER, False)
    return jsonify({'distance': distance})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
