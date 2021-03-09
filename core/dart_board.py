import numpy as np
import matplotlib.pyplot as plt
from vector import Vector
from scipy.ndimage import binary_closing
from scipy.ndimage.measurements import center_of_mass
from debug_tools import board_visualizer, show_zoomed_image_area
from helper_functions import calculate_dartboard_section_from_coords, isolate_dart_tip, time_function_execution
from helper_functions.binary_diff_images import binary_diff_images
from config import config


class DartBoard:
    def __init__(self, x_camera, y_camera, debug=False):
        self.bulls_eye_pxl_coord = Vector(0, 0)
        self.pxl_per_mm = (None, None)
        self.x_camera = x_camera  # Vector(0, 421) ##v4 has 395 camera distance
        self.y_camera = y_camera  # Vector(-422, 0)
        self.debug = debug

    def calibrate(self, empty_board, calib_board, calib_dart_distance):
        # range_min_x = self.get_single_axis_dart_pxl_pos(empty_board[0], calib_board[0])
        # range_max_x = self.get_single_axis_dart_pxl_pos(empty_board[0], calib_board[0], second_dart=True)
        # range_min_y = self.get_single_axis_dart_pxl_pos(empty_board[1], calib_board[1])
        # range_max_y = self.get_single_axis_dart_pxl_pos(empty_board[1], calib_board[1], second_dart=True)
        x_axis_img = (empty_board[0], calib_board[0])
        y_axis_img = (empty_board[1], calib_board[1])
        range_min = self.get_dart_pxl_pos(x_axis_img, y_axis_img)
        range_max = self.get_dart_pxl_pos(x_axis_img, y_axis_img, get_second_dart=True)

        print('RangeX', range_min.x, range_max.x)
        print('RangeY', range_min.y, range_max.y)
        self.bulls_eye_pxl_coord = Vector((range_min.x + range_max.x) / 2, (range_min.y + range_max.y) / 2)
        if self.debug:
            print('Found Bullseye at ( ', self.bulls_eye_pxl_coord.x, ', ', self.bulls_eye_pxl_coord.y, ')')

        fig, axes = plt.subplots(1, 2)
        axes[0].imshow(calib_board[0])
        axes[0].axvline(self.bulls_eye_pxl_coord.x, linewidth=1, color='r')
        axes[1].imshow(calib_board[1])
        axes[1].axvline(self.bulls_eye_pxl_coord.y, linewidth=1, color='r')

        # Account for the 1mm because the outer dart doesnt sit on the ring but inside
        dartboard_pixel_per_mm_x = abs(range_min.x - range_max.x) / calib_dart_distance  # 342 # 31
        dartboard_pixel_per_mm_y = abs(range_min.y - range_max.y) / calib_dart_distance
        self.pxl_per_mm = (dartboard_pixel_per_mm_x, dartboard_pixel_per_mm_y)

    @staticmethod
    def get_single_axis_dart_pxl_pos(dart_imgs, second_dart=False):
        diff_img = binary_diff_images(dart_imgs[0], dart_imgs[1], config['y_bounds'], config['pixel_diff_threshold'])
        enhanced_diff_img = binary_closing(diff_img, structure=np.ones((5, 5))).astype(int)

        isolated_dart = isolate_dart_tip(enhanced_diff_img, second_dart)
        _, x_coordinate = center_of_mass(isolated_dart)

        # if self.debug:
        #     show_zoomed_image_area(dart_img, x_coordinate, config['y_bounds'])
        return x_coordinate

    def get_dart_pxl_pos(self, x_axis_images, y_axis_images, get_second_dart=False):
        x_pxl_pos = self.get_single_axis_dart_pxl_pos(x_axis_images, get_second_dart)
        y_pxl_pos = self.get_single_axis_dart_pxl_pos(y_axis_images, get_second_dart)
        return Vector(x_pxl_pos, y_pxl_pos)

    def find_inter_section(self, dart_plane_rel_pos):
        gx_y_diff = -self.x_camera.y if dart_plane_rel_pos.x >= self.x_camera.x else self.x_camera.y
        gx = (gx_y_diff / abs(dart_plane_rel_pos.x), self.x_camera.y)
        gy_x_diff = -dart_plane_rel_pos.y if self.y_camera.x >= 0 else dart_plane_rel_pos.y
        gy = (gy_x_diff / abs(self.y_camera.x), dart_plane_rel_pos.y)
        if self.debug:
            print('Line from X Coordinate: gX(x)=', gx[0], 'x +', gx[1])
            print('Line from Y Coordinate: gY(x)=', gy[0], 'x +', gy[1])

        intersect_x = (gx[1] - gy[1]) / (gy[0] - gx[0])
        intersect_y = gx[0] * intersect_x + gx[1]
        if self.debug:
            print('Dart Pos at ( ', intersect_x, ', ', intersect_y, ' )')
        return Vector(intersect_x, intersect_y)

    def get_dart_score(self, dart_img_x_axis, dart_img_y_axis):
        dart_plane_abs_pxl_pos = self.get_dart_pxl_pos(dart_img_x_axis, dart_img_y_axis)
        print('dartPlaneAbsPxlPos: ', dart_plane_abs_pxl_pos.to_list())
        # Other way round minus if camera on other side
        dart_plane_rel_pxl_pos = self.bulls_eye_pxl_coord.minus(dart_plane_abs_pxl_pos)
        print('dartPlaneRelPxlPos: ', dart_plane_rel_pxl_pos.to_list())
        dart_plane_rel_pos = Vector(
            dart_plane_rel_pxl_pos.x / self.pxl_per_mm[0],
            dart_plane_rel_pxl_pos.y / self.pxl_per_mm[1]
        )
        print('dartPlaneRelPos: ', dart_plane_rel_pos.to_list())
        dart_rel_pos = self.find_inter_section(dart_plane_rel_pos)
        print('Relative Dart Pos in MM: ', dart_rel_pos.to_list())

        board_visualizer.draw_point_on_dartboard(dart_rel_pos)
        return calculate_dartboard_section_from_coords(dart_rel_pos)
