from helper_functions.binary_diff_images import binary_diff_images
from config import config
import numpy as np


def get_image_diff(base_image, image):
    binary_diff_image = binary_diff_images(
        base_image,
        image,
        config['y_bounds'],
        config['pixel_diff_threshold']
    )
    return np.count_nonzero(np.asarray(binary_diff_image) == 255)


class Camera:
    def __init__(self, axis, pos):
        self.last_taken_image = None
        self.empty_board_image = None
        self.pos = pos
        self.axis = axis

    def update_last_taken_image(self, new_last_image):
        self.last_taken_image = new_last_image

    def set_empty_dart_board_image(self, empty_board_image):
        self.empty_board_image = empty_board_image

    def does_image_contain_change(self, image):
        if self.last_taken_image is None:
            return False

        number_of_changed_pixels = get_image_diff(self.last_taken_image, image)
        return number_of_changed_pixels >= config['image_diff_threshold']

    def is_image_empty_board(self, image):
        if [x for x in (image, self.empty_board_image) if x is None]:
            return False

        number_of_changed_pixels = get_image_diff(self.empty_board_image, image)

        return number_of_changed_pixels <= config['image_diff_threshold']
