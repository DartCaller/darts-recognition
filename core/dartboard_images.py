import numpy as np
from config import config
from scipy.ndimage import find_objects, binary_opening, binary_closing
from scipy.ndimage.measurements import label
from helper_functions.binary_diff_images import binary_diff_images


def filter_small_obj_at_the_ground(obj, obj_pos):
    lower_bound = config['y_bounds_height'] - 100
    return np.count_nonzero(obj) < 10000 and obj_pos[1].start < 100 and obj_pos[1].stop < 100


class DartboardImage:
    def __init__(self, axis, img, last_img=None, empty_board=None):
        if last_img is None:
            last_img = img
        if empty_board is None:
            empty_board = last_img
        self.__axis = axis
        self.__img = img
        self.__last_img = last_img
        self.__empty_board = empty_board

        self.__diff_to_last = None
        self.__diff_to_empty = None

    def get_img(self):
        return self.__img

    def get_last_img(self):
        return self.__last_img

    def get_empty_img(self):
        return self.__empty_board

    def get_diff_to_empty_img(self):
        if self.__diff_to_empty is None:
            self.__diff_to_empty = self.__get_img_diff(self.__empty_board, self.__img)
        return self.__diff_to_empty

    def get_diff_to_last_img(self):
        if self.__diff_to_last is None:
            self.__diff_to_last = self.__get_img_diff(self.__last_img, self.__img)
        return self.__diff_to_last

    def get_diff_count_to_empty_img(self):
        if self.__diff_to_empty is None:
            self.__diff_to_empty = self.__get_img_diff(self.__empty_board, self.__img)
        return np.count_nonzero(np.asarray(self.__diff_to_empty) == 1)

    def get_diff_count_to_last_img(self):
        if self.__diff_to_last is None:
            self.__diff_to_last = self.__get_img_diff(self.__last_img, self.__img)
        return np.count_nonzero(np.asarray(self.__diff_to_last) == 1)

    def contains_change(self):
        diff_count_to_last = self.get_diff_count_to_last_img()
        lower_diff_threshold = config['image_diff_threshold']
        upper_diff_threshold = config['max_image_diff_threshold']
        return lower_diff_threshold <= diff_count_to_last <= upper_diff_threshold

    def is_empty_board(self):
        return self.get_diff_count_to_empty_img() <= config['image_diff_threshold']

    @staticmethod
    def __get_img_diff(base_img, img):
        binary_diff_img = binary_diff_images(
            base_img, img, None, config['pixel_diff_threshold']
        )

        enhanced_diff_img = binary_opening(binary_diff_img, structure=np.ones((5, 5))).astype(int)
        # enhanced_diff_img_copy = enhanced_diff_img.copy()
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
    def __init__(self, cur_x, cur_y, last_x=None, last_y=None, emtpy_x=None, empty_y=None):
        self.x = DartboardImage('x', cur_x, last_x, emtpy_x)
        self.y = DartboardImage('y', cur_y, last_y, empty_y)

    def list(self):
        return [self.x, self.y]

    def are_last_imgs_empty(self):
        return self.__map_to_list(self.list(), 'is_empty_board')

    def do_last_imgs_contain_change(self):
        return self.__map_to_list(self.list(), 'contains_change')

    @staticmethod
    def __map_to_list(array, method):
        return list(map(lambda item: getattr(item, method)(), array))
