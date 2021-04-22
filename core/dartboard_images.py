import numpy as np
from config import config
from scipy.ndimage import find_objects, binary_opening
from scipy.ndimage.measurements import label
from helper_functions.binary_diff_images import binary_diff_images


def filter_small_obj_at_the_ground(obj, obj_pos):
    lower_bound = config['y_bounds_height'] - 100
    return np.count_nonzero(obj) < 10000 and obj_pos[1].start < 100 and obj_pos[1].stop < 100


class DartboardImage:
    def __init__(self, axis, image, last_image, empty_board=None):
        if empty_board is None:
            empty_board = last_image
        self.__axis = axis
        self.__image = image
        self.__last_image = last_image
        self.__empty_board = empty_board

        self.__diff_to_last = None
        self.__diff_to_empty = None

    def get_image(self):
        return self.__image

    def get_last_image(self):
        return self.__image

    def get_empty_image(self):
        return self.__image

    def get_diff_to_empty_image(self):
        if self.__diff_to_empty is None:
            self.__diff_to_empty = self.__get_image_diff(self.__empty_board, self.__image)
        return self.__diff_to_empty

    def get_diff_to_last_image(self):
        if self.__diff_to_last is None:
            self.__diff_to_last = self.__get_image_diff(self.__last_image, self.__image)
        else:
            print('Using Cache')
        return self.__diff_to_last

    def get_diff_count_to_empty_image(self):
        if self.__diff_to_empty is None:
            self.__diff_to_empty = self.__get_image_diff(self.__empty_board, self.__image)
        else:
            print('Using Cache')
        return np.count_nonzero(np.asarray(self.__diff_to_empty) == 1)

    def get_diff_count_to_last_image(self):
        if self.__diff_to_last is None:
            self.__diff_to_last = self.__get_image_diff(self.__last_image, self.__image)
        return np.count_nonzero(np.asarray(self.__diff_to_last) == 1)

    def contains_change(self):
        return self.get_diff_count_to_last_image() >= config['image_diff_threshold']

    def is_empty_board(self):
        return self.get_diff_count_to_empty_image() >= config['image_diff_threshold']

    @staticmethod
    def __get_image_diff(base_image, image):
        print('Calculating Image Diff')
        binary_diff_image = binary_diff_images(
            base_image,
            image,
            (0, base_image.shape[0]),
            config['pixel_diff_threshold']
        )
        enhanced_diff_img = binary_opening(binary_diff_image, structure=np.ones((5, 5))).astype(int)
        enhanced_diff_img_copy = enhanced_diff_img.copy()
        labeled_array, _ = label(enhanced_diff_img)
        obj_locations = find_objects(labeled_array)
        obj_indexes_to_be_removed = list(filter(
            lambda obj_i: filter_small_obj_at_the_ground(enhanced_diff_img[obj_locations[obj_i]], obj_locations[obj_i]),
            range(len(obj_locations))
        ))
        enhanced_diff_img = labeled_array
        for obj_h in obj_indexes_to_be_removed:
            enhanced_diff_img = np.where(enhanced_diff_img == obj_h + 1, 0, enhanced_diff_img)
        enhanced_diff_img = np.where(enhanced_diff_img != 0, 1, 0)
        # fig, axes = plt.subplots(2, 1)
        # axes[0].imshow(enhanced_diff_img_copy)
        # axes[1].imshow(enhanced_diff_img)
        # fig.show()
        # unique, counts = np.unique(enhanced_diff_img, return_counts=True)
        # print(dict(zip(unique, counts)))

        # if len(obj_indexes_to_be_removed) > 0:
        #     print('Comp')
        #     unique, counts = np.unique(enhanced_diff_img[obj_locations[obj_indexes_to_be_removed[0]]],
        #                                return_counts=True)
        #     print(dict(zip(unique, counts)))
        #     unique, counts = np.unique(enhanced_diff_img_copy[obj_locations[obj_indexes_to_be_removed[0]]],
        #                                return_counts=True)
        #     print(dict(zip(unique, counts)))
        #     print('>Comp')
        return enhanced_diff_img


class DartboardImages:
    def __init__(self, cur_x, cur_y, last_x, last_y, emtpy_x=None, empty_y=None):
        self.__x_image = DartboardImage('x', cur_x, last_x, emtpy_x)
        self.__y_image = DartboardImage('y', cur_y, last_y, empty_y)
