from vector import Vector
from dart_board import DartBoard
from camera import Camera
from helper_functions import read_image
from config import config
import requests
import matplotlib.pyplot as plt


empty_x = read_image('exampleImages/emptyBoard/x.JPG')
empty_y = read_image('exampleImages/emptyBoard/y.JPG')
calib_x = read_image('exampleImages/wideCalib/x.JPG')
calib_y = read_image('exampleImages/wideCalib/y.JPG')


x_camera = Camera('x', Vector(0, 396))
y_camera = Camera('y', Vector(-390, 0))
dartboard = DartBoard(x_camera.pos, y_camera.pos, debug=True)


def setup():
    print('# Calibrating Dartboard')
    for camera, image in zip([x_camera, y_camera], [empty_x, empty_y]):
        camera.set_empty_dart_board_image(image)
        camera.update_last_taken_image(image)
    dartboard.calibrate((empty_x, empty_y), (calib_x, calib_y), 340)


def detect_change(camera, image):
    return camera.does_image_contain_change(image)


def on_incoming_images(x_image, y_image):
    cameras = [x_camera, y_camera]
    images = [x_image, y_image]
    change_occurred_in_images = map(detect_change, cameras, images)
    are_images_empty = map(lambda cam, img: cam.is_image_empty_board(img), cameras, images)

    if any(are_images_empty):
        last_images_were_empty = map(lambda cam: cam.is_image_empty_board(cam.last_taken_image), cameras)
        if not any(last_images_were_empty):
            # Notify Server Board was emptied
            print('Board was emptied')
            # requests.post(config['backend_url'] + '/game/boardEmptied')
        for camera, image in zip(cameras, images):
            camera.update_last_taken_image(image)
        print('Updated last taken image')
    elif all(change_occurred_in_images):
        fig, axes = plt.subplots(2, 2)
        axes[0][0].imshow(x_camera.last_taken_image)
        axes[0][1].imshow(x_image)
        axes[1][0].imshow(y_camera.last_taken_image)
        axes[1][1].imshow(y_image)
        fig.show()

        result = dartboard.get_dart_score((x_camera.last_taken_image, x_image), (y_camera.last_taken_image, y_image))
        print(f'Hit: {result}!')
        for camera, image in zip(cameras, images):
            camera.update_last_taken_image(image)
        # requests.post(config['backend_url'] + '/game/score', result)
    else:
        print('Nothing changed. Skipping Detection')
