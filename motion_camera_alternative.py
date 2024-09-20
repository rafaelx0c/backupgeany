import RPi.GPIO as GPIO
import time
import cv2  # OpenCV for capturing images from the webcam
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# GPIO Setup
PIR_PIN = 18
BUZZER_PIN = 27
GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Email Configuration
from_email = "your_email@gmail.com"
to_email = "recipient_email@gmail.com"
smtp_server = "smtp.gmail.com"
smtp_port = 587
smtp_user = "your_email@gmail.com"
smtp_password = "your_password"

def send_email(image_path):
    """Sends an email with the captured image attached."""
    subject = "Motion Detected!"
    body = "Motion detected! See the attached image."

    # Compose Email
    msg = MIMEMultipart()
    msg['From'] = from_email
    msg['To'] = to_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    # Attach Image
    with open(image_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename= {image_path}",
        )
        msg.attach(part)

    # Send Email
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(smtp_user, smtp_password)
        server.send_message(msg)

def motion_detected(channel):
    """Handles motion detection events."""
    print("Motion Detected!")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn buzzer on

    # Capture Image
    ret, frame = camera.read()
    if ret:
        image_path = "/home/pi/motion_detected.jpg"
        cv2.imwrite(image_path, frame)
        print("Image captured.")
        send_email(image_path)

    time.sleep(1)
    GPIO.output(BUZZER_PIN, GPIO.LOW)   # Turn buzzer off

# Main Loop
try:
    # Initialize the camera
    camera = cv2.VideoCapture(0, cv2.CAP_V4L2)  # For V4L2 backend
    if not camera.isOpened():
        print("Error: Could not open webcam.")
        exit()

    # Ensure GPIO edge detection setup is clean
    GPIO.remove_event_detect(PIR_PIN)
    GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detected)

    print("Monitoring for motion...")

    while True:
        # Keep the camera open and wait for motion detection
        time.sleep(1)  

except KeyboardInterrupt:
    print("Stopped by User")

finally:
    GPIO.cleanup()
    camera.release()
