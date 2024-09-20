import smtplib
import os
import subprocess
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email import encoders
from time import sleep
from datetime import datetime
import RPi.GPIO as GPIO

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering for GPIO pins
GPIO.setup(17, GPIO.IN)  # Motion sensor connected to GPIO pin 17
GPIO.setup(18, GPIO.OUT) # Buzzer connected to GPIO pin 18

# Email parameters
subject = 'Security Alert: Motion Detected!'
bodyText = """\
Hi,
A motion has been detected in your room.
Please check the attachment sent from the Raspberry Pi security system.
Regards,
AS Tech-Workshop
"""
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587   
USERNAME = 'raspiberry019@gmail.com'
PASSWORD = 'ljud ljwu kcof aele'  # Use the generated App Password
RECIEVER_EMAIL = 'raspiberry019@gmail.com'

# File paths
filepath = "/home/admin/python_code/capture/"

def send_email(file_path=None):
    """Sends an email with the attached file."""
    message = MIMEMultipart()
    message["From"] = USERNAME
    message["To"] = RECIEVER_EMAIL
    message["Subject"] = subject

    message.attach(MIMEText(bodyText, 'plain'))

    # Attach the file
    if file_path and os.path.exists(file_path):
        try:
            with open(file_path, "rb") as attachment:
                mimeBase = MIMEBase('application', 'octet-stream')
                mimeBase.set_payload(attachment.read())
                encoders.encode_base64(mimeBase)
                mimeBase.add_header('Content-Disposition', f"attachment; filename={os.path.basename(file_path)}")
                message.attach(mimeBase)

            text = message.as_string()
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as session:
                session.ehlo()
                session.starttls()
                session.ehlo()
                session.login(USERNAME, PASSWORD)
                session.sendmail(USERNAME, RECIEVER_EMAIL, text)
            
            print("Email sent")

        except Exception as e:
            print(f"Error sending email: {e}")

def capture_image():
    """Captures an image using the Raspberry Pi camera."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_path = f'/home/admin/python_code/capture/image_{timestamp}.jpg'
    try:
        result = subprocess.run(['libcamera-still', '-o', image_path], check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Image captured and saved to {image_path}")
            return image_path
        else:
            print(f"Error capturing image: {result.stderr}")
            return None
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")
        return None

def capture_video():
    """Captures video using the Raspberry Pi camera and converts it to MP4."""
    video_path = '/home/admin/python_code/capture/newvideo.h264'
    final_path = filepath + filename
    try:
        # Ensure the directory exists
        if not os.path.exists(filepath):
            os.makedirs(filepath)

        # Start capturing video
        result = subprocess.run(['libcamera-vid', '-o', video_path, '-t', '10000'], check=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"Video captured and saved to {video_path}")
            # Convert video to mp4 format using ffmpeg
            conversion_result = subprocess.run(['ffmpeg', '-i', video_path, final_path], check=True, capture_output=True, text=True)
            if conversion_result.returncode == 0:
                print(f"Video converted and saved to {final_path}")
            else:
                print(f"Error converting video: {conversion_result.stderr}")
        else:
            print(f"Error capturing video: {result.stderr}")
    except subprocess.CalledProcessError as e:
        print(f"Error capturing or converting video: {e}")

def remove_file(file_path):
    """Removes the specified file."""
    try:
        os.remove(file_path)
        print(f"Removed file {file_path}")
    except FileNotFoundError:
        print(f"File {file_path} does not exist")

# Main code for method call
if __name__ == "__main__":
    try:
        choice = input("Enter '1' to record a video or '2' to capture an image: ")
        if choice == '1':
            filename_part1 = "surveillance"
            file_ext = ".mp4"
            now = datetime.now()
            current_datetime = now.strftime("%d-%m-%Y_%H:%M:%S")
            filename = filename_part1 + "_" + current_datetime + file_ext
            final_path = filepath + filename
            
            while True:
                if GPIO.input(17) == GPIO.HIGH:  # Motion detected
                    print("Motion Detected!")
                    GPIO.output(18, GPIO.HIGH)  # Activate buzzer
                    capture_video()
                    sleep(2)
                    send_email(file_path=final_path)
                    sleep(2)
                    remove_file(video_path)
                    remove_file(final_path)
                    GPIO.output(18, GPIO.LOW)  # Deactivate buzzer
                sleep(0.1)  # Short delay to avoid high CPU usage

        elif choice == '2':
            while True:
                if GPIO.input(17) == GPIO.HIGH:  # Motion detected
                    print("Motion Detected!")
                    GPIO.output(18, GPIO.HIGH)  # Activate buzzer
                    image_path = capture_image()
                    if image_path:
                        send_email(file_path=image_path)
                    sleep(2)
                    remove_file(image_path)
                    GPIO.output(18, GPIO.LOW)  # Deactivate buzzer
                sleep(0.1)  # Short delay to avoid high CPU usage

        else:
            print("Invalid choice. Please enter '1' or '2'.")

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
