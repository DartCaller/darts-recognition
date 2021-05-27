from vector import Vector
from dart_board import DartBoard
from camera import Camera
from dartboard_images import DartboardImages
from helper_functions import read_image
from config import config
from auth_request import auth_request


max_waited = 2
waited_for_empty = 0
waited_for_change = 0
x_cam = Camera('x', Vector(0, 396), 610)
y_cam = Camera('y', Vector(-390, 0), 550)


empty_x = x_cam.crop_img(read_image('labeled_images/lowResEmpty/x_0.JPG'))
empty_y = y_cam.crop_img(read_image('labeled_images/lowResEmpty/y_0.JPG'))
calib_x = x_cam.crop_img(read_image('labeled_images/lowResCalib/x_0.JPG'))
calib_y = y_cam.crop_img(read_image('labeled_images/lowResCalib/y_0.JPG'))

dartboard = DartBoard(x_cam.pos, y_cam.pos)


def setup():
    print('# Calibrating Dartboard')
    dartboard.calibrate((empty_x, empty_y), (calib_x, calib_y), 340)
    x_cam.set_y_bounds_min(610)
    y_cam.set_y_bounds_min(550)


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

    are_imgs_empty = img_objs.are_last_imgs_empty()
    last_imgs_were_empty = list(map(lambda cam: cam.last_taken_img.is_empty_board(), cameras))
    change_occurred_in_imgs = img_objs.do_last_imgs_contain_change()

    if all(are_imgs_empty) or (any(are_imgs_empty) and waited_for_empty == max_waited):
        waited_for_empty = 0
        if not any(last_imgs_were_empty):
            print('Board was emptied')
            # auth_request(config['backend_url'] + '/game/boardEmptied')
        reset_cam_imgs(cameras, img_objs)
        print('Updated last taken image')
    elif any(are_imgs_empty) and not any(last_imgs_were_empty):
        waited_for_empty += 1
        print('Only one axis emptied')
    elif all(change_occurred_in_imgs) or (any(change_occurred_in_imgs) and waited_for_change == max_waited):
        waited_for_change = 0
        for camera, img in zip(cameras, img_objs.list()):
            camera.update_last_taken_img(img)
        result = dartboard.get_dart_score(img_objs.x, img_objs.y)
        print(f'Hit: {result}!')
        auth_request(config['backend_url'] + '/board/' + config['board_id'] + '/throw', result)
    elif any(change_occurred_in_imgs):
        waited_for_change += 1
        print('Waiting for second change in image')
    else:
        print('Nothing changed. Skipping Detection')
    print('---')
