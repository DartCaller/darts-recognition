from picamera import PiCamera
from time import sleep
import datetime

camera = PiCamera()
camera.resolution = (1640, 1232)  # (3280, 2464)
camera.framerate = 15
camera.rotation = 180


def take_image(target_dir):
    camera.start_preview(alpha=192)
    sleep(1)
    date = datetime.datetime.now().strftime("%Y-%m-%d_%H:%M:%S")
    file_location = '%s/dartboard_%s.jpg' % (target_dir, date)
    camera.capture(file_location)
    camera.stop_preview()
    return file_location


if __name__ == '__main__':
    file_path = take_image('/home/pi/Desktop')
    print(file_path)
