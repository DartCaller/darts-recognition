import numpy as np
import matplotlib.pyplot as plt
from vector import Vector
from scipy.ndimage import binary_closing
from scipy.ndimage.measurements import center_of_mass
from debug_tools import board_visualizer, show_zoomed_image_area
from helper_functions import calculate_dartboard_section_from_coords, isolate_dart_tip
from helper_functions.binary_diff_images import binary_diff_images


class DartBoard:
    def __init__(self, y_range, x_camera, y_camera, debug=False):
        self.focused_y_range = y_range
        self.bulls_eye_pxl_coord = Vector(0, 0)
        self.empty_board_images = (None, None)
        self.pxl_per_mm = (None, None)
        self.x_camera = x_camera  # Vector(0, 421) ##v4 has 395 camera distance
        self.y_camera = y_camera  # Vector(-422, 0)
        self.debug = debug

    def calibrate(self, empty_board, calibration_board, calib_dart_distance):
        self.empty_board_images = empty_board

        range_min_x = self.get_single_axis_dart_pxl_pos(calibration_board[0], 0)
        range_max_x = self.get_single_axis_dart_pxl_pos(calibration_board[0], 0, second_dart=True)
        range_min_y = self.get_single_axis_dart_pxl_pos(calibration_board[1], 1)
        range_max_y = self.get_single_axis_dart_pxl_pos(calibration_board[1], 1, second_dart=True)
        # range_min = self.get_dart_pxl_pos(calibrationBoard[0], calibrationBoard[1])
        # range_max = self.get_dart_pxl_pos(calibrationBoard[0], calibrationBoard[1], getSecondDart=True)

        print('RangeX', range_min_x, range_max_x)
        print('RangeY', range_min_y, range_max_y)
        self.bulls_eye_pxl_coord = Vector((range_min_x + range_max_x) / 2, (range_min_y + range_max_y) / 2)
        if self.debug:
            print('Found Bullseye at ( ', self.bulls_eye_pxl_coord.x, ', ', self.bulls_eye_pxl_coord.y, ')')

        fig, axes = plt.subplots(1, 2)
        axes[0].imshow(calibration_board[0])
        axes[0].axvline(self.bulls_eye_pxl_coord.x, linewidth=1, color='r')
        axes[1].imshow(calibration_board[1])
        axes[1].axvline(self.bulls_eye_pxl_coord.y, linewidth=1, color='r')

        # Account for the 1mm because the outer dart doesnt sit on the ring but inside
        dartboard_pixel_per_mm_x = abs(range_min_x - range_max_x) / calib_dart_distance  # 342 # 31
        dartboard_pixel_per_mm_y = abs(range_min_y - range_max_y) / calib_dart_distance
        self.pxl_per_mm = (dartboard_pixel_per_mm_x, dartboard_pixel_per_mm_y)

    def get_single_axis_dart_pxl_pos(self, dart_img, axis, second_dart=False):
        diff_img = binary_diff_images(self.empty_board_images[axis], dart_img, self.focused_y_range, 0.2)
        enhanced_diff_img = binary_closing(diff_img, structure=np.ones((5, 5))).astype(int)

        isolated_dart = isolate_dart_tip(enhanced_diff_img, second_dart)
        _, x_coordinate = center_of_mass(isolated_dart)

        if self.debug:
            show_zoomed_image_area(dart_img, x_coordinate, self.focused_y_range)
        return x_coordinate

    def get_dart_pxl_pos(self, dart_img_x_axis, dart_img_y_axis, get_second_dart=False):
        x_pxl_pos = self.get_single_axis_dart_pxl_pos(dart_img_x_axis, 0, get_second_dart)
        y_pxl_pos = self.get_single_axis_dart_pxl_pos(dart_img_y_axis, 1, get_second_dart)
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
        print('dartPlaneRelPxlPos: ', dart_plane_rel_pxl_pos.toList())
        dart_plane_rel_pos = Vector(
            dart_plane_rel_pxl_pos.x / self.pxl_per_mm[0],
            dart_plane_rel_pxl_pos.y / self.pxl_per_mm[1]
        )
        print('dartPlaneRelPos: ', dart_plane_rel_pos.to_list())
        dart_rel_pos = self.find_inter_section(dart_plane_rel_pos)
        print('Relative Dart Pos in MM: ', dart_rel_pos.to_list())

        board_visualizer.draw_point_on_dartboard(dart_rel_pos)
        return calculate_dartboard_section_from_coords(dart_rel_pos)
