import RPi.GPIO as GPIO
import time
import smtplib
import subprocess
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders

# Configure GPIO pins for sensor and buzzer
SENSOR_PIN = 17
BUZZER_PIN = 18

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)  # Disable GPIO warnings
GPIO.setup(SENSOR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

# Email configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
EMAIL_ADDRESS = 'raspiberry019@gmail.com'
EMAIL_PASSWORD = 'ljud ljwu kcof aele'  # Use the generated App Password
RECIPIENT_EMAIL = 'raspiberry019@gmail.com'

def send_email(image_path=None):
    subject = 'Motion Detected!'
    body = 'Motion detected at your location.'
    
    # Create message container
    msg = MIMEMultipart()
    msg['From'] = EMAIL_ADDRESS
    msg['To'] = RECIPIENT_EMAIL
    msg['Subject'] = subject

    # Attach the body with the msg instance
    msg.attach(MIMEText(body, 'plain'))

    # Attach the image file
    if image_path and Path(image_path).exists():
        try:
            part = MIMEBase('application', 'octet-stream')
            with open(image_path, 'rb') as file:
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', f'attachment; filename={Path(image_path).name}')
            msg.attach(part)
        except Exception as e:
            print(f"Error attaching image: {e}")

    # Send the email
    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  # Use App Password if necessary
        server.sendmail(EMAIL_ADDRESS, RECIPIENT_EMAIL, msg.as_string())
        server.quit()
        print("Email sent successfully")
    except smtplib.SMTPAuthenticationError as e:
        print(f"SMTP Authentication Error: {e}")
    except Exception as e:
        print(f"Error sending email: {e}")


def capture_image():
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    image_path = Path(f'/home/admin/image_{timestamp}.jpg')
    
    try:
        result = subprocess.run(['libcamera-still', '-o', str(image_path)], check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Image captured and saved to {image_path}")
            return image_path
        else:
            print(f"Error capturing image: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")
        return None

# Main loop
try:
    while True:
        if GPIO.input(SENSOR_PIN):
            print("Motion Detected!")
            GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Activate the buzzer
            image_path = capture_image()
            if image_path:
                send_email(image_path=str(image_path))
            time.sleep(5)  # Delay to avoid multiple detections
        else:
            GPIO.output(BUZZER_PIN, GPIO.LOW)  # Deactivate the buzzer
            time.sleep(0.5)

except KeyboardInterrupt:
    print("Exiting...")
    GPIO.cleanup()
