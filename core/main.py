from vector import Vector
from dart_board import DartBoard
from camera import Camera
from dartboard_images import DartboardImage
from helper_functions import read_image
from config import config
import requests


max_waited = 2
waited_for_empty = 0
waited_for_change = 0
x_camera = Camera('x', Vector(0, 396), 600)
y_camera = Camera('y', Vector(-390, 0), 630)


empty_x = x_camera.crop_image(read_image('labeled_images/empty/x_0.JPG'))
empty_y = y_camera.crop_image(read_image('labeled_images/empty/y_0.JPG'))
calib_x = x_camera.crop_image(read_image('labeled_images/calib/x_0.JPG'))
calib_y = y_camera.crop_image(read_image('labeled_images/calib/y_0.JPG'))

dartboard = DartBoard(x_camera.pos, y_camera.pos)


def setup():
    print('# Calibrating Dartboard')
    dartboard.calibrate((empty_x, empty_y), (calib_x, calib_y), 340)
    x_camera.set_y_bounds_min(580)
    y_camera.set_y_bounds_min(580)


def on_incoming_images(x_image, y_image):
    global waited_for_empty, waited_for_change
    cameras = [x_camera, y_camera]
    x_image = x_camera.crop_image(x_image)
    y_image = y_camera.crop_image(y_image)

    if any(map(lambda cam: cam.last_taken_image is None or cam.empty_board_image is None, cameras)):
        for axis, camera, image in zip(['x', 'y'], cameras, [x_image, y_image]):
            camera.set_empty_dart_board_image(image)
            camera.update_last_taken_image(DartboardImage(axis, image, image))
        print('Set first camera reference images')
        return

    images = [
        DartboardImage('x', x_image, x_camera.last_taken_image.get_image(), x_camera.empty_board_image),
        DartboardImage('y', y_image, y_camera.last_taken_image.get_image(), y_camera.empty_board_image),
    ]
    are_images_empty = list(map(lambda img: img.is_empty_board(), images))
    last_images_were_empty = list(map(lambda cam: cam.last_taken_image.is_empty_board(), cameras))
    change_occurred_in_images = list(map(lambda img: img.contains_change(), images))

    if all(are_images_empty) or (any(are_images_empty) and waited_for_empty == max_waited):
        waited_for_empty = 0
        if not any(last_images_were_empty):
            # Notify Server Board was emptied
            print('Board was emptied')
            # requests.post(config['backend_url'] + '/game/boardEmptied')
        for camera, image in zip(cameras, images):
            camera.update_last_taken_image(image)
            camera.set_empty_dart_board_image(image.get_image())
        print('Updated last taken image')
    elif any(are_images_empty) and not any(last_images_were_empty):
        waited_for_empty += 1
        print('Only one axis emptied')
    elif all(change_occurred_in_images) or (any(change_occurred_in_images) and waited_for_change == max_waited):
        waited_for_change = 0
        result = dartboard.get_dart_score(x_image, y_image)
        print(f'Hit: {result}!')
        for camera, image in zip(cameras, images):
            camera.update_last_taken_image(image)
        requests.post(config['backend_url'] + '/board/' + config['board_id'] + '/throw', result)
    elif any(change_occurred_in_images):
        waited_for_change += 1
        print('Waiting for second change in image')
    else:
        print('Nothing changed. Skipping Detection')
    print('---')
