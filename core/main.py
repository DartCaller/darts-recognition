from vector import Vector
from dart_board import DartBoard
from camera import Camera
from dartboard_images import DartboardImage, DartboardImages
from helper_functions import read_image
from datetime import datetime
import matplotlib.pyplot as plt
from config import config
import requests


max_waited = 2
waited_for_empty = 0
waited_for_change = 0
x_cam = Camera('x', Vector(0, 396), 1220)
y_cam = Camera('y', Vector(-390, 0), 1100)


empty_x = x_cam.crop_img(read_image('labeled_images/newEmpty/x_0.JPG'))
empty_y = y_cam.crop_img(read_image('labeled_images/newEmpty/y_0.JPG'))
calib_x = x_cam.crop_img(read_image('labeled_images/newCalib/x_0.JPG'))
calib_y = y_cam.crop_img(read_image('labeled_images/newCalib/y_0.JPG'))

dartboard = DartBoard(x_cam.pos, y_cam.pos)


def display_image_pair_on_axis(axis, title, imgs, methods, only_axis=None):
    def should_display_axis(ax): return only_axis is None or only_axis == ax
    for i, axis_label in enumerate(['x', 'y']):
        if should_display_axis(i):
            axis[i].set_title(f'{title} {axis_label.capitalize()}')
            axis[i].imshow(getattr(getattr(imgs, axis_label), methods)())


def display_debug_images(img_obj, properties_to_display, axis=None):
    axis_to_display = 2 if axis is None else 1
    fig, axes = plt.subplots(len(properties_to_display), axis_to_display)

    if len(properties_to_display) == 1:
        axes = [axes]
    if axis is not None:
        axes = [axes]
    for num, (title, method) in enumerate(properties_to_display):
        display_image_pair_on_axis(axes[num], title, img_obj, method, axis)
    fig.show()


def setup():
    print('# Calibrating Dartboard')
    dartboard.calibrate((empty_x, empty_y), (calib_x, calib_y), 340)
    x_cam.set_y_bounds_min(1220)
    y_cam.set_y_bounds_min(1100)


def reset_cam_imgs(cameras, img_objs):
    for camera, img_object in zip(cameras, img_objs.list()):
        camera.update_last_taken_img(img_object)
        camera.set_empty_dart_board_img(img_object.get_img())


def on_incoming_imgs(x_img, y_img):
    global waited_for_empty, waited_for_change
    cameras = [x_cam, y_cam]
    x_img = x_cam.crop_img(x_img)
    y_img = y_cam.crop_img(y_img)

    if any(map(lambda cam: cam.last_taken_img is None or cam.empty_board_img is None, cameras)):
        print('Set first camera reference images')
        return reset_cam_imgs(cameras, DartboardImages(x_img, y_img))

    img_objs = DartboardImages(
        x_img, y_img, x_cam.get_last_img(), y_cam.get_last_img(), x_cam.empty_board_img, y_cam.empty_board_img
    )

    display_debug_images(img_objs, [
        # ('Emtpy', 'get_empty_img'),
        ('Last', 'get_last_img'),
        ('New', 'get_img'),
        ('Empty Diff', 'get_diff_to_empty_img'),
        ('Last Diff', 'get_diff_to_last_img'),
    ], None)

    are_imgs_empty = img_objs.are_last_imgs_empty()
    last_imgs_were_empty = list(map(lambda cam: cam.last_taken_img.is_empty_board(), cameras))
    change_occurred_in_imgs = img_objs.do_last_imgs_contain_change()
    print('Last Diff ', list(map(lambda item: item.get_diff_count_to_last_img(), img_objs.list())))
    print('Empty Diff ', list(map(lambda item: item.get_diff_count_to_empty_img(), img_objs.list())))

    if all(are_imgs_empty) or (any(are_imgs_empty) and waited_for_empty == max_waited):
        waited_for_empty = 0
        if not any(last_imgs_were_empty):
            print('Board was emptied')
            # requests.post(config['backend_url'] + '/game/boardEmptied')
        reset_cam_imgs(cameras, img_objs)
        print('Updated last taken image')
    elif any(are_imgs_empty) and not any(last_imgs_were_empty):
        waited_for_empty += 1
        print('Only one axis emptied')
    elif all(change_occurred_in_imgs) or (any(change_occurred_in_imgs) and waited_for_change == max_waited):
        waited_for_change = 0
        result = dartboard.get_dart_score(img_objs.x, img_objs.y)
        print(f'Hit: {result}!')
        for camera, img in zip(cameras, img_objs.list()):
            camera.update_last_taken_img(img)
        # requests.post(config['backend_url'] + '/board/' + config['board_id'] + '/throw', result)
    elif any(change_occurred_in_imgs):
        waited_for_change += 1
        print('Waiting for second change in image')
    else:
        print('Nothing changed. Skipping Detection')
    print('---')
