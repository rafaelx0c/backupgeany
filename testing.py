import RPi.GPIO as GPIO
import time
import smtplib
import cv2
import numpy as np

# Configure GPIO pins for sensor and buzzer
SENSOR_PIN = 17
BUZZER_PIN = 18

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'raspiberry019@gmail.com'
EMAIL_PASSWORD = 'Raspi1234'
RECIPIENT_EMAIL = 'raspiberry019@gmail.com'

def send_email():
    subject = 'Motion Detected!'
    body = 'Motion detected at your location.'
    
    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
    server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, f'Subject: {subject}\n\n{body}')
    server.quit()

# Function to capture image from webcam
def capture_image():
    cap = cv2.VideoCapture(0)  # Open the webcam
    ret, frame = cap.read()
    if ret:
        cv2.imwrite('/home/pi/image.jpg', frame)  # Save the image
    cap.release()

# Main loop
try:
    while True:
        if GPIO.input(SENSOR_PIN):
            print("Motion Detected!")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Activate the buzzer
            send_email()
            capture_image()
            time.sleep(5)  # Delay to avoid multiple detections
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Deactivate the buzzer
            time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
