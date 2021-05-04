from scipy.ndimage.measurements import label
from scipy.ndimage import find_objects
import numpy as np


def isolate_dart_tip(img, second_dart=False):
    labeled_array, _ = label(img)
    obj_locations = find_objects(labeled_array)
    obj_indexes_sorted_by_obj_size = sorted(
        range(len(obj_locations)),
        key=lambda obj_i:
        np.count_nonzero(img[obj_locations[obj_i]]), reverse=True
    )
    index_of_dart = obj_indexes_sorted_by_obj_size[0 if not second_dart else 1]
    dart_obj = obj_locations[index_of_dart]
    y_coord_maxima = dart_obj[0].stop
    isolated_dart = np.where(labeled_array == (index_of_dart + 1), 1, 0)
    # Remove everything from dart and leave only the bottom most X pxl
    isolated_dart[:y_coord_maxima - 20, :] = isolated_dart[y_coord_maxima + 1:, :] = 0
    return isolated_dart
