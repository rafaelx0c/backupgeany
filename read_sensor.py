import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# Set up GPIO pins
TRIG = 23
ECHO = 24

GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)

def get_distance():
    # Ensure the trigger is low
    GPIO.output(TRIG, False)
    time.sleep(2)

    # Send a 10us pulse to trigger
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Measure the duration of the echo pulse
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

if __name__ == "__main__":
    try:
        while True:
            distance = get_distance()
            print(f"Distance: {distance} cm")
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
