from gpiozero import MotionSensor
from picamera import PiCamera 
from time import sleep

pir = MotionSensor(17)
camera = PiCamera()

while True:
	pir.wait_for_motion()
	print("Motion detected!")
	camera.start_recording('/home/admin/video.h264')
	sleep(10) #Record for 10 seconds
	camera.stop_recording()
	pir.wait_for_no_motion()
