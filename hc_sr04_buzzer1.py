import RPi.GPIO as GPIO
import time

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
    distance = (TimeElapsed * 34300) / 2

    return distance

def buzzer_on():
    GPIO.output(BUZZER, True)

def buzzer_off():
    GPIO.output(BUZZER, False)

if __name__ == '__main__':
    try:
        while True:
            dist = distance()
            print(f"Measured Distance = {dist:.2f} cm")

            if dist > 12:  # If distance is greater than 12 cm
                buzzer_on()
            else:
                buzzer_off()

            time.sleep(1)

    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
