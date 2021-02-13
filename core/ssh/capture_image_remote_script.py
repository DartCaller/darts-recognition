from picamera import PiCamera
from time import sleep
import datetime

camera = PiCamera()
camera.resolution = (1640, 1232)  # (3280, 2464)
camera.framerate = 15
camera.rotation = 180
camera.start_preview(alpha=192)
sleep(1)
date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
file_location = '/home/pi/Desktop/dartboard_%s.jpg' % date
camera.capture(file_location)
camera.stop_preview()
print(file_location)
