import cv2
import time
import RPi.GPIO as GPIO

# GPIO setup
PIR_PIN = 17  # GPIO pin where the PIR sensor output is connected
BUZZER_PIN = 27  # GPIO pin where the buzzer is connected

GPIO.setmode(GPIO.BCM)
GPIO.setup(PIR_PIN, GPIO.IN)
GPIO.setup(BUZZER_PIN, GPIO.OUT)

def start_recording():
    # Initialize webcam
    cap = cv2.VideoCapture(0)

    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('motion_record.avi', fourcc, 20.0, (640, 480))

    print("Recording started...")
    start_time = time.time()
    
    while True:
        ret, frame = cap.read()
        if ret:
            out.write(frame)
            cv2.imshow('Recording', frame)
            # Stop recording after 10 seconds
            if time.time() - start_time > 10:
                break
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        else:
            break

    # Release everything if job is finished
    cap.release()
    out.release()
    cv2.destroyAllWindows()
    print("Recording stopped.")

def motion_detected(channel):
    print("Motion Detected!")
    GPIO.output(BUZZER_PIN, GPIO.HIGH)  # Turn on buzzer
    time.sleep(1)  # Buzzer sound duration
    GPIO.output(BUZZER_PIN, GPIO.LOW)  # Turn off buzzer

    start_recording()  # Start recording video

# Configure event detection on PIR_PIN
GPIO.add_event_detect(PIR_PIN, GPIO.RISING, callback=motion_detected)

try:
    print("System is ready...")
    while True:
        time.sleep(1)  # Infinite loop to keep the script running

except KeyboardInterrupt:
    print("Program stopped by User")
    GPIO.cleanup()
