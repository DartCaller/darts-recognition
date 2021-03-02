from vector import Vector
from dart_board import DartBoard
from camera import Camera
from helper_functions import read_image, time_function_execution
from os.path import basename
import time

empty_x = read_image('../exampleImages/emptyBoard/x.JPG')
empty_y = read_image('../exampleImages/emptyBoard/y.JPG')
calib_x = read_image('../exampleImages/wideCalib/x.JPG')
calib_y = read_image('../exampleImages/wideCalib/y.JPG')

y_bounds = (700, 1460)
x_camera_pos = Vector(0, 396)
y_camera_pos = Vector(-390, 0)
dartboard = DartBoard(y_bounds, x_camera_pos, y_camera_pos, debug=True)
x_camera = Camera('x')
y_camera = Camera('y', 'raspberrypi.local')


def setup():
    print('# Calibrating Dartboard')
    time_function_execution('Calibration', lambda: dartboard.calibrate((empty_x, empty_y), (calib_x, calib_y), 340))


def main():
    print('# Starting Up')

    while True:
        x_image = time_function_execution('Local Image Taking', lambda: x_camera.take_photo())
        y_image = time_function_execution('Remote Image Taking', lambda: y_camera.take_photo())
        result = time_function_execution(
            'Calculating Dart',
            lambda: dartboard.get_dart_score(read_image(x_image), read_image(y_image))
        )
        print(f'Hit: {result}! From images: X:{basename(x_image)} and Y:{basename(y_image)}')
        time.sleep(5)


if __name__ == "__main__":
    print('## Dart Recognition ##')
    setup()
    main()
