import RPi.GPIO as GPIO
import time
import smtplib
from email.message import EmailMessage
import cv2  # OpenCV library

# Set up GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

PIR_PIN = 14  # GPIO pin for PIR Motion Sensor
BUZZER_PIN = 15  # GPIO pin for Buzzer

GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Camera setup
camera = cv2.VideoCapture(0)  # Use the first detected webcam (index 0)

# Email configuration
EMAIL_ADDRESS = "your_email@example.com"
EMAIL_PASSWORD = "your_password"
TO_EMAIL = "recipient_email@example.com"

def send_email(image_path):
    """Sends an email with the captured image attached."""
    msg = EmailMessage()
    msg['Subject'] = 'Motion Detected!'
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = TO_EMAIL
    msg.set_content('Motion detected! See attached image.')

    with open(image_path, 'rb') as f:
        file_data = f.read()
        msg.add_attachment(file_data, maintype='image', subtype='jpeg', filename='motion.jpg')

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        smtp.send_message(msg)
    print("Email sent successfully.")

def motion_camera(channel):
    """Callback function to run when motion is detected."""
    print("Motion Detected!")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)
    time.sleep(1)  # Buzzer ON for 1 second
    GPIO.output(BUZZER_PIN, GPIO.LOW)

    # Capture image
    ret, frame = camera.read()
    if ret:
        image_path = '/home/pi/motion.jpg'
        cv2.imwrite(image_path, frame)
        print("Image captured.")

        # Send email with captured image
        send_email(image_path)
    else:
        print("Failed to capture image.")

try:
    # Test GPIO Pin Setup
    GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    # Add event detection for PIR sensor
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_camera)
    print("Monitoring for motion...")

    while True:
        time.sleep(0.1)  # Continuously check for motion

except KeyboardInterrupt:
    print("Program stopped by user.")
finally:
    GPIO.cleanup()
    camera.release()  # Release the webcam
    print("GPIO and Camera cleaned up.")
