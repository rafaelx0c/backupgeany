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
import mysql.connector  # MySQL Connector for database interaction
from Adafruit_DHT import DHT11, read_retry  # Import Adafruit library for DHT11

# GPIO setup
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)  # Use BCM numbering for GPIO pins
GPIO.setup(17, GPIO.IN)  # Motion sensor connected to GPIO pin 22
GPIO.setup(18, GPIO.OUT)  # Buzzer connected to GPIO pin 18

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

# Database connection parameters
db_config = {
    'host': 'localhost',
    'user': 'admin',
    'password': 'password',
    'database': 'PiCamera'
}

# DHT11 sensor settings
DHT_PIN = 4  # GPIO pin connected to the data pin of the DHT11

# Temperature and humidity thresholds
TEMP_THRESHOLD = 1  # Temperature threshold in Celsius
HUMIDITY_THRESHOLD = 3  # Humidity threshold in percentage

def connect_to_database():
    """Connect to the MySQL database."""
    try:
        connection = mysql.connector.connect(**db_config)
        print("Connected to the database successfully.")
        return connection
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return None

def insert_record(file_name, file_type, motion_status, temperature, humidity):
    """Inserts the record of the captured file into the database."""
    connection = connect_to_database()
    if connection:
        cursor = connection.cursor()
        query = """INSERT INTO recordings (file_name, file_type, timestamp, motion_status, temperature, humidity) 
                   VALUES (%s, %s, %s, %s, %s, %s)"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        values = (file_name, file_type, timestamp, motion_status, temperature, humidity)
        try:
            cursor.execute(query, values)
            connection.commit()
            print(f"Record inserted into database: {values}")
        except mysql.connector.Error as err:
            print(f"Error inserting record: {err}")
        finally:
            cursor.close()
            connection.close()

def send_email(file_name, file_data, file_type):
    """Sends an email with the attached file."""
    message = MIMEMultipart()
    message["From"] = USERNAME
    message["To"] = RECIEVER_EMAIL
    message["Subject"] = subject

    message.attach(MIMEText(bodyText, 'plain'))

    # Attach the file
    if file_data:
        try:
            mimeBase = MIMEBase('application', 'octet-stream')
            mimeBase.set_payload(file_data)
            encoders.encode_base64(mimeBase)
            mimeBase.add_header('Content-Disposition', f"attachment; filename={file_name}")
            message.attach(mimeBase)

            text = message.as_string()
            with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as session:
                session.ehlo()
                session.starttls()
                session.ehlo()
                session.login(USERNAME, PASSWORD)
                session.sendmail(USERNAME, RECIEVER_EMAIL, text)
            
            print("Email sent with attachment")

        except Exception as e:
            print(f"Error sending email: {e}")

def capture_image(motion_status):
    """Captures an image using the Raspberry Pi camera and sends it without saving locally."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    image_name = f'image_{timestamp}.jpg'
    temperature, humidity = read_retry(DHT11, DHT_PIN)  # Read temperature and humidity
    try:
        # Capture image using libcamera-still and save to stdout
        result = subprocess.run(['libcamera-still', '-o', '-'], capture_output=True)
        if result.returncode == 0:
            print("Image captured")
            send_email(image_name, result.stdout, 'image')  # Send email with captured image
            insert_record(image_name, 'image', motion_status, temperature, humidity)  # Insert record to database
        else:
            print(f"Error capturing image: {result.stderr.decode()}")
    except subprocess.CalledProcessError as e:
        print(f"Error capturing image: {e}")

def capture_video(motion_status):
    """Captures video using the Raspberry Pi camera, converts to MP4, sends it, and avoids saving long-term."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    raw_video_name = f"video_{timestamp}.h264"
    mp4_video_name = f"video_{timestamp}.mp4"
    temperature, humidity = read_retry(DHT11, DHT_PIN)  # Read temperature and humidity
    
    try:
        # Capture raw H264 video using libcamera-vid
        result = subprocess.run(['libcamera-vid', '-o', raw_video_name, '-t', '10000'], capture_output=True, text=False)
        
        if result.returncode == 0:
            print("Video captured")

            # Convert H264 to MP4 using ffmpeg
            conversion_result = subprocess.run(['ffmpeg', '-i', raw_video_name, '-c:v', 'libx264', '-preset', 'fast', '-movflags', '+faststart', mp4_video_name])

            if conversion_result.returncode == 0:
                print("Video converted to MP4 format")
                
                # Read the MP4 file data for sending via email
                with open(mp4_video_name, 'rb') as video_file:
                    video_data = video_file.read()
                
                # Send the MP4 video via email
                send_email(mp4_video_name, video_data, 'video')
                
                # Insert record into the database
                insert_record(mp4_video_name, 'video', motion_status, temperature, humidity)
                
            else:
                print(f"Error converting video: {conversion_result.stderr}")

            # Clean up: remove the raw and converted video files
            os.remove(raw_video_name)
            os.remove(mp4_video_name)

        else:
            print(f"Error capturing video: {result.stderr}")

    except subprocess.CalledProcessError as e:
        print(f"Error capturing or converting video: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

def check_temperature_and_humidity():
    """Reads temperature and humidity from the DHT11 sensor and checks if they meet the thresholds."""
    humidity, temperature = read_retry(DHT11, DHT_PIN)  # Use Adafruit library to read sensor
    if humidity is not None and temperature is not None:
        print(f"Temperature: {temperature:.1f}C, Humidity: {humidity:.1f}%")
        return temperature >= TEMP_THRESHOLD and humidity <= HUMIDITY_THRESHOLD
    else:
        print("Failed to read from DHT11 sensor.")
        return False

# Main code for method call
if __name__ == "__main__":
    try:
        choice = input("Enter '1' to record a video or '2' to capture an image: ")
        while True:
            motion_status = 1 if GPIO.input(17) == GPIO.HIGH else 0  # Set motion status
            if motion_status == 1:  # Motion detected
                print("Motion Detected!")
                if check_temperature_and_humidity():  # Check if temperature and humidity meet the thresholds
                    GPIO.output(18, GPIO.HIGH)  # Activate buzzer
                    if choice == '1':
                        capture_video(motion_status)
                    elif choice == '2':
                        capture_image(motion_status)
                    else:
                        print("Invalid choice. Please enter '1' or '2'.")
                    sleep(2)
                    GPIO.output(18, GPIO.LOW)  # Deactivate buzzer
                else:
                    print("Temperature or humidity threshold not met.")
            sleep(0.1)  # Short delay to avoid high CPU usage

    except KeyboardInterrupt:
        print("Exiting...")
    finally:
        GPIO.cleanup()
