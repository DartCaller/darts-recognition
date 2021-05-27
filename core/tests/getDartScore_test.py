import pytest
from vector import Vector
from dart_board import DartBoard
from camera import Camera
from helper_functions import read_image
from time import time
from pathlib import Path
import re

x_camera = Camera('x', Vector(0, 354), 600)  # 354
y_camera = Camera('y', Vector(-354, 0), 630)


def read_and_crop_image_pair(image_path, number='0'):
    def get_axis_image(axis):
        return read_image(f'{image_path}/{axis}_{number}.JPG')

    return x_camera.crop_img(get_axis_image('x')), \
        y_camera.crop_img(get_axis_image('y'))


empty_imgs = read_and_crop_image_pair('../labeled_images/empty')
calib_imgs = read_and_crop_image_pair('../labeled_images/calib')
s3_imgs = read_and_crop_image_pair('../labeled_images/S3')

start_time = time()
dart_board = DartBoard(x_camera.pos, y_camera.pos)
dart_board.calibrate((empty_imgs[0], empty_imgs[1]), (calib_imgs[0], calib_imgs[1]), 340)
end_time = time()
print(f'setup tests took {end_time - start_time} seconds')


def get_all_labeled_image_pairs():
    print('loading all images')
    labeled_images = Path('../labeled_images').glob('*/*.jpg')
    image_pair_dict = {}
    for image in labeled_images:
        direct_parent_folder = image.parts[-2]
        if re.compile("[SDT]([1]?[1-9]|10|20|25)").fullmatch(direct_parent_folder):
            axis, nmb = image.stem.split('_')
            key = '_'.join((direct_parent_folder, nmb))
            if key not in image_pair_dict:
                image_pair_dict[key] = {'x': None, 'y': None, 'path': None}
                print(image)
            image_pair_dict[key][axis] = read_image(str(image))
            image_pair_dict[key]['path'] = str(image.parent)

    result = []
    for key, value in image_pair_dict.items():
        if value['x'] is not None and value['y'] is not None:
            result.append((
                key.split('_')[0],
                x_camera.crop_img(value['x']),
                y_camera.crop_img(value['y']),
                value['path']
            ))
    print('finished loading images')
    return result


all_labeled_images = get_all_labeled_image_pairs()


class TestDartboardGetDartScore:
    @pytest.mark.parametrize(
        'expected, x_image, y_image, path',
        all_labeled_images
        # [('S3', s3_imgs[0], s3_imgs[1])]
    )
    def test_correct_dart_score(self, expected, x_image, y_image, path):
        result = dart_board.get_dart_score([empty_imgs[0], x_image], [empty_imgs[1], y_image])
        assert expected == result
